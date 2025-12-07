## Bài 1. Tô màu đồ thị từ ma trận kề

Trong bài toán này, mục tiêu là xây dựng một chương trình có khả năng **tô màu các đỉnh của một đồ thị vô hướng** sao cho **không có hai đỉnh kề nhau nào được gán cùng một màu**. Dữ liệu đầu vào được cung cấp dưới dạng **ma trận kề** lưu trong một tệp văn bản. Từ ma trận này, chương trình đọc và xây dựng lại cấu trúc đồ thị trong bộ nhớ, sau đó áp dụng **thuật toán tô màu tham lam (greedy)** để tìm một phương án tô màu hợp lệ.

### 1. Đọc ma trận kề từ file

Chương trình định nghĩa hàm `read_adjacency_matrix` để đọc ma trận kề từ file văn bản. Tệp dữ liệu đầu vào là một file (ví dụ `graph.txt`), trong đó mỗi dòng tương ứng với một hàng của ma trận kề. Các phần tử trên dòng được phân tách bằng dấu cách, giá trị bằng `0` thể hiện giữa hai đỉnh không có cạnh nối, còn giá trị bằng `1` thể hiện tồn tại cạnh nối giữa hai đỉnh tương ứng. Đồng thời, chương trình cũng kiểm tra ma trận phải là ma trận vuông:

```python
import string

def read_adjacency_matrix(filename):
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
````

### 2. Gán nhãn đỉnh và tạo ánh xạ

Sau khi đọc xong, chương trình gán nhãn cho các đỉnh lần lượt là `A, B, C, …` dựa trên chỉ số hàng/cột trong ma trận, giúp việc in kết quả trực quan và dễ quan sát hơn so với dùng chỉ số `0, 1, 2,…`. Việc gán nhãn và tạo bảng ánh xạ tên đỉnh → chỉ số được thực hiện như sau:

```python
G = read_adjacency_matrix("graph.txt")
n = len(G)
if n > 26:
    raise ValueError("Ví dụ này chỉ đặt tên đỉnh từ A–Z, tối đa 26 đỉnh.")

node = string.ascii_uppercase[:n]   # "A", "B", "C", ...
t_ = {}
for i in range(len(G)):
    t_[node[i]] = i                 # ví dụ: 'A' -> 0, 'B' -> 1, ...
```

### 3. Tính bậc và sắp xếp đỉnh theo bậc giảm dần

Để cải thiện chất lượng tô màu, chương trình không tô màu các đỉnh theo thứ tự tự nhiên mà sắp xếp lại thứ tự xử lý dựa trên **bậc của đỉnh**. Cụ thể, với mỗi đỉnh `i`, bậc của nó được tính bằng tổng các phần tử trên hàng `i` của ma trận kề – tức là số lượng đỉnh kề trực tiếp với đỉnh đó.

Sau khi có bậc của tất cả các đỉnh, chương trình sắp xếp các đỉnh theo thứ tự bậc giảm dần. Ý tưởng trực giác là: những đỉnh có bậc lớn (kết nối với nhiều đỉnh khác) nên được tô màu trước, vì chúng bị ràng buộc nhiều hơn và khó lựa chọn màu hơn.

```python
# Tính bậc của từng đỉnh
degree = []
for i in range(len(G)):
    degree.append(sum(G[i]))

# Sắp xếp các đỉnh theo thứ tự bậc giảm dần (dùng selection sort đơn giản)
sortedNode = []
indeks = []
for i in range(len(degree)):
    _max = -1
    for j in range(len(degree)):
        if j not in indeks:
            if degree[j] > _max:
                _max = degree[j]
                idx = j
    indeks.append(idx)
    sortedNode.append(node[idx])
```

### 4. Thuật toán tô màu tham lam

Thuật toán tô màu sử dụng trong bài là **thuật toán tham lam (greedy)**. Trước hết, chương trình xây dựng một danh sách các màu có thể sử dụng, ví dụ như `"Blue"`, `"Red"`, `"Yellow"`, `"Green"`. Đối với mỗi đỉnh, ban đầu ta cho rằng tất cả các màu đều còn khả dụng, được lưu trong `colorDict`.

Chương trình duyệt các đỉnh theo thứ tự đã sắp xếp ở trên (`sortedNode`). Với mỗi đỉnh đang xét, chương trình lấy danh sách các màu còn khả dụng của đỉnh đó và chọn màu **đầu tiên** trong danh sách để gán cho đỉnh. Sau khi một đỉnh được gán một màu cụ thể, chương trình duyệt qua hàng tương ứng trong ma trận kề, tìm tất cả các đỉnh kề với nó và **loại bỏ màu vừa gán** khỏi danh sách màu khả dụng của các đỉnh kề này.

```python
# Khởi tạo danh sách màu khả dụng cho từng đỉnh
colorDict = {}
for i in range(len(G)):
    colorDict[node[i]] = ["Blue", "Red", "Yellow", "Green"]

theSolution = {}
for n_ in sortedNode:
    setTheColor = colorDict[n_]       # danh sách màu còn dùng được của đỉnh n_
    # chọn màu đầu tiên còn lại
    theSolution[n_] = setTheColor[0]

    # cấm màu này ở các đỉnh kề
    adjacentNode = G[t_[n_]]          # hàng tương ứng trong ma trận kề
    for j in range(len(adjacentNode)):
        if adjacentNode[j] == 1 and (setTheColor[0] in colorDict[node[j]]):
            colorDict[node[j]].remove(setTheColor[0])
```

Nhờ cách “cấm màu” này, khi đến lượt các đỉnh kề được tô màu, thuật toán sẽ không chọn lại màu đã bị cấm, đảm bảo ràng buộc **“hai đỉnh kề nhau không cùng màu”**. Quy trình trên tiếp tục lặp cho đến khi tất cả các đỉnh trong đồ thị đều được gán màu.

Kết quả cuối cùng được lưu trong một cấu trúc ánh xạ từ tên đỉnh (`A, B, C, …`) sang màu tương ứng. Khi in ra màn hình, chương trình lần lượt liệt kê từng đỉnh cùng với màu đã gán, ví dụ:

```python
print("Kết quả tô màu đồ thị đọc từ file", filename)
for t, w in sorted(theSolution.items()):
    print("Đỉnh", t, "=", w)
```

---

## Bài 2. Cải tiến chương trình tô màu đồ thị và trực quan hóa kết quả

So với Bài 1, Bài 2 vẫn giải quyết cùng một bài toán: tô màu các đỉnh của một đồ thị vô hướng dựa trên ma trận kề, sao cho không có hai đỉnh kề nhau nào được gán cùng một màu. Tuy nhiên, ở bài này chương trình được cải tiến theo hai hướng chính:

1. **Tổ chức lại cấu trúc mã nguồn theo dạng hàm.**
2. **Bổ sung phần trực quan hóa đồ thị bằng hình vẽ.**

### 1. Cải tiến về cấu trúc chương trình

Trong Bài 1, hầu hết các bước xử lý – từ đọc dữ liệu, tính bậc, sắp xếp đỉnh cho tới tô màu và in kết quả – đều được viết liền trong phần chương trình chính. Điều này tuy vẫn hoạt động đúng, nhưng khi chương trình dài lên sẽ khó theo dõi, khó tái sử dụng và khó mở rộng.

Ở Bài 2, mã nguồn được **tách thành nhiều hàm riêng biệt**, mỗi hàm đảm nhận một nhiệm vụ rõ ràng, chẳng hạn như:

* Hàm đọc ma trận kề từ file.
* Hàm sinh tên các đỉnh `A, B, C, …`.
* Hàm tính bậc của từng đỉnh.
* Hàm sắp xếp đỉnh theo thứ tự bậc giảm dần.
* Hàm thực hiện thuật toán tô màu tham lam.
* Hàm in kết quả ra màn hình.
* Hàm vẽ đồ thị.

Nhờ cách tổ chức này, luồng xử lý trong `main` trở nên rất gọn: chỉ còn là chuỗi lời gọi hàm theo đúng logic **“đọc dữ liệu → xử lý → hiển thị kết quả”**.

Việc tách hàm mang lại nhiều lợi ích:

* **Dễ đọc, dễ hiểu:** mỗi khối lệnh đều có tên ý nghĩa, chỉ cần nhìn tên hàm là có thể đoán chức năng.
* **Dễ bảo trì:** khi muốn chỉnh sửa cách tính bậc, cách sắp xếp hay cách tô màu, chỉ cần sửa trong hàm tương ứng, không ảnh hưởng đến các phần khác.
* **Dễ tái sử dụng:** các hàm như đọc ma trận kề, tính bậc đỉnh,… có thể dùng lại cho các bài tập khác liên quan đến đồ thị mà không cần viết lại từ đầu.

Nhờ đó, Bài 2 không chỉ giữ nguyên kết quả đúng của thuật toán tô màu, mà còn nâng chất lượng mã nguồn theo hướng “mô-đun hóa”, phù hợp với phong cách lập trình tốt trong các bài toán lớn hơn.

### 2. Trực quan hóa kết quả tô màu bằng đồ thị

Một điểm nổi bật khác trong Bài 2 là việc **bổ sung phần vẽ hình minh họa cho đồ thị**. Thay vì chỉ in ra màn hình các dòng dạng “Đỉnh A = blue, Đỉnh B = red,…”, chương trình sử dụng thư viện `networkx` kết hợp với `matplotlib` để xây dựng và hiển thị đồ thị một cách trực quan.

Cụ thể, sau khi đã có ma trận kề `G` và danh sách tên đỉnh `nodes`, chương trình tạo một đối tượng đồ thị vô hướng `G_nx` của `networkx`, thêm các đỉnh và các cạnh dựa trên ma trận kề, sau đó vẽ đồ thị và **tô màu các đỉnh theo kết quả tô màu** của thuật toán tham lam. Phần này được đóng gói trong hàm `draw_graph`:

```python
def draw_graph(G, nodes, solution=None, save_path=None):

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
```

Dựa trên `save_path`, chương trình có thể lưu hình ra file (ví dụ `graph_colored.png`) để chèn vào báo cáo hoặc slide thuyết trình. Nhờ việc trực quan hóa kết quả, việc kiểm tra tính đúng đắn của thuật toán trở nên trực quan hơn: chỉ cần nhìn vào hình vẽ để xem các đỉnh kề nhau đã được tô màu khác nhau hay chưa.

---

## Bài 3. Cài đặt thuật toán người bán hàng và ứng dụng tìm chu trình qua n thành phố, mỗi thành phố qua 1 lần với chi phí tối thiểu

Trong bài toán này, chương trình cài đặt **thuật toán người bán hàng** (Traveling Salesman Problem – TSP) để tìm một **chu trình đi qua n thành phố**, mỗi thành phố được thăm **chính xác một lần**, sau đó quay trở về thành phố xuất phát sao cho **tổng chi phí di chuyển là nhỏ nhất**.

Dữ liệu đầu vào của bài toán là **ma trận chi phí** giữa các cặp thành phố, được lưu trong một tệp văn bản (ví dụ `tsp.txt`). Mỗi dòng trong tệp biểu diễn chi phí đi từ một thành phố `i` đến các thành phố `j` còn lại, các giá trị cách nhau bằng dấu cách. Phần tử `cost[i][j]` trong ma trận thể hiện chi phí (hoặc khoảng cách) khi đi trực tiếp từ thành phố `i` sang thành phố `j`.

Sau khi đọc ma trận này và kiểm tra tính vuông (số dòng bằng số cột), chương trình áp dụng giải thuật **quay lui (backtracking)** để duyệt các chu trình có thể, từ đó tìm ra chu trình thỏa mãn yêu cầu đề bài: **đi qua mỗi thành phố đúng một lần và có tổng chi phí nhỏ nhất**.

### 1. Đọc ma trận chi phí từ file

Phần đọc dữ liệu được tách thành một hàm riêng `read_cost_matrix`. Hàm này chịu trách nhiệm mở file, đọc từng dòng, tách các số theo dấu cách và chuyển sang kiểu `float`, đồng thời kiểm tra điều kiện ma trận vuông (số phần tử trên mỗi dòng phải bằng số dòng của file). Nếu ma trận không vuông, chương trình báo lỗi:

```python
import math

def read_cost_matrix(filename):
    
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
```

Nhờ việc tách hàm, phần chương trình chính chỉ cần gọi `read_cost_matrix("tsp.txt")` để thu được ma trận chi phí phục vụ cho thuật toán TSP.

### 2. Cài đặt thuật toán người bán hàng bằng quay lui

Giải thuật quay lui được sử dụng để duyệt tất cả các chu trình có thể đi qua `n` thành phố. Ý tưởng cơ bản như sau:

* Chọn một thành phố xuất phát (trong chương trình mặc định là thành phố `0`).
* Từ thành phố hiện tại, lần lượt thử đi đến các thành phố chưa được thăm.
* Mỗi khi đã đi qua đủ `n` thành phố, cộng thêm chi phí quay về thành phố xuất phát để tạo thành một chu trình đầy đủ.
* So sánh tổng chi phí của chu trình vừa tìm được với chi phí tốt nhất đang lưu, nếu nhỏ hơn thì cập nhật lời giải tối ưu.
* Trong quá trình duyệt, sử dụng **cắt tỉa (pruning)**: nếu chi phí tạm thời của đường đi hiện tại đã lớn hơn hoặc bằng chi phí tốt nhất tìm được trước đó thì dừng việc mở rộng nhánh này (vì chắc chắn không thể cho lời giải tốt hơn).

Các bước trên được hiện thực trong hàm `tsp_backtracking`:

```python
def tsp_backtracking(cost, start=0):
    
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
```

Trong đó:

* `visited[i]` dùng để đánh dấu xem thành phố `i` đã được đi qua hay chưa, đảm bảo **mỗi thành phố chỉ được thăm đúng một lần**.
* `path` lưu đường đi hiện tại (danh sách chỉ số thành phố theo thứ tự).
* `best_cost` và `best_path` lưu lại **chu trình tối ưu** tìm được cho đến thời điểm hiện tại.
* Hàm con `backtrack` thực hiện công việc duyệt đệ quy và quay lui, đồng thời áp dụng điều kiện cắt tỉa để giảm bớt số nhánh phải xét.

### 3. Chương trình chính và kết quả

Phần chương trình chính (`main`) điều phối toàn bộ luồng xử lý: đọc dữ liệu, in ma trận chi phí, gọi thuật toán TSP và in kết quả chu trình tối ưu ra màn hình:

```python
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
```

Chu trình tối ưu được in ra dưới dạng **chỉ số đỉnh**, ví dụ:

```text
0 -> 2 -> 3 -> 1 -> 0
```

tương ứng với thứ tự các thành phố trong ma trận chi phí. Tổng chi phí là tổng các `cost[i][j]` trên các cung của chu trình này (bao gồm cả cung quay về thành phố xuất phát), đúng với yêu cầu: **“mỗi thành phố qua 1 lần với chi phí tối thiểu”**.

### 4. Nhận xét

Ưu điểm của phương pháp này là:

* Dễ hiểu, bám sát đúng phát biểu bài toán.
* Cho kết quả chính xác (chu trình tối ưu thật sự) với những bộ dữ liệu có số lượng thành phố không quá lớn.

Nhược điểm là độ phức tạp tính toán tăng rất nhanh khi số thành phố `n` tăng, do số hoán vị cần xét là `(n − 1)!`; do đó, trong thực tế thuật toán quay lui thường chỉ dùng cho các bài toán **quy mô nhỏ**, như trong bài thực hành này, còn với `n` rất lớn người ta dùng các phương pháp **xấp xỉ hoặc heuristic** (tham lam, nhánh cận nâng cao, di truyền, mô phỏng tôi luyện, v.v.).

---

## Bài 4 (BTVN). Cài đặt giải thuật di truyền và ứng dụng vào bài toán sắp lịch dạy môn Toán và Tin học cho các giáo viên ở bậc PTTH trong 1 tuần

Trong bài này, chương trình sử dụng **giải thuật di truyền** (Genetic Algorithm – GA) để sắp xếp **thời khóa biểu** cho ba lớp 10A1, 10A2, 10A3 trong một tuần, với các môn cần xếp là **Toán** và **Tin học**. Bài toán được mô hình hóa đơn giản như sau:

* Thời gian: 5 ngày (thứ Hai đến thứ Sáu), mỗi ngày 4 tiết → tổng cộng **20 slot / lớp**.
* Có 3 lớp: 10A1, 10A2, 10A3 → tổng số slot cần xem xét: `3 × 20 = 60` slot.
* Có 2 giáo viên Toán (`Toan1`, `Toan2`) và 1 giáo viên Tin (`Tin1`).
* Mỗi lớp cần có **4 tiết Toán** và **2 tiết Tin** trong tuần.
* Một giáo viên **không được dạy hai lớp cùng một thời điểm**.

Giải thuật di truyền được sử dụng để tìm ra một thời khóa biểu thỏa mãn càng nhiều ràng buộc càng tốt (số tiết đúng, không trùng giáo viên), thông qua việc **mã hóa thời khóa biểu thành nhiễm sắc thể (chromosome)** và tiến hóa qua nhiều thế hệ.

### 1. Mã hoá thời khóa biểu thành nhiễm sắc thể

Đầu tiên là phần cấu hình bài toán:

```python
NUM_DAYS = 5            # Thứ 2..Thứ 6
PERIODS_PER_DAY = 4     # 4 tiết / ngày
NUM_CLASSES = 3         # 3 lớp: 10A1, 10A2, 10A3

NUM_SLOTS = NUM_DAYS * PERIODS_PER_DAY        # 20 slot / lớp
CHROMO_LEN = NUM_CLASSES * NUM_SLOTS          # 60 gene
```

* `NUM_SLOTS = 20`: mỗi lớp có 20 ô (5 ngày × 4 tiết).
* `CHROMO_LEN = 60`: 3 lớp × 20 = 60 ô → **1 nhiễm sắc thể = lịch dạy cho cả 3 lớp trong tuần**.

Mỗi ô (gene) mang 1 con số, ý nghĩa:

```python
# 0 = trống (không học)
# 1 = Toán - GV_Toan1 (teacher_id = 0)
# 2 = Toán - GV_Toan2 (teacher_id = 1)
# 3 = Tin  - GV_Tin1  (teacher_id = 2)
TEACHER_OF_GENE = {
    0: None,
    1: 0,
    2: 1,
    3: 2
}

SUBJECT_OF_GENE = {
    0: None,
    1: "Toan",
    2: "Toan",
    3: "Tin"
}
TEACHER_NAME = {
    0: "Toan1",
    1: "Toan2",
    2: "Tin1"
}
```

Hiểu như sau:

* Gene = 1 → “tiết này lớp đó học Toán với thầy Toan1”.
* Gene = 2 → “tiết này lớp đó học Toán với thầy Toan2”.
* Gene = 3 → “tiết này lớp đó học Tin với thầy Tin1”.
* Gene = 0 → slot trống (không có tiết).

Một nhiễm sắc thể (**chromosome**) là list 60 số thuộc `{0,1,2,3}`, mô tả đầy đủ TKB tuần cho 3 lớp.

Sinh một nhiễm sắc thể ngẫu nhiên:

```python
def make_random_chromosome():

    genes = []
    for _ in range(CHROMO_LEN):
        genes.append(random.choice([0, 1, 2, 3]))
    return genes
```

Nghĩa là ban đầu GA sẽ **đoán ngẫu nhiên** nhiều thời khóa biểu, sau đó dùng **fitness** để chấm điểm, chọn lịch tốt, lai – đột biến để dần dần “tiến hóa” ra lịch đẹp hơn.

### 2. Hàm fitness – chấm điểm 1 thời khóa biểu

Đây là “trái tim” của bài toán: một lịch có “hợp lý” hay không nằm ở đây.

```python
def compute_fitness(chrom):
    """
    Fitness càng cao càng tốt.
    Ta bắt đầu từ điểm cơ sở rồi trừ dần theo số lỗi.
    """
    penalty = 0
```

Ý tưởng:

* Cho mỗi TKB một điểm cơ bản `base_score = 1000`.
* Mỗi lỗi vi phạm → cộng `penalty` → càng nhiều lỗi thì fitness càng thấp.
* Cuối cùng: `fitness = base_score - penalty`.

#### 2.1. Ràng buộc số tiết Toán/Tin cho từng lớp

```python
    for c_idx in range(NUM_CLASSES):
        math_count = 0
        cs_count = 0
        # quét tất cả slot của lớp này
        for slot in range(NUM_SLOTS):
            gene = chrom[c_idx * NUM_SLOTS + slot]
            subj = SUBJECT_OF_GENE[gene]
            if subj == "Toan":
                math_count += 1
            elif subj == "Tin":
                cs_count += 1

        # phạt nếu sai lệch so với yêu cầu
        penalty += abs(math_count - REQUIRED_MATH) * 5
        penalty += abs(cs_count - REQUIRED_CS) * 5
```

* `c_idx * NUM_SLOTS + slot` → nhảy tới đúng đoạn 20 gene của lớp `c_idx`.
* Đếm số tiết Toán (`math_count`) và số tiết Tin (`cs_count`) của lớp đó.
* Yêu cầu: `REQUIRED_MATH = 4`, `REQUIRED_CS = 2`.
* Nếu lệch, ví dụ có 6 tiết Toán → lệch 2 → phạt `2 * 5 = 10`.

=> TKB nào có đúng 4 Toán, 2 Tin sẽ **được lợi** so với lịch bị lệch.

#### 2.2. Ràng buộc giáo viên không dạy 2 lớp cùng giờ

```python
    for slot in range(NUM_SLOTS):
        # đếm giáo viên nào xuất hiện bao nhiêu lần trong slot này
        teacher_count = {0: 0, 1: 0, 2: 0}
        for c_idx in range(NUM_CLASSES):
            gene = chrom[c_idx * NUM_SLOTS + slot]
            t_id = TEACHER_OF_GENE[gene]
            if t_id is not None:
                teacher_count[t_id] += 1

        # nếu giáo viên xuất hiện > 1 trong cùng slot => bị trùng
        for t_id, cnt in teacher_count.items():
            if cnt > 1:
                penalty += (cnt - 1) * 20  # phạt nặng
```

* Ở đây `slot` chạy từ `0..19` → tương ứng **tiết (day, period) giống nhau** cho cả 3 lớp.
* Với mỗi slot, ta xem:

  * Lớp 10A1 học gì?
  * Lớp 10A2 học gì?
  * Lớp 10A3 học gì?
* Đếm xem thầy nào dạy mấy lớp cùng lúc.

  * Nếu thầy `Toan1` bị xếp dạy 2 lớp cùng tiết → vi phạm → phạt `+20` (phạt nặng hơn lệch số tiết).

Cuối cùng:

```python
    base_score = 1000
    fitness = base_score - penalty
    return fitness
```

Kết luận:

* **Fitness cao** = ít lỗi = lịch đẹp.
* **Fitness thấp** = nhiều lỗi = lịch tệ.

### 3. Các toán tử GA: chọn, lai, đột biến

#### 3.1. Chọn (selection) – tournament

```python
def tournament_selection(population, fitnesses):
    """
    Chọn 1 cá thể bằng tournament selection.
    """
    best_idx = None
    for _ in range(TOURNAMENT_SIZE):
        i = random.randrange(len(population))
        if best_idx is None or fitnesses[i] > fitnesses[best_idx]:
            best_idx = i
    return population[best_idx][:]  # copy
```

* `population`: danh sách các TKB.
* `fitnesses`: điểm của từng TKB.
* `TOURNAMENT_SIZE = 3`:

  * Random 3 lịch, lấy cái nào fitness cao nhất.
  * Có “cạnh tranh”, lịch đẹp có cơ hội được chọn lớn hơn.

#### 3.2. Lai (crossover) – ghép 2 lịch lại

```python
def crossover(parent1, parent2):
    """
    Lai ghép 1 điểm cắt.
    """
    if random.random() > CROSSOVER_RATE:
        return parent1[:], parent2[:]

    point = random.randint(1, CHROMO_LEN - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2
```

* Chọn 1 điểm cắt trong `[1..CHROMO_LEN-1]`.
* Con 1: nửa đầu của bố 1 + nửa sau của bố 2.
* Con 2: ngược lại.

→ Hy vọng tự nhiên ghép ra lịch đẹp hơn (thừa hưởng phần tốt của bố/mẹ).

#### 3.3. Đột biến (mutation) – chỉnh gene lặt vặt

```python
def mutate(chrom):
    """
    Đột biến: với xác suất MUTATION_RATE, đổi gene thành giá trị khác.
    """
    for i in range(CHROMO_LEN):
        if random.random() < MUTATION_RATE:
            chrom[i] = random.choice([0, 1, 2, 3])
```

* Mỗi gene có xác suất 2% bị đổi sang 0/1/2/3 khác.
  → Giúp quần thể không bị “mắc kẹt” ở một vùng nghiệm, tạo cơ hội nảy ra lịch mới hay hơn.

### 4. Vòng lặp GA – tiến hóa qua nhiều thế hệ

```python
def run_ga():
    # Khởi tạo quần thể
    population = [make_random_chromosome() for _ in range(POP_SIZE)]
    fitnesses = [compute_fitness(ch) for ch in population]

    best_chrom = None
    best_fitness = float("-inf")

    for gen in range(NUM_GENERATIONS):
        # Cập nhật best
        for ch, fit in zip(population, fitnesses):
            if fit > best_fitness:
                best_fitness = fit
                best_chrom = ch[:]

        print(f"Gen {gen}: best_fitness = {best_fitness}")

        # Tạo quần thể mới (elitism: giữ lại 1 con tốt nhất)
        new_population = [best_chrom[:]]

        while len(new_population) < POP_SIZE:
            p1 = tournament_selection(population, fitnesses)
            p2 = tournament_selection(population, fitnesses)
            c1, c2 = crossover(p1, p2)
            mutate(c1)
            mutate(c2)
            new_population.append(c1)
            if len(new_population) < POP_SIZE:
                new_population.append(c2)

        population = new_population
        fitnesses = [compute_fitness(ch) for ch in population]

    return best_chrom, best_fitness
```

Luồng:

1. Giữ lại 1 lịch tốt nhất (**elitism**) → không bị mất lời giải tốt.
2. Lặp đến khi đủ `POP_SIZE` cá thể:

   * Chọn 2 “bố mẹ” bằng tournament.
   * Lai → sinh 2 “con”.
   * Đột biến nhẹ.
   * Thêm vào quần thể mới.
3. Sau khi tạo xong quần thể mới → tính lại `fitness` → sang thế hệ tiếp theo.

Lặp lại `NUM_GENERATIONS = 200` lần → lịch dần dần đẹp lên (fitness tăng).




