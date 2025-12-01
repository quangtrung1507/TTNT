from math import inf
import tkinter as tk
from tkinter import messagebox

EMPTY = "."
PLAYER_X = "X"
PLAYER_O = "O"

# Bán kính lân cận để sinh nước đi
MOVE_RADIUS = 1

# Trọng số cho chuỗi 1..5 quân liên tiếp
WEIGHTS = {
    1: 1,
    2: 8,
    3: 40,
    4: 200,
    5: 10000,
}


class Board:
    def __init__(self, n: int):
        self.n = n
        self.grid = [[EMPTY for _ in range(n)] for _ in range(n)]
        # Quy định độ dài thắng theo N
        if n <= 3:
            self.win_len = 3
        elif n == 4:
            self.win_len = 4
        else:
            self.win_len = 5

    def clone(self):
        b = Board(self.n)
        b.win_len = self.win_len
        b.grid = [row[:] for row in self.grid]
        return b

    def is_empty(self) -> bool:
        return all(cell == EMPTY for row in self.grid for cell in row)

    def make_move(self, i: int, j: int, player: str):
        self.grid[i][j] = player

    def undo_move(self, i: int, j: int):
        self.grid[i][j] = EMPTY

    def in_bounds(self, i: int, j: int) -> bool:
        return 0 <= i < self.n and 0 <= j < self.n

    def get_winner(self):
        """Kiểm tra người thắng theo self.win_len."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == EMPTY:
                    continue
                player = self.grid[i][j]
                for di, dj in directions:
                    count = 1
                    x, y = i + di, j + dj
                    while self.in_bounds(x, y) and self.grid[x][y] == player:
                        count += 1
                        if count >= self.win_len:
                            return player
                        x += di
                        y += dj
        return None

    def is_full(self) -> bool:
        return all(cell != EMPTY for row in self.grid for cell in row)

    def is_terminal(self) -> bool:
        return self.get_winner() is not None or self.is_full()


def get_opponent(player: str) -> str:
    return PLAYER_O if player == PLAYER_X else PLAYER_X


def generate_moves(board: Board, radius: int = MOVE_RADIUS):
    """
    Sinh nước đi ứng cử viên với vùng lân cận.
    """
    n = board.n
    moves = set()

    if board.is_empty():
        mid = n // 2
        for di in range(-1, 2):
            for dj in range(-1, 2):
                x, y = mid + di, mid + dj
                if board.in_bounds(x, y) and board.grid[x][y] == EMPTY:
                    moves.add((x, y))
        return list(moves)

    for i in range(n):
        for j in range(n):
            if board.grid[i][j] != EMPTY:
                for di in range(-radius, radius + 1):
                    for dj in range(-radius, radius + 1):
                        x, y = i + di, j + dj
                        if board.in_bounds(x, y) and board.grid[x][y] == EMPTY:
                            moves.add((x, y))

    return list(moves)


def get_all_lines(board: Board):
    """
    Lấy tất cả các line (hàng, cột, chéo) có độ dài >= win_len.
    """
    n = board.n
    L = board.win_len
    lines = []

    # Hàng ngang
    for i in range(n):
        if n >= L:
            lines.append(board.grid[i][:])

    # Hàng dọc
    for j in range(n):
        if n >= L:
            col = [board.grid[i][j] for i in range(n)]
            lines.append(col)

    # Chéo chính (i - j = const)
    for d in range(-n + 1, n):
        diag = []
        for i in range(n):
            j = i - d
            if 0 <= j < n:
                diag.append(board.grid[i][j])
        if len(diag) >= L:
            lines.append(diag)

    # Chéo phụ (i + j = const)
    for s in range(0, 2 * n - 1):
        diag = []
        for i in range(n):
            j = s - i
            if 0 <= j < n:
                diag.append(board.grid[i][j])
        if len(diag) >= L:
            lines.append(diag)

    return lines


def evaluate_line(line, player: str, win_len: int) -> int:
    """
    Tính điểm cho 'player' trên một line (list các ô).
    """
    score = 0
    length = len(line)
    opp = get_opponent(player)

    for start in range(0, length - win_len + 1):
        window = line[start:start + win_len]
        if player in window and opp in window:
            continue

        count_p = window.count(player)
        if count_p == 0:
            continue

        if count_p >= win_len:
            score += WEIGHTS.get(win_len, WEIGHTS[5])
        else:
            score += WEIGHTS.get(count_p, 0)

    return score


def evaluate(board: Board, player: str) -> int:
    """
    Heuristic: score(player) - score(opponent).
    """
    winner = board.get_winner()
    opp = get_opponent(player)
    if winner == player:
        return WEIGHTS.get(board.win_len, WEIGHTS[5]) * 10
    elif winner == opp:
        return -WEIGHTS.get(board.win_len, WEIGHTS[5]) * 10

    lines = get_all_lines(board)
    my_score = 0
    opp_score = 0

    for line in lines:
        my_score += evaluate_line(line, player, board.win_len)
        opp_score += evaluate_line(line, opp, board.win_len)

    return my_score - opp_score


def minimax(board: Board, depth: int, maximizing_player: bool, player: str):
    """
    Minimax với depth giới hạn.
    """
    if depth == 0 or board.is_terminal():
        return evaluate(board, player), None

    current_player = player if maximizing_player else get_opponent(player)
    moves = generate_moves(board)

    if not moves:
        return evaluate(board, player), None

    if maximizing_player:
        best_value = -inf
        best_move = None
        for (i, j) in moves:
            board.make_move(i, j, current_player)
            value, _ = minimax(board, depth - 1, False, player)
            board.undo_move(i, j)
            if value > best_value:
                best_value = value
                best_move = (i, j)
        return best_value, best_move
    else:
        best_value = inf
        best_move = None
        for (i, j) in moves:
            board.make_move(i, j, current_player)
            value, _ = minimax(board, depth - 1, True, player)
            board.undo_move(i, j)
            if value < best_value:
                best_value = value
                best_move = (i, j)
        return best_value, best_move


def order_moves(board: Board, moves, player: str):
    """
    Sắp xếp nước đi để alpha-beta cắt tỉa tốt hơn.
    """
    scored = []
    for (i, j) in moves:
        board.make_move(i, j, player)
        score = evaluate(board, player)
        board.undo_move(i, j)
        scored.append((score, (i, j)))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [m for _, m in scored]


def alphabeta(board: Board, depth: int, alpha: float, beta: float,
              maximizing_player: bool, player: str):
    """
    Alpha-beta pruning.
    """
    if depth == 0 or board.is_terminal():
        return evaluate(board, player), None

    current_player = player if maximizing_player else get_opponent(player)
    moves = generate_moves(board)

    if not moves:
        return evaluate(board, player), None

    moves = order_moves(board, moves, current_player)

    if maximizing_player:
        best_value = -inf
        best_move = None
        for (i, j) in moves:
            board.make_move(i, j, current_player)
            value, _ = alphabeta(board, depth - 1, alpha, beta, False, player)
            board.undo_move(i, j)
            if value > best_value:
                best_value = value
                best_move = (i, j)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return best_value, best_move
    else:
        best_value = inf
        best_move = None
        for (i, j) in moves:
            board.make_move(i, j, current_player)
            value, _ = alphabeta(board, depth - 1, alpha, beta, True, player)
            board.undo_move(i, j)
            if value < best_value:
                best_value = value
                best_move = (i, j)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return best_value, best_move


def choose_depth(n: int, algo: str) -> int:
    """
    Chọn depth dựa theo kích thước bàn và loại thuật toán.
    """
    if algo == "minimax":
        if n <= 4:
            return 5
        elif n <= 7:
            return 4
        elif n <= 10:
            return 3
        else:
            return 2
    else:  # alphabeta
        if n <= 4:
            return 6
        elif n <= 7:
            return 5
        elif n <= 10:
            return 4
        else:
            return 3


def choose_best_move(board: Board, player: str, algo: str = "alphabeta"):
    depth = choose_depth(board.n, algo)
    if algo == "minimax":
        value, move = minimax(board, depth, True, player)
    else:
        value, move = alphabeta(board, depth, -inf, inf, True, player)
    return value, move


# ===================== GUI BASIC VỚI TKINTER =====================

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TicTacToe NxN - Minimax / Alpha-Beta")

        # Khung cấu hình
        config_frame = tk.Frame(root)
        config_frame.pack(pady=10)

        tk.Label(config_frame, text="N:").grid(row=0, column=0, padx=5)
        self.n_var = tk.StringVar(value="10")
        self.n_entry = tk.Entry(config_frame, width=5, textvariable=self.n_var)
        self.n_entry.grid(row=0, column=1, padx=5)

        tk.Label(config_frame, text="Algorithm:").grid(row=0, column=2, padx=5)
        self.algo_var = tk.StringVar(value="alphabeta")
        algo_menu = tk.OptionMenu(config_frame, self.algo_var, "minimax", "alphabeta")
        algo_menu.grid(row=0, column=3, padx=5)

        self.start_button = tk.Button(config_frame, text="Start Game", command=self.start_game)
        self.start_button.grid(row=0, column=4, padx=10)

        # Khung status
        self.status_var = tk.StringVar(value="Nhập N và chọn thuật toán, rồi bấm Start Game")
        status_label = tk.Label(root, textvariable=self.status_var)
        status_label.pack(pady=5)

        # Khung bàn cờ
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        # Các biến game
        self.board = None
        self.buttons = []
        self.ai_player = PLAYER_X
        self.human_player = PLAYER_O
        self.current = PLAYER_X
        self.game_over = False

    def clear_board_frame(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.buttons = []

    def start_game(self):
        # Đọc N
        try:
            n = int(self.n_var.get())
            if n < 3:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "N phải là số nguyên >= 3")
            return

        # Cảnh báo N quá to (giao diện sẽ rất rộng)
        if n > 15:
            if not messagebox.askyesno(
                "Cảnh báo",
                "N > 15 sẽ làm giao diện rất lớn, bạn vẫn muốn tiếp tục?"
            ):
                return

        self.board = Board(n)
        self.current = PLAYER_X
        self.game_over = False

        self.clear_board_frame()

        # Tạo lưới button
        self.buttons = []
        for i in range(n):
            row_btns = []
            for j in range(n):
                btn = tk.Button(
                    self.board_frame,
                    text=".",
                    width=2,
                    height=1,
                    font=("Consolas", 14),
                    command=lambda i=i, j=j: self.on_cell_click(i, j)
                )
                btn.grid(row=i, column=j)
                row_btns.append(btn)
            self.buttons.append(row_btns)

        self.status_var.set(
            f"Bàn {n}x{n}, thắng {self.board.win_len}. AI: X (đi trước), Bạn: O."
        )

        # Cho AI đi trước luôn (X)
        self.root.after(200, self.ai_move)

    def on_cell_click(self, i, j):
        if self.board is None or self.game_over:
            return
        if self.current != self.human_player:
            return
        if not self.board.in_bounds(i, j) or self.board.grid[i][j] != EMPTY:
            return

        # Người đánh
        self.board.make_move(i, j, self.human_player)
        self.update_button(i, j)
        self.check_game_state()

        if not self.game_over:
            self.current = self.ai_player
            self.status_var.set("Lượt AI suy nghĩ...")
            self.root.after(200, self.ai_move)

    def ai_move(self):
        if self.board is None or self.game_over:
            return
        if self.current != self.ai_player:
            return

        # Tính nước đi
        _, move = choose_best_move(self.board, self.ai_player, algo=self.algo_var.get())
        if move is None:
            # Không còn nước đi
            self.status_var.set("Không còn nước đi. Hòa!")
            self.game_over = True
            return

        i, j = move
        self.board.make_move(i, j, self.ai_player)
        self.update_button(i, j)

        self.check_game_state()

        if not self.game_over:
            self.current = self.human_player
            self.status_var.set("Lượt bạn (O). Click vào ô để đánh.")

    def update_button(self, i, j):
        if self.buttons:
            self.buttons[i][j]["text"] = self.board.grid[i][j]

    def check_game_state(self):
        winner = self.board.get_winner()
        if winner is not None:
            if winner == self.ai_player:
                self.status_var.set("AI thắng!")
                messagebox.showinfo("Kết quả", "AI thắng!")
            else:
                self.status_var.set("Bạn thắng!")
                messagebox.showinfo("Kết quả", "Bạn thắng!")
            self.game_over = True
            return

        if self.board.is_full():
            self.status_var.set("Hòa!")
            messagebox.showinfo("Kết quả", "Hòa!")
            self.game_over = True


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()
