import math

def read_cost_matrix(filename):
    """
    Đọc ma trận chi phí từ file txt.
    Mỗi dòng: các số cách nhau bằng dấu cách.
    Trả về: ma trận cost (list[list[float]]).
    """
    cost = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = [float(x) for x in line.split()]
            cost.append(row)

    # Kiểm tra ma trận vuông
    n = len(cost)
    for row in cost:
        if len(row) != n:
            raise ValueError("Ma trận chi phí không vuông (số cột != số dòng).")

    return cost


def tsp_backtracking(cost, start=0):
    """
    Giải bài toán người bán hàng (TSP) bằng quay lui (backtracking).

    - cost: ma trận chi phí cost[i][j]
    - start: thành phố xuất phát (mặc định = 0)

    Trả về:
    - best_cost: chi phí nhỏ nhất tìm được
    - best_path: chu trình tối ưu (list các đỉnh, kết thúc bằng 'start')
    """
    n = len(cost)
    visited = [False] * n
    visited[start] = True  # đã thăm thành phố xuất phát

    best_cost = math.inf
    best_path = []
    path = [start]  # đường đi hiện tại

    def backtrack(current_city, count_visited, cost_so_far):
        nonlocal best_cost, best_path

        # Nếu đã đi qua tất cả thành phố
        if count_visited == n:
            # quay về thành phố xuất phát
            total_cost = cost_so_far + cost[current_city][start]
            if total_cost < best_cost:
                best_cost = total_cost
                best_path = path[:] + [start]
            return

        # Cắt tỉa: chi phí hiện tại đã >= tốt nhất thì khỏi đi tiếp nhánh này
        if cost_so_far >= best_cost:
            return

        # Thử đi đến từng thành phố chưa thăm
        for next_city in range(n):
            if not visited[next_city]:
                visited[next_city] = True
                path.append(next_city)

                backtrack(
                    next_city,
                    count_visited + 1,
                    cost_so_far + cost[current_city][next_city]
                )

                # quay lui
                path.pop()
                visited[next_city] = False

    # Gọi đệ quy từ thành phố xuất phát
    backtrack(start, 1, 0.0)
    return best_cost, best_path


def main():
    filename = "tsp.txt"   # đổi tên nếu cần
    cost = read_cost_matrix(filename)

    print("Ma trận chi phí đọc từ file:", filename)
    for row in cost:
        print(row)

    best_cost, best_path = tsp_backtracking(cost, start=0)

    print("\nChu trình tối ưu tìm được (theo chỉ số đỉnh):")
    # In dạng 0 -> 2 -> 1 -> 3 -> 0
    print(" -> ".join(str(x) for x in best_path))
    print("Tổng chi phí:", best_cost)


if __name__ == "__main__":
    main()
