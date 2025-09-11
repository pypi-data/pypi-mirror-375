import numpy as np

# ===================== Quantum Feature Generator (اختیاری) =====================
try:
    import pennylane as qml
    from pennylane.optimize import SPSAOptimizer
    QML_AVAILABLE = True
except ImportError:
    QML_AVAILABLE = False

class QuantumFeature:
    def __init__(self, n_qubits=2, n_layers=1):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        if QML_AVAILABLE:
            self.dev = qml.device("default.qubit", wires=self.n_qubits)
        else:
            self.dev = None

    def _quantum_circuit(self, inputs, weights):
        for i in range(min(len(inputs), self.n_qubits)):
            qml.RX(inputs[i], wires=i)
        for layer in range(self.n_layers):
            for i in range(self.n_qubits - 1):
                qml.CNOT(wires=[i, i+1])
            for i in range(self.n_qubits):
                qml.RX(weights[layer, i], wires=i)
        return [qml.expval(qml.PauliZ(i)) for i in range(self.n_qubits)]

    def fit_transform(self, X, y=None):  # y رو اضافه کردم اما استفاده نمی‌شه (برای سازگاری)
        if self.dev is None:  # QML نصب نشده
            return X
        X = np.array(X, dtype=np.float32)
        self.weights = np.random.uniform(0, np.pi, (self.n_layers, self.n_qubits))
        # بهینه سازی ساده (کم هزینه)
        qnode = qml.QNode(self._quantum_circuit, self.dev, interface="numpy")
        X_quantum = np.zeros((X.shape[0], self.n_qubits))
        for i in range(X.shape[0]):
            X_norm = np.pi * (X[i] - X.min(axis=0)) / (X.ptp(axis=0) + 1e-8)
            X_quantum[i] = qnode(X_norm[:self.n_qubits], self.weights)
        return X_quantum.astype(np.float32)

    def transform(self, X):
        return self.fit_transform(X)