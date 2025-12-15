# BƯỚC 1: IMPORT CÁC THƯ VIỆN CẦN THIẾT
import numpy as np                 # Tính toán số
import matplotlib.pyplot as plt    # Vẽ đồ thị
from scipy.spatial.distance import cdist   # Tính khoảng cách


# BƯỚC 2: KHỞI TẠO DỮ LIỆU
means = [[2, 2], [9, 2], [4, 9]]
cov = [[2, 0], [0, 2]]
n_samples = 500
n_cluster = 3

X0 = np.random.multivariate_normal(means[0], cov, n_samples)
X1 = np.random.multivariate_normal(means[1], cov, n_samples)
X2 = np.random.multivariate_normal(means[2], cov, n_samples)

X = np.concatenate((X0, X1, X2), axis=0)    # (1500, 2)


# BƯỚC 3: XEM PHÂN BỐ DỮ LIỆU BAN ĐẦU
plt.xlabel('x')
plt.ylabel('y')
plt.title('Raw data')
plt.plot(X[:, 0], X[:, 1], 'bo', markersize=5)
plt.show()


# BƯỚC 4: HÀM KHỞI TẠO n_cluster TÂM CỤM
def kmeans_init_centers(X, n_cluster):
    """
    Chọn ngẫu nhiên n_cluster điểm trong X làm tâm ban đầu.
    """
    # random k index between 0 and shape(X) without duplicate index.
    idx = np.random.choice(X.shape[0], n_cluster, replace=False)
    # Then return X[index] as cluster
    return X[idx]


# BƯỚC 5: HÀM GÁN NHÃN CỤM CHO TỪNG ĐIỂM
def kmeans_predict_labels(X, centers):
    """
    Với mỗi điểm trong X, tìm tâm gần nhất và gán nhãn cụm tương ứng.
    """
    D = cdist(X, centers)             # ma trận khoảng cách (num_points x n_cluster)
    # return index of the closest center
    return np.argmin(D, axis=1)


# BƯỚC 6: HÀM CẬP NHẬT LẠI TÂM CỤM
def kmeans_update_centers(X, labels, n_cluster):
    """
    Cập nhật lại vị trí tâm cụm bằng trung bình các điểm thuộc mỗi cụm.
    """
    centers = np.zeros((n_cluster, X.shape[1]))
    for k in range(n_cluster):
        # collect all points assigned to the k-th cluster
        Xk = X[labels == k, :]
        # take average
        centers[k, :] = np.mean(Xk, axis=0)
    return centers


# BƯỚC 7: HÀM KIỂM TRA TÍNH HỘI TỤ
def kmeans_has_converged(centers, new_centers):
    """
    Trả về True nếu hai bộ tâm cụm giống nhau.
    (So sánh bằng set của các tuple tọa độ)
    """
    return set([tuple(a) for a in centers]) == set([tuple(a) for a in new_centers])


# BƯỚC 8: HÀM VẼ KẾT QUẢ LÊN ĐỒ THỊ
# Random color chỉ phù hợp với k <= 4 trong ví dụ này
def kmeans_visualize(X, centers, labels, n_cluster, title):
    plt.xlabel('x')    # label trục x
    plt.ylabel('y')    # label trục y
    plt.title(title)   # tiêu đề đồ thị

    plt_colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

    for i in range(n_cluster):
        # lấy dữ liệu của cụm i
        data = X[labels == i]
        # vẽ các điểm thuộc cụm i
        plt.plot(
            data[:, 0],
            data[:, 1],
            plt_colors[i] + '^',
            markersize=4,
            label='cluster_' + str(i)
        )
        # vẽ tâm cụm i
        plt.plot(
            centers[i][0],
            centers[i][1],
            plt_colors[i + 4] + 'o',
            markersize=10,
            label='center_' + str(i)
        )

    plt.legend()
    plt.show()


# BƯỚC 9: TOÀN BỘ THUẬT TOÁN K-MEANS
def kmeans(init_centers, init_labels, X, n_cluster):
    centers = init_centers
    labels = init_labels
    times = 0

    while True:
        # Gán nhãn cho các điểm
        labels = kmeans_predict_labels(X, centers)
        kmeans_visualize(
            X, centers, labels, n_cluster,
            'Assigned label for data at time = ' + str(times + 1)
        )

        # Cập nhật tâm cụm
        new_centers = kmeans_update_centers(X, labels, n_cluster)

        # Kiểm tra hội tụ
        if kmeans_has_converged(centers, new_centers):
            break

        centers = new_centers
        kmeans_visualize(
            X, centers, labels, n_cluster,
            'Update center position at time = ' + str(times + 1)
        )

        times += 1

    return centers, labels, times


# BƯỚC 10: GỌI HÀM KMEANS ĐỂ THỰC THI
init_centers = kmeans_init_centers(X, n_cluster)
print("Init centers:")
print(init_centers)   # In ra tọa độ khởi tạo ban đầu của các tâm cụm

# Gán tạm tất cả điểm vào cụm 0 để vẽ bước khởi tạo
init_labels = np.zeros(X.shape[0], dtype=int)
kmeans_visualize(
    X, init_centers, init_labels, n_cluster,
    'Init centers in the first run. Assigned all data as cluster 0'
)

centers, labels, times = kmeans(init_centers, init_labels, X, n_cluster)
print('Done! Kmeans has converged after', times, 'times')
print('Final centers:')
print(centers)
