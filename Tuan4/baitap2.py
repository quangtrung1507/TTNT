import string
import networkx as nx
import matplotlib.pyplot as plt


def read_adjacency_matrix(filename):
    """
    Đọc ma trận kề từ file txt.
    Mỗi dòng: các số 0/1 cách nhau bằng dấu cách.
    Trả về: ma trận G (list[list[int]]).
    """
    G = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = [int(x) for x in line.split()]
            G.append(row)

    # Kiểm tra ma trận vuông
    n = len(G)
    for row in G:
        if len(row) != n:
            raise ValueError("Ma trận kề trong file không vuông (số cột != số dòng).")

    return G


def build_nodes(G):
    """
    Sinh tên đỉnh A, B, C, ... dựa vào số đỉnh trong ma trận G.
    """
    n = len(G)
    if n > 26:
        raise ValueError("Chỉ hỗ trợ tối đa 26 đỉnh (A–Z).")
    return list(string.ascii_uppercase[:n])


def compute_degrees(G):
    """
    Tính bậc của mỗi đỉnh trong ma trận kề G.
    degree[i] = tổng các phần tử dòng i.
    """
    return [sum(row) for row in G]


def sort_nodes_by_degree(nodes, degrees):
    """
    Sắp xếp đỉnh theo thứ tự bậc giảm dần (dùng selection sort giống bài mẫu).
    Trả về: danh sách tên đỉnh đã được sắp xếp.
    """
    sorted_nodes = []
    used_idx = []

    for _ in range(len(degrees)):
        _max = -1
        idx = None
        for j, deg in enumerate(degrees):
            if j not in used_idx and deg > _max:
                _max = deg
                idx = j
        used_idx.append(idx)
        sorted_nodes.append(nodes[idx])

    return sorted_nodes


def greedy_coloring(G, nodes, sorted_nodes, colors=None):
    """
    Thuật toán tô màu tham lam:
    - Duyệt đỉnh theo thứ tự bậc giảm dần (sorted_nodes).
    - Mỗi đỉnh chọn màu khả dụng đầu tiên.
    - Cấm màu đó ở các đỉnh kề.
    Trả về: dict {đỉnh: màu}.
    """
    if colors is None:
        colors = ["blue", "red", "yellow", "green"]  # dùng luôn màu matplotlib

    # map tên đỉnh -> chỉ số trong ma trận
    t_ = {nodes[i]: i for i in range(len(nodes))}

    # Mỗi đỉnh có một bản copy danh sách màu
    colorDict = {node: colors[:] for node in nodes}

    solution = {}
    for n_ in sorted_nodes:
        available = colorDict[n_]
        if not available:
            raise ValueError(f"Không còn màu khả dụng cho đỉnh {n_}")

        chosen = available[0]
        solution[n_] = chosen

        # Cấm màu chosen ở các đỉnh kề
        row = G[t_[n_]]
        for j, adj in enumerate(row):
            if adj == 1 and chosen in colorDict[nodes[j]]:
                colorDict[nodes[j]].remove(chosen)

    return solution


def print_solution(solution, filename=None):
    """
    In kết quả tô màu ra màn hình.
    """
    if filename:
        print(f"Kết quả tô màu đồ thị đọc từ file {filename}:")
    else:
        print("Kết quả tô màu đồ thị:")

    for node in sorted(solution.keys()):
        print(f"Đỉnh {node} = {solution[node]}")


def draw_graph(G, nodes, solution=None, save_path=None):
    """
    Vẽ sơ đồ đồ thị từ ma trận kề G.
    - Nếu solution != None thì tô màu đỉnh theo solution (dict {đỉnh: màu}).
    - Nếu save_path != None thì lưu hình ra file, ví dụ: 'graph.png'
    """
    # 1. Tạo đồ thị NetworkX
    G_nx = nx.Graph()

    # Thêm các đỉnh
    for node in nodes:
        G_nx.add_node(node)

    # Thêm các cạnh từ ma trận kề
    n = len(nodes)
    for i in range(n):
        for j in range(i + 1, n):  # chỉ cần nửa trên vì đồ thị vô hướng
            if G[i][j] == 1:
                G_nx.add_edge(nodes[i], nodes[j])

    # 2. Tính vị trí các đỉnh (layout)
    pos = nx.spring_layout(G_nx)  # layout lò xo, nhìn khá đẹp

    # 3. Chuẩn bị màu cho từng đỉnh (nếu có solution)
    if solution is not None:
        node_colors = [solution[node] for node in G_nx.nodes()]
    else:
        node_colors = "lightgray"

    # 4. Vẽ đồ thị
    plt.figure(figsize=(6, 6))
    nx.draw(
        G_nx,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=800,
        font_size=12,
        font_weight="bold",
        edge_color="black",
    )
    plt.title("Đồ thị từ ma trận kề")

    # 5. Lưu file nếu cần
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Đã lưu hình đồ thị tại: {save_path}")

    # 6. Hiển thị cửa sổ hình
    plt.show()


def main():
    filename = "graph.txt"   # đổi tên nếu cần
    # 1. Đọc ma trận
    G = read_adjacency_matrix(filename)
    # 2. Tạo tên đỉnh
    nodes = build_nodes(G)
    # 3. Tính bậc
    degrees = compute_degrees(G)
    # 4. Sắp xếp theo bậc giảm dần
    sorted_nodes = sort_nodes_by_degree(nodes, degrees)
    # 5. Tô màu
    solution = greedy_coloring(G, nodes, sorted_nodes)
    # 6. In kết quả
    print_solution(solution, filename)
    # 7. Vẽ đồ thị (tô màu theo solution) và lưu thành file PNG
    draw_graph(G, nodes, solution, save_path="graph_colored.png")


if __name__ == "__main__":
    main()
