import time
import numpy as np
from sklearn.datasets import make_regression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor

from mdquantumlite import MDQuantumLite  # ایمپورت از پکیج

def test_mdquantum_lite():
    X, y = make_regression(n_samples=10000, n_features=20, noise=0.1, random_state=42)
    cats = np.random.choice(['A','B','C','D'], size=X.shape[0])
    X = np.array(X, dtype=object)
    X[:,0] = cats

    # MDQuantumLite
    md = MDQuantumLite(n_estimators=100,
                       learning_rate=0.05,
                       max_depth=5,
                       categorical_features=[0],
                       use_sparse=False,
                       early_stopping_rounds=5,
                       verbose=20)
    start = time.time()
    md.fit(X, y)
    y_pred_md = md.predict(X)
    mse_md = mean_squared_error(y, y_pred_md)
    time_md = time.time() - start
    print(f"MDQuantumLite - MSE: {mse_md:.4f}, زمان: {time_md:.4f} ثانیه")

    # XGBoost
    le = LabelEncoder()
    X_xgb = X.copy()
    X_xgb[:,0] = le.fit_transform(X_xgb[:,0])
    X_xgb = X_xgb.astype(np.float32)
    xgb = XGBRegressor(n_estimators=100,
                       learning_rate=0.05,
                       max_depth=5,
                       subsample=0.6,
                       random_state=42)
    start = time.time()
    xgb.fit(X_xgb, y)
    y_pred_xgb = xgb.predict(X_xgb)
    mse_xgb = mean_squared_error(y, y_pred_xgb)
    time_xgb = time.time() - start
    print(f"XGBoost - MSE: {mse_xgb:.4f}, زمان: {time_xgb:.4f} ثانیه")

if __name__ == "__main__":
    test_mdquantum_lite()