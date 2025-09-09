import numpy as np
import unittest

# Fungsi untuk menghasilkan dataset sintetis
def generate_mixed_data(n_samples=1000, noise=0.001):
    X = np.linspace(-2, 2, n_samples).reshape(-1, 1)
    Y = 2 * X + np.sin(X) + np.random.randn(n_samples, 1) * noise
    return Tensor(X, requires_grad=False), Tensor(Y, requires_grad=False)

def generate_classification_data(n_samples=1000, noise=0.05):
    X = np.random.randn(n_samples, 2) * 2
    Y = (X[:, 0] + X[:, 1] > 0).astype(float).reshape(-1, 1)
    Y = np.eye(2)[Y.astype(int).reshape(-1)]  # One-hot encoding
    return Tensor(X, requires_grad=False), Tensor(Y, requires_grad=False)

def generate_quadratic_data(n_samples=1000, noise=0.001):
    X = np.linspace(-2, 2, n_samples).reshape(-1, 1)
    Y = X ** 2 + np.random.randn(n_samples, 1) * noise
    return Tensor(X, requires_grad=False), Tensor(Y, requires_grad=False)

def generate_nonlinear_data(n_samples=1000, noise=0.001):
    X = np.linspace(-2, 2, n_samples).reshape(-1, 1)
    Y = np.sin(2 * np.pi * X) + np.random.randn(n_samples, 1) * noise
    return Tensor(X, requires_grad=False), Tensor(Y, requires_grad=False)

# Kelas Tensor
class Tensor:
    def __init__(self, data, requires_grad=False, prev=()):
        self.data = np.array(data, dtype=float)
        self.grad = np.zeros_like(self.data) if requires_grad else None
        self.requires_grad = requires_grad
        self.prev = set(prev)
        self._backward = lambda: None

    def __getitem__(self, key):
        return Tensor(self.data[key], requires_grad=self.requires_grad, prev=(self,))

    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        if other.data.ndim == 0:  # Skalar
            out_data = self.data + other.data
        else:
            if self.data.shape != other.data.shape:
                raise ValueError(f"Shape mismatch: {self.data.shape} vs {other.data.shape}")
            out_data = self.data + other.data
        out = Tensor(out_data, self.requires_grad or other.requires_grad, (self, other))

        def _backward():
            if self.requires_grad and out.grad is not None:
                self.grad += out.grad
            if other.requires_grad and out.grad is not None:
                if other.data.ndim == 0:  # Skalar
                    other.grad += np.sum(out.grad)
                else:
                    other.grad += out.grad
        out._backward = _backward
        return out

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        if other.data.ndim == 0:  # Skalar
            out_data = self.data * other.data
        else:
            if self.data.shape != other.data.shape:
                raise ValueError(f"Shape mismatch: {self.data.shape} vs {other.data.shape}")
            out_data = self.data * other.data
        out = Tensor(out_data, self.requires_grad or other.requires_grad, (self, other))

        def _backward():
            if self.requires_grad and out.grad is not None:
                if other.data.ndim == 0:  # Skalar
                    self.grad += other.data * out.grad
                else:
                    self.grad += other.data * out.grad
            if other.requires_grad and out.grad is not None:
                if other.data.ndim == 0:  # Skalar
                    other.grad += np.sum(self.data * out.grad)
                else:
                    other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def __rmul__(self, other):
        return self.__mul__(other)

    def backward(self, gradient=None):
        if not self.requires_grad:
            return
        if gradient is None:
            gradient = np.ones_like(self.data)
        if self.grad is None:
            self.grad = np.zeros_like(self.data)
        self.grad += gradient

        topo = []
        visited = set()
        def build_topo(v):
            if v not in visited and v.requires_grad:
                visited.add(v)
                for prev in v.prev:
                    build_topo(prev)
                topo.append(v)
        build_topo(self)

        for node in reversed(topo):
            node._backward()

# Kelas Linear
class Linear:
    def __init__(self, in_features, out_features, init_method='he'):
        if init_method == 'xavier':
            scale = np.sqrt(2.0 / (in_features + out_features))
        elif init_method == 'he':
            scale = np.sqrt(2.0 / in_features)
        else:
            scale = 0.01
        self.W = Tensor(np.random.randn(in_features, out_features) * scale, requires_grad=True)
        self.b = Tensor(np.zeros(out_features), requires_grad=True)

    def __call__(self, x):
        out = Tensor(np.dot(x.data, self.W.data) + self.b.data,
                     x.requires_grad or self.W.requires_grad or self.b.requires_grad, (x, self.W, self.b))

        def _backward():
            if x.requires_grad and out.grad is not None:
                x.grad += np.dot(out.grad, self.W.data.T)
            if self.W.requires_grad and out.grad is not None:
                x_reshaped = x.data.reshape(-1, x.data.shape[-1]) if x.data.ndim > 2 else x.data
                self.W.grad += np.dot(x_reshaped.T, out.grad)
            if self.b.requires_grad and out.grad is not None:
                self.b.grad += np.sum(out.grad, axis=0)
        out._backward = _backward
        return out

    def parameters(self):
        return [self.W, self.b]

# Kelas Aktivasi
class LeakyReLU:
    def __init__(self, negative_slope=0.01):
        self.negative_slope = negative_slope

    def __call__(self, x):
        out_data = np.where(x.data >= 0, x.data, x.data * self.negative_slope)
        out = Tensor(out_data, requires_grad=x.requires_grad, prev=(x,))

        def _backward():
            grad = np.where(x.data >= 0, 1.0, self.negative_slope)
            if x.requires_grad and out.grad is not None:
                x.grad += grad * out.grad
        out._backward = _backward
        return out

class ReLU:
    def __call__(self, x):
        out_data = np.maximum(0, x.data)
        out = Tensor(out_data, requires_grad=x.requires_grad, prev=(x,))

        def _backward():
            grad = np.where(x.data > 0, 1.0, 0.0)
            if x.requires_grad and out.grad is not None:
                x.grad += grad * out.grad
        out._backward = _backward
        return out

class Sigmoid:
    def __call__(self, x):
        x_data = np.clip(x.data, -500, 500)
        out_data = 1 / (1 + np.exp(-x_data))
        out = Tensor(out_data, requires_grad=x.requires_grad, prev=(x,))

        def _backward():
            s = out.data
            grad = s * (1 - s)
            if x.requires_grad and out.grad is not None:
                x.grad += grad * out.grad
        out._backward = _backward
        return out

class Tanh:
    def __call__(self, x):
        out_data = np.tanh(x.data)
        out = Tensor(out_data, requires_grad=x.requires_grad, prev=(x,))

        def _backward():
            grad = 1 - out.data ** 2
            if x.requires_grad and out.grad is not None:
                x.grad += grad * out.grad
        out._backward = _backward
        return out

class Softmax:
    def __call__(self, x):
        exp_x = np.exp(x.data - np.max(x.data, axis=-1, keepdims=True))
        out_data = exp_x / np.sum(exp_x, axis=-1, keepdims=True)
        out = Tensor(out_data, requires_grad=x.requires_grad, prev=(x,))

        def _backward():
            if x.requires_grad and out.grad is not None:
                batch_size = out.data.shape[0]
                grad = np.zeros_like(out.data)
                for i in range(batch_size):
                    s = out.data[i]
                    jacobian = np.diag(s) - np.outer(s, s)
                    grad[i] = np.dot(out.grad[i], jacobian)
                x.grad += grad
        out._backward = _backward
        return out

# Dropout
class Dropout:
    def __init__(self, p=0.5):
        self.p = p
        self.mask = None
        self.training = True

    def __call__(self, x):
        if self.training:
            self.mask = np.random.binomial(1, 1 - self.p, size=x.data.shape) / (1 - self.p)
            out_data = x.data * self.mask
        else:
            out_data = x.data
        out = Tensor(out_data, requires_grad=x.requires_grad, prev=(x,))

        def _backward():
            if x.requires_grad and self.training and out.grad is not None:
                x.grad += out.grad * self.mask
        out._backward = _backward
        return out

    def eval(self):
        self.training = False

    def train(self):
        self.training = True

# BatchNorm1D
class BatchNorm1D:
    def __init__(self, num_features, eps=1e-5, momentum=0.1):
        self.eps = eps
        self.momentum = momentum
        self.gamma = Tensor(np.ones(num_features), requires_grad=True)
        self.beta = Tensor(np.zeros(num_features), requires_grad=True)
        self.running_mean = np.zeros(num_features)
        self.running_var = np.ones(num_features)
        self.training = True
        self._x_mean = None
        self._x_var = None
        self._x_normalized = None

    def __call__(self, x):
        if self.training:
            mean = np.mean(x.data, axis=0)
            var = np.var(x.data, axis=0)
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mean
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var
            x_normalized = (x.data - mean) / np.sqrt(var + self.eps)
        else:
            x_normalized = (x.data - self.running_mean) / np.sqrt(self.running_var + self.eps)
        out_data = self.gamma.data * x_normalized + self.beta.data
        out = Tensor(out_data, requires_grad=x.requires_grad or self.gamma.requires_grad or self.beta.requires_grad,
                     prev=(x, self.gamma, self.beta))
        self._x_mean = mean if self.training else self.running_mean
        self._x_var = var if self.training else self.running_var
        self._x_normalized = x_normalized

        def _backward():
            if out.grad is None:
                return
            N = x.data.shape[0]
            if self.training:
                x_mu = x.data - self._x_mean
                std_inv = 1.0 / np.sqrt(self._x_var + self.eps)
                dx_norm = out.grad * self.gamma.data
                dvar = np.sum(dx_norm * x_mu, axis=0) * -0.5 * std_inv**3
                dmu = np.sum(dx_norm * -std_inv, axis=0) + dvar * np.mean(-2.0 * x_mu, axis=0)
                if x.requires_grad:
                    x.grad += (dx_norm * std_inv) + (dvar * 2 * x_mu / N) + (dmu / N)
                if self.gamma.requires_grad:
                    self.gamma.grad += np.sum(out.grad * self._x_normalized, axis=0)
                if self.beta.requires_grad:
                    self.beta.grad += np.sum(out.grad, axis=0)
            else:
                if x.requires_grad:
                    x.grad += out.grad * self.gamma.data / np.sqrt(self.running_var + self.eps)
                if self.gamma.requires_grad:
                    self.gamma.grad += np.sum(out.grad * self._x_normalized, axis=0)
                if self.beta.requires_grad:
                    self.beta.grad += np.sum(out.grad, axis=0)
        out._backward = _backward
        return out

    def eval(self):
        self.training = False

    def train(self):
        self.training = True

# Sequential
class Sequential:
    def __init__(self, *layers):
        self.layers = layers

    def __call__(self, x):
        out = x
        for layer in self.layers:
            out = layer(out)
        return out

    def parameters(self):
        params = []
        for layer in self.layers:
            if hasattr(layer, 'W'):
                params.append(layer.W)
                params.append(layer.b)
            if hasattr(layer, 'gamma'):
                params.append(layer.gamma)
                params.append(layer.beta)
        return params

    def eval(self):
        for layer in self.layers:
            if hasattr(layer, 'eval'):
                layer.eval()

    def train(self):
        for layer in self.layers:
            if hasattr(layer, 'train'):
                layer.train()

# Fungsi Loss
def mse(pred, target, model=None, reduction='mean'):
    diff = pred.data - target.data
    if reduction == 'mean':
        loss_data = np.mean(diff ** 2)
    elif reduction == 'sum':
        loss_data = np.sum(diff ** 2)
    else:
        loss_data = diff ** 2
    loss = Tensor(loss_data, requires_grad=True, prev=(pred, target))

    def _backward():
        if reduction == 'mean':
            grad = 2 * (pred.data - target.data) / pred.data.size
        elif reduction == 'sum':
            grad = 2 * (pred.data - target.data)
        else:
            grad = 2 * (pred.data - target.data)
        if pred.requires_grad and pred.grad is not None:
            pred.grad += grad
        if target.requires_grad and target.grad is not None:
            target.grad -= grad
    loss._backward = _backward
    return loss

def bce(pred, target, model=None, reduction='mean'):
    pred_data = np.clip(pred.data, 1e-15, 1 - 1e-15)
    if reduction == 'mean':
        loss_data = -np.mean(target.data * np.log(pred_data) + (1 - target.data) * np.log(1 - pred_data))
    elif reduction == 'sum':
        loss_data = -np.sum(target.data * np.log(pred_data) + (1 - target.data) * np.log(1 - pred_data))
    else:
        loss_data = -(target.data * np.log(pred_data) + (1 - target.data) * np.log(1 - pred_data))
    loss = Tensor(loss_data, requires_grad=True, prev=(pred, target))

    def _backward():
        if reduction == 'mean':
            grad = (pred_data - target.data) / (pred_data * (1 - pred_data) * pred.data.size)
        elif reduction == 'sum':
            grad = (pred_data - target.data) / (pred_data * (1 - pred_data))
        else:
            grad = (pred_data - target.data) / (pred_data * (1 - pred_data))
        if pred.requires_grad and pred.grad is not None:
            pred.grad += grad
        if target.requires_grad and target.grad is not None:
            target.grad -= grad
    loss._backward = _backward
    return loss

def cross_entropy(pred, target, model=None, reduction='mean'):
    pred_data = np.clip(pred.data, 1e-15, 1 - 1e-15)
    if pred_data.ndim == 1:
        pred_data = pred_data.reshape(-1, 1)
    if target.data.ndim == 1:
        target_data = target.data.reshape(-1, 1)
    else:
        target_data = target.data

    loss_data = -np.sum(target_data * np.log(pred_data), axis=-1)

    if reduction == 'mean':
        loss_data = np.mean(loss_data)
    elif reduction == 'sum':
        loss_data = np.sum(loss_data)

    loss = Tensor(loss_data, requires_grad=True, prev=(pred, target))

    def _backward():
        if pred.requires_grad:
            grad = (pred_data - target_data) / pred_data.shape[0] if reduction == 'mean' else (pred_data - target_data)
            pred.grad += grad
    loss._backward = _backward
    return loss

# Optimizer Adam dengan Scheduler
class Adam:
    def __init__(self, parameters, lr=0.00001, beta1=0.9, beta2=0.999, eps=1e-8, weight_decay=0.01):
        self.parameters = parameters
        self.lr = lr
        self.base_lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.weight_decay = weight_decay
        self.m = [np.zeros_like(p.data) for p in parameters]
        self.v = [np.zeros_like(p.data) for p in parameters]
        self.t = 0

    def step(self):
        self.t += 1
        for param, m, v in zip(self.parameters, self.m, self.v):
            if param.grad is not None:
                m[:] = self.beta1 * m + (1 - self.beta1) * param.grad
                v[:] = self.beta2 * v + (1 - self.beta2) * (param.grad ** 2)
                m_hat = m / (1 - self.beta1 ** self.t)
                v_hat = v / (1 - self.beta2 ** self.t)
                param.data -= self.lr * (m_hat / (np.sqrt(v_hat) + self.eps) + self.weight_decay * param.data)

    def zero_grad(self):
        for param in self.parameters:
            if param.grad is not None:
                param.grad.fill(0.0)

    def update_lr(self, factor):
        self.lr = self.base_lr * factor

# Pipeline
class Pipeline:
    def __init__(self, model, loss_fn=mse, optimizer=Adam, batch_size=16, task='regression', weight_decay=0.01):
        self.model = model
        self.loss_fn = loss_fn
        self.optimizer = optimizer(model.parameters(), lr=0.00001, weight_decay=weight_decay)
        self.batch_size = batch_size
        self.mean = None
        self.std = None
        self.task = task
        self.best_val_loss = float('inf')
        self.patience = 5  # Early stopping lebih ketat
        self.patience_counter = 0

    def preprocess(self, X, Y=None):
        if self.mean is None or self.std is None:
            self.mean = np.mean(X.data, axis=0)
            self.std = np.std(X.data, axis=0) + 1e-8
        X_norm = Tensor((X.data - self.mean) / self.std, requires_grad=X.requires_grad)
        return X_norm, Y

    def r2_score(self, y_true, y_pred):
        ss_tot = np.sum((y_true.data - np.mean(y_true.data)) ** 2)
        ss_res = np.sum((y_true.data - y_pred.data) ** 2)
        return 1 - ss_res / ss_tot if ss_tot > 0 else 0

    def accuracy(self, y_true, y_pred):
        if self.task == 'classification':
            pred_labels = np.argmax(y_pred.data, axis=-1)
            true_labels = np.argmax(y_true.data, axis=-1)
            return np.mean(pred_labels == true_labels)
        return self.r2_score(y_true, y_pred)

    def f1_score(self, y_true, y_pred):
        if self.task == 'classification':
            pred_labels = np.argmax(y_pred.data, axis=-1)
            true_labels = np.argmax(y_true.data, axis=-1)
            tp = np.sum((pred_labels == 1) & (true_labels == 1))
            fp = np.sum((pred_labels == 1) & (true_labels == 0))
            fn = np.sum((pred_labels == 0) & (true_labels == 1))
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        return 0.0

    def mae(self, y_true, y_pred):
        return np.mean(np.abs(y_true.data - y_pred.data))

    def evaluate_model_learning(self, losses, accuracies, maes, f1_scores=None, threshold_loss=0.1, threshold_acc=0.1, threshold_r2=0.1):
        is_learning = False
        message = ""
        initial_loss = losses[0]
        final_loss = losses[-1]
        loss_decrease = initial_loss - final_loss
        if loss_decrease > threshold_loss:
            is_learning = True
            message += f"Train Loss menurun dari {initial_loss:.4f} ke {final_loss:.4f}. "
        else:
            message += f"Train Loss tidak menurun signifikan: {initial_loss:.4f} ke {final_loss:.4f}. "
        if accuracies and len(accuracies) > 0:
            initial_acc = accuracies[0]
            final_acc = accuracies[-1]
            acc_increase = final_acc - initial_acc
            metric_name = 'Accuracy' if self.task == 'classification' else 'R2'
            if acc_increase > (threshold_acc if self.task == 'classification' else threshold_r2):
                is_learning = True
                message += f"Train {metric_name} meningkat dari {initial_acc:.4f} ke {final_acc:.4f}. "
            else:
                message += f"Train {metric_name} tidak meningkat signifikan: {initial_acc:.4f} ke {final_acc:.4f}. "
        if maes and len(maes) > 0:
            initial_mae = maes[0]
            final_mae = maes[-1]
            mae_decrease = initial_mae - final_mae
            if mae_decrease > 0.05:
                is_learning = True
                message += f"Train MAE menurun dari {initial_mae:.4f} ke {final_mae:.4f}. "
            else:
                message += f"Train MAE tidak menurun signifikan: {initial_mae:.4f} ke {final_mae:.4f}. "
        if self.task == 'classification' and f1_scores and len(f1_scores) > 0:
            initial_f1 = f1_scores[0]
            final_f1 = f1_scores[-1]
            f1_increase = final_f1 - initial_f1
            if f1_increase > 0.1:
                is_learning = True
                message += f"Train F1 meningkat dari {initial_f1:.4f} ke {final_f1:.4f}. "
            else:
                message += f"Train F1 tidak meningkat signifikan: {initial_f1:.4f} ke {final_f1:.4f}. "
        if is_learning:
            message = "Model belajar dengan baik. " + message
        else:
            message = "Model tidak belajar secara signifikan. " + message
        return message

    def fit(self, X_train, Y_train, X_val=None, Y_val=None, epochs=1000, early_stopping_threshold=0.0005, metric_interval=5):
        X_train_norm, Y_train = self.preprocess(X_train, Y_train)
        losses = []
        val_losses = []
        accuracies = []
        val_accuracies = []
        f1_scores = []
        val_f1_scores = []
        maes = []
        val_maes = []

        for epoch in range(epochs):
            if epoch % 50 == 0 and epoch > 0:
                self.optimizer.update_lr(0.95)
            self.model.train()
            indices = np.random.permutation(X_train_norm.data.shape[0])
            batch_losses = []

            for i in range(0, X_train_norm.data.shape[0], self.batch_size):
                self.optimizer.zero_grad()
                batch_indices = indices[i:i + self.batch_size]
                X_batch = Tensor(X_train_norm.data[batch_indices], requires_grad=True)
                Y_batch = Tensor(Y_train.data[batch_indices])
                pred = self.model(X_batch)
                loss = self.loss_fn(pred, Y_batch, model=self.model)
                batch_losses.append(loss.data)

                loss.backward()
                self.optimizer.step()

            losses.append(np.mean(batch_losses))
            if epoch % metric_interval == 0:
                pred_train = self.predict(X_train)
                accuracies.append(self.accuracy(Y_train, pred_train))
                maes.append(self.mae(Y_train, pred_train))
                if self.task == 'classification':
                    f1_scores.append(self.f1_score(Y_train, pred_train))

                if X_val is not None and Y_val is not None:
                    self.model.eval()
                    X_val_norm, Y_val = self.preprocess(X_val, Y_val)
                    pred_val = self.model(X_val_norm)
                    val_loss = self.loss_fn(pred_val, Y_val, model=self.model)
                    val_losses.append(val_loss.data)
                    val_accuracies.append(self.accuracy(Y_val, pred_val))
                    val_maes.append(self.mae(Y_val, pred_val))
                    if self.task == 'classification':
                        val_f1_scores.append(self.f1_score(Y_val, pred_val))

                    if val_loss.data < self.best_val_loss:
                        self.best_val_loss = val_loss.data
                        self.patience_counter = 0
                    else:
                        self.patience_counter += 1
                    if self.patience_counter >= self.patience:
                        print(f"Early stopping triggered after {epoch + 1} epochs")
                        break

                if epoch % metric_interval == 0:
                    if X_val is not None and Y_val is not None:
                        print(f"Epoch {epoch}, Train Loss: {losses[-1]:.6f}, Val Loss: {val_losses[-1]:.6f}, "
                              f"Train {'Acc' if self.task == 'classification' else 'R2'}: {accuracies[-1]:.6f}, "
                              f"Val {'Acc' if self.task == 'classification' else 'R2'}: {val_accuracies[-1]:.6f}, "
                              f"Train MAE: {maes[-1]:.6f}, Val MAE: {val_maes[-1]:.6f}" +
                              (f", Train F1: {f1_scores[-1]:.6f}, Val F1: {val_f1_scores[-1]:.6f}" if self.task == 'classification' else ""))
                    else:
                        print(f"Epoch {epoch}, Train Loss: {losses[-1]:.6f}, "
                              f"Train {'Acc' if self.task == 'classification' else 'R2'}: {accuracies[-1]:.6f}, "
                              f"Train MAE: {maes[-1]:.6f}" +
                              (f", Train F1: {f1_scores[-1]:.6f}" if self.task == 'classification' else ""))

        print("----------------------------------------------------------------------")
        print("Statistik Pelatihan:")
        print(f"Train Loss - Min: {np.min(losses):.6f}, Max: {np.max(losses):.6f}, Mean: {np.mean(losses):.6f}")
        print(f"Train {'Acc' if self.task == 'classification' else 'R2'} - Min: {np.min(accuracies):.6f}, Max: {np.max(accuracies):.6f}, Mean: {np.mean(accuracies):.6f}")
        print(f"Train MAE - Min: {np.min(maes):.6f}, Max: {np.max(maes):.6f}, Mean: {np.mean(maes):.6f}")
        if val_losses:
            print(f"Val Loss - Min: {np.min(val_losses):.6f}, Max: {np.max(val_losses):.6f}, Mean: {np.mean(val_losses):.6f}")
            print(f"Val {'Acc' if self.task == 'classification' else 'R2'} - Min: {np.min(val_accuracies):.6f}, Max: {np.max(val_accuracies):.6f}, Mean: {np.mean(val_accuracies):.6f}")
            print(f"Val MAE - Min: {np.min(val_maes):.6f}, Max: {np.max(val_maes):.6f}, Mean: {np.mean(val_maes):.6f}")
        print("Hasil Evaluasi Pelatihan:")
        print(self.evaluate_model_learning(losses, accuracies, maes, f1_scores if self.task == 'classification' else None))
        print("----------------------------------------------------------------------")

        return losses, val_losses, accuracies, val_accuracies, maes, val_maes, f1_scores, val_f1_scores

    def predict(self, X):
        self.model.eval()
        X_norm, _ = self.preprocess(X)
        return self.model(X_norm)

# Unit Test
class TestMiniTorch(unittest.TestCase):
    def setUp(self):
        self.x = Tensor(np.array([[1.0], [2.0], [3.0]]), requires_grad=True)
        self.y = Tensor(np.array([[2.0], [4.0], [6.0]]), requires_grad=False)
        np.random.seed(42)

    def test_tensor_operations(self):
        x1 = Tensor(np.array([1.0, 2.0]), requires_grad=True)
        x2 = Tensor(np.array([3.0, 4.0]), requires_grad=True)
        y = x1 + x2
        self.assertTrue(np.allclose(y.data, np.array([4.0, 6.0])))
        self.assertTrue(y.requires_grad)
        z = x1 * x2
        self.assertTrue(np.allclose(z.data, np.array([3.0, 8.0])))
        self.assertTrue(z.requires_grad)
        z.backward(np.array([1.0, 1.0]))
        self.assertTrue(np.allclose(x1.grad, np.array([3.0, 4.0])))
        self.assertTrue(np.allclose(x2.grad, np.array([1.0, 2.0])))
        y_scalar = x1 + 5.0
        self.assertTrue(np.allclose(y_scalar.data, np.array([6.0, 7.0])))
        z_scalar = 2.0 * x1
        self.assertTrue(np.allclose(z_scalar.data, np.array([2.0, 4.0])))

    def test_linear_layer(self):
        linear = Linear(1, 3, init_method='he')
        linear.W.data = np.array([[1.0, 2.0, 3.0]])
        linear.b.data = np.array([0.1, 0.2, 3.0])
        out = linear(self.x)
        expected = np.array([[1.1, 2.2, 6.0], [2.1, 4.2, 9.0], [3.1, 6.2, 12.0]])
        self.assertTrue(np.allclose(out.data, expected))
        self.assertTrue(out.requires_grad)
        out.backward(np.ones_like(out.data))
        self.assertTrue(np.allclose(linear.W.grad, np.array([[6.0, 6.0, 6.0]])))
        self.assertTrue(np.allclose(linear.b.grad, np.array([3.0, 3.0, 3.0])))
        self.assertTrue(np.allclose(self.x.grad, np.array([[6.0], [6.0], [6.0]])))

    def test_leaky_relu(self):
        leaky_relu = LeakyReLU(negative_slope=0.02)
        x = Tensor(np.array([[-1.0], [0.0], [1.0]]), requires_grad=True)
        out = leaky_relu(x)
        expected = np.array([[-0.02], [0.0], [1.0]])
        self.assertTrue(np.allclose(out.data, expected, atol=1e-5))
        out.backward(np.ones_like(out.data))
        self.assertTrue(np.allclose(x.grad, [[0.02], [1.0], [1.0]], atol=1e-5))

    def test_relu(self):
        relu = ReLU()
        x = Tensor(np.array([[-1.0], [0.0], [1.0]]), requires_grad=True)
        out = relu(x)
        expected = np.array([[0.0], [0.0], [1.0]])
        self.assertTrue(np.allclose(out.data, expected, atol=1e-5))
        out.backward(np.ones_like(out.data))
        self.assertTrue(np.allclose(x.grad, [[0.0], [0.0], [1.0]], atol=1e-5))

    def test_sigmoid(self):
        sigmoid = Sigmoid()
        x = Tensor(np.array([[-1.0], [0.0], [1.0]]), requires_grad=True)
        out = sigmoid(x)
        expected = 1 / (1 + np.exp(-np.clip(x.data, -500, 500)))
        self.assertTrue(np.allclose(out.data, expected, atol=1e-5))
        out.backward(np.ones_like(out.data))
        s = expected
        expected_grad = s * (1 - s)
        self.assertTrue(np.allclose(x.grad, expected_grad, atol=1e-5))

    def test_tanh(self):
        tanh = Tanh()
        x = Tensor(np.array([[-1.0], [0.0], [1.0]]), requires_grad=True)
        out = tanh(x)
        expected = np.tanh(x.data)
        self.assertTrue(np.allclose(out.data, expected, atol=1e-5))
        out.backward(np.ones_like(out.data))
        expected_grad = 1 - out.data ** 2
        self.assertTrue(np.allclose(x.grad, expected_grad, atol=1e-5))

    def test_dropout(self):
        dropout = Dropout(p=0.5)
        x = Tensor(np.array([[1.0], [2.0], [3.0]]), requires_grad=True)
        np.random.seed(42)
        out = dropout(x)
        out.backward(np.ones_like(out.data))
        self.assertTrue(np.allclose(x.grad.shape, x.data.shape))
        dropout.eval()
        out_eval = dropout(x)
        self.assertTrue(np.allclose(out_eval.data, x.data))

    def test_batchnorm1d(self):
        bn = BatchNorm1D(3)
        x = Tensor(np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]), requires_grad=True)
        out = bn(x)
        out.backward(np.ones_like(out.data))
        self.assertTrue(np.allclose(bn.gamma.grad.shape, [3]))
        self.assertTrue(np.allclose(bn.beta.grad.shape, [3]))
        bn.eval()
        out_eval = bn(x)
        self.assertTrue(np.allclose(out_eval.data.shape, x.data.shape))

    def test_bce_loss(self):
        pred = Tensor(np.array([[0.1], [0.5], [0.9]]), requires_grad=True)
        target = Tensor(np.array([[0.0], [1.0], [1.0]]), requires_grad=False)
        model = Sequential(Linear(1, 1))
        loss = bce(pred, target, model=model, reduction='mean')
        pred_data = np.clip(pred.data, 1e-15, 1 - 1e-15)
        expected_loss = -np.mean(target.data * np.log(pred_data) + (1 - target.data) * np.log(1 - pred_data))
        self.assertTrue(np.allclose(loss.data, expected_loss, atol=1e-5))
        loss.backward()
        expected_grad = (pred_data - target.data) / (pred_data * (1 - pred_data) * pred.data.size)
        self.assertTrue(np.allclose(pred.grad, expected_grad, atol=1e-5))
        self.assertIsNone(target.grad)

    def test_mse_loss(self):
        pred = Tensor(np.array([[1.0], [2.0], [3.0]]), requires_grad=True)
        target = Tensor(np.array([[2.0], [4.0], [6.0]]), requires_grad=False)
        model = Sequential(Linear(1, 1))
        loss = mse(pred, target, model=model, reduction='mean')
        expected_loss = np.mean((pred.data - target.data) ** 2)
        self.assertTrue(np.allclose(loss.data, expected_loss))
        loss.backward()
        expected_grad = 2 * (pred.data - target.data) / pred.data.size
        self.assertTrue(np.allclose(pred.grad, expected_grad))
        self.assertIsNone(target.grad)

    def test_cross_entropy_loss(self):
        pred = Tensor(np.array([[0.1, 0.9], [0.7, 0.3], [0.2, 0.8]]), requires_grad=True)
        target = Tensor(np.array([[0, 1], [1, 0], [0, 1]]), requires_grad=False)
        loss = cross_entropy(pred, target, reduction='mean')
        pred_data = np.clip(pred.data, 1e-15, 1 - 1e-15)
        expected_loss = -np.mean(np.sum(target.data * np.log(pred_data), axis=-1))
        self.assertTrue(np.allclose(loss.data, expected_loss, atol=1e-5))
        loss.backward()
        expected_grad = (pred_data - target.data) / pred.data.shape[0]
        self.assertTrue(np.allclose(pred.grad, expected_grad, atol=1e-5))

    def test_softmax(self):
        x = Tensor(np.array([[1.0, 2.0], [3.0, 4.0]]), requires_grad=True)
        softmax = Softmax()
        out = softmax(x)
        exp_x = np.exp(x.data - np.max(x.data, axis=-1, keepdims=True))
        expected = exp_x / np.sum(exp_x, axis=-1, keepdims=True)
        self.assertTrue(np.allclose(out.data, expected, atol=1e-5))
        out.backward(np.ones_like(out.data))
        batch_size = out.data.shape[0]
        expected_grad = np.zeros_like(out.data)
        for i in range(batch_size):
            s = out.data[i]
            jacobian = np.diag(s) - np.outer(s, s)
            expected_grad[i] = np.dot(np.ones_like(out.data[i]), jacobian)
        self.assertTrue(np.allclose(x.grad, expected_grad, atol=1e-5))

    def test_sequential_model(self):
        model = Sequential(
            Linear(1, 2, init_method='he'),
            LeakyReLU(negative_slope=0.02),
            Linear(2, 1, init_method='he')
        )
        model.layers[0].W.data = np.array([[1.0, 2.0]])
        model.layers[0].b.data = np.array([0.1, 0.2])
        model.layers[2].W.data = np.array([[0.5], [0.5]])
        model.layers[2].b.data = np.array([0.1])
        out = model(self.x)
        expected = np.array([[1.75], [3.25], [4.75]])
        self.assertTrue(np.allclose(out.data, expected, atol=1e-5))
        out.backward(np.ones_like(out.data))
        self.assertIsNotNone(model.layers[0].W.grad)
        self.assertIsNotNone(model.layers[0].b.grad)
        self.assertIsNotNone(model.layers[2].W.grad)
        self.assertIsNotNone(model.layers[2].b.grad)

    def test_optimizer(self):
        linear = Linear(1, 1, init_method='he')
        linear.W.data = np.array([[2.0]])
        linear.b.data = np.array([1.0])
        optimizer = Adam([linear.W, linear.b], lr=0.1, weight_decay=0.001)
        x = Tensor(np.array([[1.0]]), requires_grad=True)
        y = Tensor(np.array([[3.0]]), requires_grad=False)
        pred = linear(x)
        loss = mse(pred, y, model=linear)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        self.assertTrue(np.allclose(linear.W.data.shape, [1, 1]))
        self.assertTrue(np.allclose(linear.b.data.shape, [1]))

    def test_pipeline_classification(self):
        model = Sequential(
            Linear(2, 30, init_method='xavier'),
            BatchNorm1D(30),
            Tanh(),
            Dropout(0.2),
            Linear(30, 15, init_method='xavier'),
            Tanh(),
            Linear(15, 2, init_method='xavier'),
            Softmax()
        )
        pipeline = Pipeline(model, loss_fn=cross_entropy, optimizer=Adam, batch_size=16, task='classification', weight_decay=0.01)
        X, Y = generate_classification_data(1000, 0.05)
        train_size = int(0.8 * len(X.data))
        X_train, X_val = Tensor(X.data[:train_size]), Tensor(X.data[train_size:])
        Y_train, Y_val = Tensor(Y.data[:train_size]), Tensor(Y.data[train_size:])
        losses, val_losses, accuracies, val_accuracies, maes, val_maes, f1_scores, val_f1_scores = pipeline.fit(X_train, Y_train, X_val, Y_val, epochs=500, metric_interval=5)
        self.assertTrue(losses[-1] < losses[0])
        self.assertTrue(accuracies[-1] > 0.5)
        pred = pipeline.predict(X)
        self.assertTrue(pred.data.shape == Y.data.shape)

    def test_pipeline_regression(self):
        model = Sequential(
            Linear(1, 32, init_method='he'),
            BatchNorm1D(32),
            Tanh(),
            Dropout(0.2),
            Linear(32, 16, init_method='he'),
            BatchNorm1D(16),
            Tanh(),
            Linear(16, 8, init_method='he'),
            BatchNorm1D(8),
            Tanh(),
            Linear(8, 1, init_method='he')
        )
        pipeline = Pipeline(model, loss_fn=mse, optimizer=lambda params: Adam(params, lr=0.001, weight_decay=0.001), batch_size=16, task='regression', weight_decay=0.001)
        X, Y = generate_mixed_data(1000, 0.001)
        train_size = int(0.8 * len(X.data))
        X_train, X_val = Tensor(X.data[:train_size]), Tensor(X.data[train_size:])
        Y_train, Y_val = Tensor(Y.data[:train_size]), Tensor(Y.data[train_size:])
        losses, val_losses, accuracies, val_accuracies, maes, val_maes, f1_scores, val_f1_scores = pipeline.fit(X_train, Y_train, X_val, Y_val, epochs=1000, metric_interval=5)
        self.assertTrue(losses[-1] < losses[0])
        pred = pipeline.predict(X)
        self.assertTrue(pred.data.shape == Y.data.shape)

    def test_pipeline_quadratic(self):
        model = Sequential(
            Linear(1, 16, init_method='he'),
            BatchNorm1D(16),
            Tanh(),
            Dropout(0.2),
            Linear(16, 8, init_method='he'),
            BatchNorm1D(8),
            Tanh(),
            Linear(8, 4, init_method='he'),
            BatchNorm1D(4),
            Tanh(),
            Linear(4, 1, init_method='he')
        )
        pipeline = Pipeline(model, loss_fn=mse, optimizer=lambda params: Adam(params, lr=0.001, weight_decay=0.0001), batch_size=16, task='regression', weight_decay=0.0001)
        X, Y = generate_quadratic_data(1000, 0.001)
        train_size = int(0.8 * len(X.data))
        X_train, X_val = Tensor(X.data[:train_size]), Tensor(X.data[train_size:])
        Y_train, Y_val = Tensor(Y.data[:train_size]), Tensor(Y.data[train_size:])
        losses, val_losses, accuracies, val_accuracies, maes, val_maes, f1_scores, val_f1_scores = pipeline.fit(X_train, Y_train, X_val, Y_val, epochs=1000, metric_interval=5)
        self.assertTrue(losses[-1] < losses[0])
        pred = pipeline.predict(X)
        self.assertTrue(pred.data.shape == Y.data.shape)

    def test_pipeline_nonlinear(self):
        model = Sequential(
            Linear(1, 100, init_method='he'),
            BatchNorm1D(100),
            LeakyReLU(negative_slope=0.01),
            Dropout(0.4),
            Linear(100, 80, init_method='he'),
            BatchNorm1D(80),
            LeakyReLU(negative_slope=0.01),
            Linear(80, 60, init_method='he'),
            BatchNorm1D(60),
            LeakyReLU(negative_slope=0.01),
            Linear(60, 40, init_method='he'),
            BatchNorm1D(40),
            LeakyReLU(negative_slope=0.01),
            Linear(40, 20, init_method='he'),
            BatchNorm1D(20),
            LeakyReLU(negative_slope=0.01),
            Linear(20, 1, init_method='he')
        )
        pipeline = Pipeline(model, loss_fn=mse, optimizer=Adam, batch_size=16, task='regression', weight_decay=0.01)
        X, Y = generate_nonlinear_data(1000, 0.001)
        train_size = int(0.8 * len(X.data))
        X_train, X_val = Tensor(X.data[:train_size]), Tensor(X.data[train_size:])
        Y_train, Y_val = Tensor(Y.data[:train_size]), Tensor(Y.data[train_size:])
        losses, val_losses, accuracies, val_accuracies, maes, val_maes, f1_scores, val_f1_scores = pipeline.fit(X_train, Y_train, X_val, Y_val, epochs=1000, metric_interval=5)
        self.assertTrue(losses[-1] < losses[0])
        pred = pipeline.predict(X)
        self.assertTrue(pred.data.shape == Y.data.shape)


