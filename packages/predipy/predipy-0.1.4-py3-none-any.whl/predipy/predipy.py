import numpy as np

# ===================== Utils =====================
def mse(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

def akurasi(y_true, y_pred):
    return np.mean(y_true == y_pred)

# ===================== Regresi Linier =====================
class RegresiLinier:
    def __init__(self, lr=0.01, epochs=1000):
        self.lr = lr
        self.epochs = epochs
        self.w = None
        self.b = None

    def fit(self, X, y):
        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float).reshape(-1, 1)
        n_samples, n_features = X.shape
        self.w = np.zeros((n_features, 1))
        self.b = 0

        for _ in range(self.epochs):
            y_pred = np.dot(X, self.w) + self.b
            dw = (1/n_samples) * np.dot(X.T, (y_pred - y))
            db = (1/n_samples) * np.sum(y_pred - y)
            self.w -= self.lr * dw
            self.b -= self.lr * db

    def prediksi(self, X):
        X = np.array(X, dtype=float)
        return np.dot(X, self.w) + self.b

# ===================== Regresi Logistik =====================
class RegresiLogistik:
    def __init__(self, lr=0.01, epochs=1000):
        self.lr = lr
        self.epochs = epochs
        self.w = None
        self.b = None

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float).reshape(-1,1)
        n_samples, n_features = X.shape
        self.w = np.zeros((n_features,1))
        self.b = 0

        for _ in range(self.epochs):
            linear_model = np.dot(X, self.w) + self.b
            y_pred = self.sigmoid(linear_model)
            dw = (1/n_samples) * np.dot(X.T, (y_pred - y))
            db = (1/n_samples) * np.sum(y_pred - y)
            self.w -= self.lr * dw
            self.b -= self.lr * db

    def prediksi_prob(self, X):
        X = np.array(X, dtype=float)
        return self.sigmoid(np.dot(X, self.w) + self.b)

    def prediksi(self, X, threshold=0.5):
        return (self.prediksi_prob(X) >= threshold).astype(int)

# ===================== MLP Mini =====================
class MLP:
    def __init__(self, ukuran_input, ukuran_tersembunyi, ukuran_output, lr=0.01, epoch=1000, batch_size=None):
        self.input_size = ukuran_input
        self.hidden_size = ukuran_tersembunyi
        self.output_size = ukuran_output
        self.lr = lr
        self.epochs = epoch
        self.batch_size = batch_size

        self.W1 = np.random.randn(self.input_size, self.hidden_size) * 0.01
        self.b1 = np.zeros((1, self.hidden_size))
        self.W2 = np.random.randn(self.hidden_size, self.output_size) * 0.01
        self.b2 = np.zeros((1, self.output_size))

    def relu(self, z):
        return np.maximum(0, z)

    def relu_deriv(self, z):
        return (z > 0).astype(float)

    def forward(self, X):
        self.Z1 = np.dot(X, self.W1) + self.b1
        self.A1 = self.relu(self.Z1)
        self.Z2 = np.dot(self.A1, self.W2) + self.b2
        self.A2 = self.Z2
        return self.A2

    def backward(self, X, y, y_pred):
        m = X.shape[0]
        dZ2 = (y_pred - y) / m
        dW2 = np.dot(self.A1.T, dZ2)
        db2 = np.sum(dZ2, axis=0, keepdims=True)
        dA1 = np.dot(dZ2, self.W2.T)
        dZ1 = dA1 * self.relu_deriv(self.Z1)
        dW1 = np.dot(X.T, dZ1)
        db1 = np.sum(dZ1, axis=0, keepdims=True)

        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2

    def fit(self, X, y):
        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float)
        if y.ndim == 1:
            y = y.reshape(-1,1)

        n_samples = X.shape[0]
        batch_size = self.batch_size or n_samples

        for _ in range(self.epochs):
            for start in range(0, n_samples, batch_size):
                end = start + batch_size
                X_batch = X[start:end]
                y_batch = y[start:end]
                y_pred = self.forward(X_batch)
                self.backward(X_batch, y_batch, y_pred)

    def prediksi(self, X):
        X = np.array(X, dtype=float)
        return self.forward(X)

