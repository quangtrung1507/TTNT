import random

# ================== CẤU HÌNH BÀI TOÁN ==================

NUM_DAYS = 5            # Thứ 2..Thứ 6
PERIODS_PER_DAY = 4     # 4 tiết / ngày
NUM_CLASSES = 3         # 3 lớp: 10A1, 10A2, 10A3

NUM_SLOTS = NUM_DAYS * PERIODS_PER_DAY        # 20 slot / lớp
CHROMO_LEN = NUM_CLASSES * NUM_SLOTS          # 60 gene

# Mã hóa gene:
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
# Môn học (không gắn thầy ở đây, chỉ để đếm số tiết)
SUBJECT_OF_GENE = {
    0: None,
    1: "Toan",
    2: "Toan",
    3: "Tin"
}
# Tên giáo viên để in ra
TEACHER_NAME = {
    0: "Toan1",   # GV Toán 1
    1: "Toan2",   # GV Toán 2
    2: "Tin1"     # GV Tin 1
}

CLASSES = ["10A1", "10A2", "10A3"]
DAYS = ["T2", "T3", "T4", "T5", "T6"]

# Yêu cầu số tiết / tuần / lớp
REQUIRED_MATH = 4
REQUIRED_CS = 2

# ================== THAM SỐ GA ==================

POP_SIZE = 50
NUM_GENERATIONS = 200
TOURNAMENT_SIZE = 3
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.02


# ================== HÀM TIỆN ÍCH ==================

def index_to_class_slot(idx):
    """
    Chuyển chỉ số gene -> (class_idx, day, period)
    """
    class_idx = idx // NUM_SLOTS
    slot_idx = idx % NUM_SLOTS
    day = slot_idx // PERIODS_PER_DAY
    period = slot_idx % PERIODS_PER_DAY
    return class_idx, day, period


def make_random_chromosome():
    """
    Tạo ngẫu nhiên 1 thời khóa biểu (chromosome).
    Mỗi gene = 0,1,2,3
    """
    genes = []
    for _ in range(CHROMO_LEN):
        genes.append(random.choice([0, 1, 2, 3]))
    return genes


# ================== FITNESS ==================

def compute_fitness(chrom):
    """
    Fitness càng cao càng tốt.
    Ta bắt đầu từ điểm cơ sở rồi trừ dần theo số lỗi.
    """
    penalty = 0

    # 1. Ràng buộc số tiết Toán/Tin cho từng lớp
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

    # 2. Ràng buộc GV không được dạy 2 lớp cùng giờ
    # Với mỗi timeslot (day,period), kiểm tra tất cả lớp
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

    # 3. Có thể thêm ràng buộc khác (không dồn quá nhiều tiết 1 ngày, v.v.)

    base_score = 1000
    fitness = base_score - penalty
    return fitness


# ================== CÁC TOÁN TỬ GA ==================

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


def mutate(chrom):
    """
    Đột biến: với xác suất MUTATION_RATE, đổi gene thành giá trị khác.
    """
    for i in range(CHROMO_LEN):
        if random.random() < MUTATION_RATE:
            chrom[i] = random.choice([0, 1, 2, 3])


# ================== CHẠY GA ==================

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


# ================== HÀM IN THỜI KHÓA BIỂU ==================

def print_timetable(chrom):
    for c_idx in range(NUM_CLASSES):
        print(f"\n===== Thời khóa biểu lớp {CLASSES[c_idx]} =====")
        # tạo bảng ngày x tiết
        for day in range(NUM_DAYS):
            row = []
            for period in range(PERIODS_PER_DAY):
                slot = day * PERIODS_PER_DAY + period
                gene = chrom[c_idx * NUM_SLOTS + slot]

                if gene == 0:
                    cell = "--"
                else:
                    subj = SUBJECT_OF_GENE[gene]
                    t_id = TEACHER_OF_GENE[gene]
                    if subj == "Toan":
                        # in Toan1 / Toan2 tùy giáo viên
                        cell = TEACHER_NAME[t_id]
                    else:  # Tin
                        cell = "Tin1"

                row.append(cell)
            print(f"{DAYS[day]}: " + " | ".join(f"{x:5}" for x in row))


# ================== MAIN ==================

def main():
    best_chrom, best_fit = run_ga()
    print("\n===== KẾT QUẢ TỐT NHẤT =====")
    print("Fitness:", best_fit)
    print_timetable(best_chrom)


if __name__ == "__main__":
    main()
