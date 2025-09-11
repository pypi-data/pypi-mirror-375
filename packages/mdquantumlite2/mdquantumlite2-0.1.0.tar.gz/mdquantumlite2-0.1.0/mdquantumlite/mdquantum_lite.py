import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from scipy.sparse import csr_matrix
from lightgbm import LGBMRegressor

from .quantum_feature import QuantumFeature  # ایمپورت از فایل جداگانه

class MDQuantumLite:
    def __init__(self,
                 n_estimators=100,
                 learning_rate=0.05,
                 max_depth=5,
                 min_samples_leaf=5,
                 top_rate=0.3,
                 other_rate=0.2,
                 subsample=0.6,
                 categorical_features=None,
                 use_sparse=False,
                 early_stopping_rounds=5,
                 validation_fraction=0.1,
                 use_quantum_features=False,
                 random_state=42,
                 verbose=20):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.top_rate = top_rate
        self.other_rate = other_rate
        self.subsample = subsample
        self.categorical_features = categorical_features or []
        self.use_sparse = use_sparse
        self.early_stopping_rounds = early_stopping_rounds
        self.validation_fraction = validation_fraction
        self.use_quantum_features = use_quantum_features
        self.random_state = random_state
        self.verbose = verbose

        self.models = []
        self.base_prediction = None
        self.label_encoders = {}
        self.target_encoders = {}
        self.global_mean = None
        self.num_imputer = None
        self.cat_imputer = None
        if self.use_quantum_features:
            self.quantum = QuantumFeature(n_qubits=2, n_layers=1)
        else:
            self.quantum = None

    # ---------------------- Target Encoding سریع با KFold=2 ----------------------
    def _target_encode(self, X_col, y, smoothing=10):
        global_mean = np.mean(y)
        self.global_mean = global_mean
        df = pd.DataFrame({'val': X_col, 'target': y})
        mean_map = df.groupby('val')['target'].mean().to_dict()
        encoded = np.array([mean_map.get(v, global_mean) for v in X_col], dtype=np.float32)
        return encoded, mean_map

    # ---------------------- Encode Features ----------------------
    def _encode_features(self, X, y=None, training=True):
        X = np.array(X, dtype=object)
        X_enc = np.zeros(X.shape, dtype=np.float32)
        for col in range(X.shape[1]):
            if col in self.categorical_features:
                if training:
                    le = LabelEncoder()
                    le.fit(X[:, col])
                    self.label_encoders[col] = le
                    encoded_col, mean_map = self._target_encode(X[:, col], y)
                    self.target_encoders[col] = mean_map
                    X_enc[:, col] = encoded_col
                else:
                    mean_map = self.target_encoders.get(col, {})
                    global_mean = self.global_mean if hasattr(self, "global_mean") else 0.0
                    X_enc[:, col] = np.array([mean_map.get(v, global_mean) for v in X[:, col]], dtype=np.float32)
            else:
                X_enc[:, col] = pd.to_numeric(X[:, col], errors='coerce').astype(np.float32)
        if self.use_quantum_features and self.quantum:
            X_enc = self.quantum.transform(X_enc)
        if self.use_sparse:
            X_enc = csr_matrix(X_enc)
        return X_enc

    # ---------------------- GOSS Sampling ----------------------
    def _goss_sample(self, residuals):
        n = len(residuals)
        top_n = int(self.top_rate * n)
        other_n = int(self.other_rate * n)
        sorted_idx = np.argsort(np.abs(residuals))[::-1]
        top_idx = sorted_idx[:top_n]
        other_idx = np.random.choice(sorted_idx[top_n:], other_n, replace=False)
        weights = np.ones(top_n + other_n)
        weights[top_n:] = (1.0 - self.top_rate) / self.other_rate
        return np.concatenate([top_idx, other_idx]), weights

    # ---------------------- Fit ----------------------
    def fit(self, X, y):
        X = np.array(X, dtype=object)
        # Impute عددی
        num_cols = [i for i in range(X.shape[1]) if i not in self.categorical_features]
        if num_cols:
            self.num_imputer = SimpleImputer(strategy='mean')
            X[:, num_cols] = self.num_imputer.fit_transform(X[:, num_cols])
        # Impute دسته‌ای
        self.cat_imputer = SimpleImputer(strategy='constant', fill_value='missing')
        X[:, self.categorical_features] = self.cat_imputer.fit_transform(X[:, self.categorical_features])

        if self.validation_fraction > 0:
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=self.validation_fraction, random_state=self.random_state
            )
        else:
            X_train, y_train = X, y
            X_val, y_val = None, None

        X_train_enc = self._encode_features(X_train, y_train, training=True)
        self.base_prediction = np.mean(y_train)
        preds_train = np.full_like(y_train, self.base_prediction, dtype=np.float32)
        if X_val is not None:
            X_val_enc = self._encode_features(X_val, training=False)
            preds_val = np.full_like(y_val, self.base_prediction, dtype=np.float32)

        self.models = []
        best_val_mse = float("inf")
        rounds_no_improve = 0

        for i in range(self.n_estimators):
            residuals = y_train - preds_train
            sample_idx, weights = self._goss_sample(residuals)
            X_sub = X_train_enc[sample_idx]
            residuals_sub = residuals[sample_idx]

            tree = LGBMRegressor(max_depth=self.max_depth,
                                 min_child_samples=self.min_samples_leaf,
                                 num_leaves=31,
                                 random_state=self.random_state,
                                 verbose=-1)
            tree.fit(X_sub, residuals_sub, sample_weight=weights)
            self.models.append(tree)
            preds_train += self.learning_rate * tree.predict(X_train_enc)
            if X_val is not None:
                preds_val += self.learning_rate * tree.predict(X_val_enc)
                val_mse = mean_squared_error(y_val, preds_val)
                if val_mse < best_val_mse:
                    best_val_mse = val_mse
                    rounds_no_improve = 0
                else:
                    rounds_no_improve += 1
                    if rounds_no_improve >= self.early_stopping_rounds:
                        if self.verbose:
                            print(f"توقف زودهنگام در تکرار {i+1}, MSE: {best_val_mse:.4f}")
                        break
            if self.verbose and (i+1) % self.verbose == 0:
                print(f"تکرار {i+1}, MSE: {mean_squared_error(y_val, preds_val):.4f}" if X_val is not None else f"تکرار {i+1}")

    # ---------------------- Predict ----------------------
    def predict(self, X):
        X = np.array(X, dtype=object)
        num_cols = [i for i in range(X.shape[1]) if i not in self.categorical_features]
        if num_cols and self.num_imputer:
            X[:, num_cols] = self.num_imputer.transform(X[:, num_cols])
        if self.cat_imputer:
            X[:, self.categorical_features] = self.cat_imputer.transform(X[:, self.categorical_features])
        X_enc = self._encode_features(X, training=False)
        preds = np.full(X_enc.shape[0], self.base_prediction, dtype=np.float32)
        for tree in self.models:
            preds += self.learning_rate * tree.predict(X_enc)
        return preds