import string

def read_adjacency_matrix(filename):
    """
    Đọc ma trận kề từ file txt.
    - Mỗi dòng: các số 0/1 cách nhau bằng dấu cách.
    - Trả về: ma trận G (list[list[int]])
    """
    G = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:          # bỏ qua dòng trống
                continue
            row = [int(x) for x in line.split()]
            G.append(row)

    # Kiểm tra ma trận vuông
    n = len(G)
    for row in G:
        if len(row) != n:
            raise ValueError("Ma trận kề trong file không vuông (số cột != số dòng).")

    return G


# ================== CHƯƠNG TRÌNH CHÍNH ==================
if __name__ == "__main__":
    # 1. Đọc ma trận kề từ file
    filename = "graph.txt"   # đổi tên nếu bạn dùng file khác
    G = read_adjacency_matrix(filename)

    # 2. Sinh tên các đỉnh tự động: A, B, C, ...
    n = len(G)
    if n > 26:
        raise ValueError("Ví dụ này chỉ đặt tên đỉnh từ A–Z, tối đa 26 đỉnh.")
    node = string.ascii_uppercase[:n]   # "ABCDEF..." tùy theo n

    # 3. Tạo map tên đỉnh -> chỉ số
    t_ = {}
    for i in range(len(G)):
        t_[node[i]] = i

    # 4. Tính bậc của các đỉnh
    degree = []
    for i in range(len(G)):
        degree.append(sum(G[i]))

    # 5. Các màu có thể dùng
    colorDict = {}
    for i in range(len(G)):
        colorDict[node[i]] = ["Blue", "Red", "Yellow", "Green"]

    # 6. Sắp xếp các đỉnh theo thứ tự bậc giảm dần (giống code mẫu dùng selection sort)
    sortedNode = []
    indeks = []
    for i in range(len(degree)):
        _max = -1
        # tìm đỉnh có bậc lớn nhất chưa chọn
        for j in range(len(degree)):
            if j not in indeks:
                if degree[j] > _max:
                    _max = degree[j]
                    idx = j
        indeks.append(idx)
        sortedNode.append(node[idx])

    # 7. Tô màu (tham lam – greedy)
    theSolution = {}
    for n_ in sortedNode:
        setTheColor = colorDict[n_]
        # chọn màu đầu tiên còn lại
        theSolution[n_] = setTheColor[0]

        # cấm màu này ở các đỉnh kề
        adjacentNode = G[t_[n_]]
        for j in range(len(adjacentNode)):
            if adjacentNode[j] == 1 and (setTheColor[0] in colorDict[node[j]]):
                colorDict[node[j]].remove(setTheColor[0])

    # 8. In kết quả
    print("Kết quả tô màu đồ thị đọc từ file", filename)
    for t, w in sorted(theSolution.items()):
        print("Đỉnh", t, "=", w)
