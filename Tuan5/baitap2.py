import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# BƯỚC 1: TẠO DỮ LIỆU CÓ NHÃN (3 LỚP)
# Có thể dùng lại means, cov, n_samples, n_cluster như bài 1
means = [[2, 2], [9, 2], [4, 9]]
cov = [[2, 0], [0, 2]]
n_samples = 500
n_cluster = 3

X0 = np.random.multivariate_normal(means[0], cov, n_samples)
X1 = np.random.multivariate_normal(means[1], cov, n_samples)
X2 = np.random.multivariate_normal(means[2], cov, n_samples)

X = np.concatenate((X0, X1, X2), axis=0)   # (1500, 2)

# Tạo nhãn cho từng cụm:
# cụm quanh (2,2) -> label 0
# cụm quanh (9,2) -> label 1
# cụm quanh (4,9) -> label 2
y0 = np.zeros(n_samples, dtype=int)
y1 = np.ones(n_samples, dtype=int)
y2 = np.full(n_samples, 2, dtype=int)

y = np.concatenate((y0, y1, y2), axis=0)   # (1500,)

# BƯỚC 2: VẼ DỮ LIỆU ĐỂ QUAN SÁT
plt.figure()
plt.title("Data for K-NN (3 classes)")
plt.xlabel("x")
plt.ylabel("y")
plt.scatter(X0[:, 0], X0[:, 1], s=5, label="class 0")
plt.scatter(X1[:, 0], X1[:, 1], s=5, label="class 1")
plt.scatter(X2[:, 0], X2[:, 1], s=5, label="class 2")
plt.legend()
plt.show()

# BƯỚC 3: CHIA TRAIN / TEST
# Ví dụ: 70% train, 30% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y  # giữ tỉ lệ lớp
)

# BƯỚC 4: HUẤN LUYỆN MÔ HÌNH K-NN CHO MỘT GIÁ TRỊ k CỤ THỂ
k = 5  # bạn có thể thử k = 1, 3, 5, 7, ...
knn = KNeighborsClassifier(n_neighbors=k)
knn.fit(X_train, y_train)

# BƯỚC 5: DỰ ĐOÁN TRÊN TẬP TEST
y_pred = knn.predict(X_test)

# BƯỚC 6: ĐÁNH GIÁ MÔ HÌNH
acc = accuracy_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print(f"Accuracy với k = {k}: {acc:.4f}")
print("Confusion matrix:")
print(cm)
print("Classification report:")
print(classification_report(y_test, y_pred))

# BƯỚC 7: THỬ NHIỀU GIÁ TRỊ k KHÁC NHAU
k_values = [1, 3, 5, 7, 9, 11]
accuracies = []

for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    accuracies.append(acc)
    print(f"k = {k:2d} -> accuracy = {acc:.4f}")

# Vẽ biểu đồ accuracy theo k
plt.figure()
plt.plot(k_values, accuracies, marker='o')
plt.title("Accuracy theo số lượng hàng xóm k")
plt.xlabel("k")
plt.ylabel("Accuracy")
plt.grid(True)
plt.show()
