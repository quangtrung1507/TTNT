
# Obesity Prediction (K-Means + K-NN + GUI)

## 1. Giới thiệu & mục tiêu
Bài này xây dựng mô hình dự đoán **mức độ béo phì** dựa trên thông tin cá nhân và thói quen sinh hoạt. Khi người dùng nhập dữ liệu (tuổi, chiều cao, cân nặng, thói quen ăn uống, vận động…), hệ thống sẽ dự đoán mức độ thuộc một trong **7 lớp** từ thiếu cân đến béo phì nặng.

Trong bài mình kết hợp:
- **K-Means (không giám sát)** để phân cụm hành vi/sức khoẻ.
- **K-NN (có giám sát)** để dự đoán nhãn mức độ béo phì.

---

## 2. Nguồn dữ liệu & mô tả thuộc tính

### 2.1. Nguồn dữ liệu
Sử dụng bộ dữ liệu mức độ béo phì dạng CSV:

- `ObesityDataSet_raw_and_data_sinthetic.csv` (gồm dữ liệu gốc và dữ liệu tổng hợp trên UCI).

### 2.2. Nhãn dự đoán (Target)
- **Tên cột:** `NObeyesdad`
- **Ý nghĩa:** Mức độ cân nặng/béo phì (7 lớp):
  - `Insufficient_Weight` → Thiếu cân  
  - `Normal_Weight` → Bình thường  
  - `Overweight_Level_I` → Thừa cân mức 1  
  - `Overweight_Level_II` → Thừa cân mức 2  
  - `Obesity_Type_I` → Béo phì độ 1  
  - `Obesity_Type_II` → Béo phì độ 2  
  - `Obesity_Type_III` → Béo phì độ 3  

### 2.3. Các cột dữ liệu đầu vào (Features)

#### a) Nhóm thông tin cá nhân
- `Gender` → Giới tính
- `Age` → Tuổi
- `Height` → Chiều cao (m)
- `Weight` → Cân nặng (kg)

#### b) Nhóm tiền sử & thói quen ăn uống
- `family_history_with_overweight` → Tiền sử gia đình có thừa cân/béo phì (có/không)
- `FAVC` *(Frequent consumption of high caloric food)* → Thường xuyên ăn đồ nhiều calo (có/không)
- `FCVC` *(Frequency of consumption of vegetables)* → Tần suất ăn rau (mức độ 1–3)
- `NCP` *(Number of main meals)* → Số bữa ăn chính trong ngày
- `CAEC` *(Consumption of food between meals)* → Ăn giữa các bữa/ăn vặt (không / thỉnh thoảng / thường xuyên / luôn luôn)
- `CH2O` *(Consumption of water daily)* → Mức độ uống nước mỗi ngày (mức độ 1–3)
- `CALC` *(Consumption of alcohol)* → Mức độ uống rượu/bia (không / thỉnh thoảng / thường xuyên / luôn luôn)

#### c) Nhóm hành vi sức khoẻ & lối sống
- `SMOKE` → Hút thuốc (có/không)
- `SCC` *(Calories consumption monitoring)* → Theo dõi lượng calo nạp vào (có/không)
- `FAF` *(Physical activity frequency)* → Tần suất hoạt động thể chất/tập luyện (mức độ 0–3)
- `TUE` *(Time using technology devices)* → Thời gian sử dụng thiết bị công nghệ (mức độ 0–2)

#### d) Nhóm di chuyển
- `MTRANS` *(Transportation used)* → Phương tiện di chuyển chính (công cộng/ô tô/đi bộ/xe máy/xe đạp)

---

## 3. Làm sạch dữ liệu & chia tập Train/Test (80:20)

Thực hiện bước tiền xử lý trong file `clean_data.py` với mục tiêu:
1. Đọc dữ liệu từ file CSV gốc  
2. Làm sạch cơ bản (chuẩn hoá chuỗi, xử lý thiếu dữ liệu, loại bản ghi trùng)  
3. Chia dữ liệu thành **80% train** và **20% test** theo đúng quy tắc đánh giá mô hình

### 3.1. Đọc dữ liệu và kiểm tra cột nhãn
- Dữ liệu được đọc bằng `pd.read_csv(INPUT_CSV)`.
- Chuẩn hoá tên cột bằng:
  ```python
  df.columns = [c.strip() for c in df.columns]

để tránh lỗi do tên cột có khoảng trắng thừa.

* Kiểm tra bắt buộc phải có cột nhãn `NObeyesdad`. Nếu không có, chương trình dừng và báo lỗi để tránh train nhầm.

### 3.2. Làm sạch cơ bản (Basic cleaning)

Mình thực hiện các thao tác làm sạch sau:

**(1) Chuẩn hoá dữ liệu dạng chữ (object)**

```python
if df[c].dtype == "object":
    df[c] = df[c].astype(str).str.strip()
```

* Mục đích: loại bỏ khoảng trắng thừa ở đầu/cuối chuỗi (ví dụ `"Male "` → `"Male"`), tránh việc mô hình hiểu sai đây là hai giá trị khác nhau.

**(2) Xử lý dữ liệu số**

```python
df[c] = pd.to_numeric(df[c], errors="coerce")
```

* Mục đích: đảm bảo các cột số (Age/Height/Weight, …) đúng kiểu numeric.
* `errors="coerce"` sẽ biến các giá trị không hợp lệ thành `NaN` để loại bỏ ở bước tiếp theo.

**(3) Loại bỏ dữ liệu thiếu và bản ghi trùng**

```python
df = df.dropna().drop_duplicates()
```

* `dropna()`: bỏ các dòng có giá trị thiếu (`NaN`) sau khi chuyển kiểu dữ liệu
* `drop_duplicates()`: bỏ dòng bị lặp
* Sau đó in thống kê:

  * số dòng trước/sau khi làm sạch
  * số lượng mẫu của từng lớp nhãn `NObeyesdad` (Label counts)

### 3.3. Chia Train/Test theo tỉ lệ 80:20 (Stratified split)

Mình chia dữ liệu bằng:

```python
train_df, test_df = train_test_split(
    df, test_size=0.2, random_state=42, stratify=df[TARGET]
)
```

Ý nghĩa:

* `test_size=0.2`: lấy 20% làm test, còn lại 80% train
* `random_state=42`: cố định ngẫu nhiên để lần chạy sau ra kết quả chia giống nhau (dễ tái lập)
* `stratify=df[TARGET]`: chia theo tỉ lệ lớp (các mức béo phì) để đảm bảo train và test có phân phối nhãn tương tự nhau

### 3.4. Kết quả sau bước chia dữ liệu

Sau khi chia xong, chương trình xuất ra 2 file:

* `obesity_train.csv`: dữ liệu train (80%)
* `obesity_test.csv`: dữ liệu test (20%)

Đồng thời in ra:

* số dòng train/test
* tỉ lệ nhãn trong train và test (`value_counts(normalize=True)`) để kiểm tra việc stratify đã giữ phân phối lớp ổn định

**Kết quả chạy thực tế:**

```txt
Rows before: 2111 | after clean: 2087 | removed: 24

Label counts:
Obesity_Type_I         351
Obesity_Type_III       324
Obesity_Type_II        297
Overweight_Level_II    290
Normal_Weight          282
Overweight_Level_I     276
Insufficient_Weight    267

✅ Saved:
 - obesity_train.csv | rows: 1669
 - obesity_test.csv | rows: 418

Label distribution (train):
Obesity_Type_I         0.168364
Obesity_Type_III       0.155183
Obesity_Type_II        0.142001
Overweight_Level_II    0.139005
Normal_Weight          0.134811
Overweight_Level_I     0.132415
Insufficient_Weight    0.128220

Label distribution (test):
Obesity_Type_I         0.167464
Obesity_Type_III       0.155502
Obesity_Type_II        0.143541
Overweight_Level_II    0.138756
Normal_Weight          0.136364
Overweight_Level_I     0.131579
Insufficient_Weight    0.126794
```

---

## 4. K-Means (Phân cụm K-Means)

### 4.1. Mục tiêu của file này là gì?

File `kmeans.py` làm 3 việc chính:

1. **Tiền xử lý dữ liệu** (vì có cả số + chữ):

   * Chuẩn hoá cột số bằng `StandardScaler`
   * Mã hoá cột chữ bằng `OneHotEncoder`
2. **Chạy K-Means với K = 7**

   * Tự chia dữ liệu train thành 7 cụm (cluster)
3. **Lưu kết quả và mô hình**

   * Lưu file CSV có thêm cột `Cluster`
   * Lưu cả “gói” gồm `preprocessor + kmeans` để bước KNN và GUI dùng lại

### 4.2. Các biến cấu hình đầu file

```python
TRAIN_CSV = "obesity_train.csv"
OUT_WITH_CLUSTER = "obesity_train_with_cluster.csv"
OUT_PACK = "obesity_kmeans_pack.joblib"
TARGET = "NObeyesdad"
```

* `TRAIN_CSV`: file input là tập train 80%.
* `OUT_WITH_CLUSTER`: output CSV sau khi gắn cụm.
* `OUT_PACK`: file lưu mô hình (dùng joblib).
* `TARGET`: tên cột nhãn thật — K-Means không dùng để học, nhưng dùng để đối chiếu phân bố.

### 4.3. Tại sao phải tách NUM_COLS và CAT_COLS?

```python
NUM_COLS = ["Age", "Height", "Weight", "FCVC", "NCP", "CH2O", "FAF", "TUE"]
CAT_COLS = ["Gender", "family_history_with_overweight", "FAVC", "CAEC", "SMOKE",
            "SCC", "CALC", "MTRANS"]
```

**NUM_COLS (cột số)**

* Dạng số thực/số nguyên
* Được `StandardScaler` để đưa về cùng thang đo (vì KMeans dùng khoảng cách)

**CAT_COLS (cột chữ/phân loại)**

* Dạng `Male/Female`, `yes/no`, `Sometimes/...`
* KMeans không hiểu chữ → cần `OneHotEncoder` để chuyển thành 0/1

### 4.4. Đọc dữ liệu & chuẩn hoá tên cột

```python
df = pd.read_csv(TRAIN_CSV)
df.columns = [c.strip() for c in df.columns]
```

### 4.5. Kiểm tra dữ liệu có đủ cột không

* Nếu thiếu cột target hoặc thiếu cột input cần thiết → dừng ngay để tránh chạy sai.

### 4.6. Tách X (feature) ra khỏi nhãn

```python
X = df.drop(columns=[TARGET]).copy()
```

### 4.7. Ép kiểu cột số + loại bỏ dòng lỗi

```python
for c in NUM_COLS:
    X[c] = pd.to_numeric(X[c], errors="coerce")
X = X.dropna(subset=NUM_COLS + CAT_COLS)
```

* `errors="coerce"`: dữ liệu số lỗi → thành `NaN`
* `dropna(subset=...)`: bỏ dòng thiếu dữ liệu ở các cột cần dùng

### 4.8. Preprocessor: StandardScaler + OneHotEncoder

```python
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), NUM_COLS),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
    ],
    remainder="drop"
)
```

* Nhánh `"num"`: chuẩn hoá cột số
* Nhánh `"cat"`: one-hot cho cột chữ
* `handle_unknown="ignore"`: GUI nhập giá trị lạ sẽ không crash

### 4.9. Fit + transform dữ liệu train

```python
Xp = preprocessor.fit_transform(X)
```

* `fit`: học tham số scale và danh sách categories
* `transform`: tạo ma trận số (thường dạng sparse do one-hot)

---

## 5. Huấn luyện K-NN và kết hợp K-Means để dự đoán `NObeyesdad`

File dùng: `knn.py`

Input:

* `obesity_train.csv` (80% train)
* `obesity_test.csv` (20% test)
* `obesity_kmeans_pack.joblib` (preprocessor + kmeans đã train ở bước 4)

Output:

* In kết quả đánh giá trên 20% test (accuracy, confusion matrix, classification report)
* Lưu mô hình dùng cho GUI: `obesity_knn_model.joblib`

### 5.1. Mục tiêu của bước này

K-NN là thuật toán phân loại có giám sát (supervised): học từ dữ liệu đã có nhãn để dự đoán nhãn mới.

Ở bài này, mình kết hợp K-Means theo cách:

* Không dùng “mã cluster” (0..6) trực tiếp,
* Mà dùng **khoảng cách từ mỗi mẫu đến 7 tâm cụm** (7 giá trị số) làm feature bổ sung.

Lý do:

* “Cluster id” chỉ là nhãn rời rạc (0/1/2/…), đôi khi không ổn định.
* “Khoảng cách tới centroid” là thông tin liên tục, phản ánh mức độ gần xa với từng nhóm → thường hữu ích hơn cho KNN.

### 5.2. Giải thích các biến cấu hình đầu file

```python
TRAIN_CSV = "obesity_train.csv"
TEST_CSV  = "obesity_test.csv"
KMEANS_PACK = "obesity_kmeans_pack.joblib"
OUT_MODEL = "obesity_knn_model.joblib"
TARGET = "NObeyesdad"
```
* TRAIN_CSV, TEST_CSV: dữ liệu đã chia 80/20 từ bước clean.
* KMEANS_PACK: gói model đã lưu ở bước KMeans (chứa preprocessor + kmeans).
* OUT_MODEL: file output lưu model KNN + kmeans_pack để GUI dùng.
* TARGET: nhãn cần dự đoán.

### 5.3. Hàm `make_features()` — kết hợp KMeans vào KNN

```python
def make_features(df, pack):
    preprocessor = pack["preprocessor"]
    kmeans = pack["kmeans"]

    X = df.drop(columns=[TARGET]).copy()
    Xp = preprocessor.transform(X)              # đã scale + onehot
    D = kmeans.transform(Xp)                    # khoảng cách tới 7 tâm cụm
    X_aug = np.hstack([Xp.toarray() if hasattr(Xp, "toarray") else Xp, D])
    return X_aug
```

* `Xp`: feature đã scale + one-hot theo đúng preprocessor cũ
* `D`: 7 khoảng cách đến 7 tâm cụm (K=7)
* `X_aug`: ghép feature gốc và khoảng cách centroid để tăng thông tin cho KNN

### 5.4. Đọc dữ liệu train/test và tách nhãn y

```python
train_df = pd.read_csv(TRAIN_CSV)
test_df  = pd.read_csv(TEST_CSV)

y_train = train_df[TARGET].astype(str).values
y_test  = test_df[TARGET].astype(str).values
```

### 5.5. Tạo đặc trưng train/test đã được kết hợp

```python
X_train = make_features(train_df, pack)
X_test  = make_features(test_df, pack)
```

### 5.6. GridSearchCV — tìm tham số tốt nhất cho KNN

```python
param_grid = {
    "n_neighbors": [1,3,5,7,9,11,13,15],
    "weights": ["uniform", "distance"]
}

gs = GridSearchCV(KNeighborsClassifier(), param_grid, cv=5, n_jobs=-1)
gs.fit(X_train, y_train)
```

* `n_neighbors`: số láng giềng k
* `weights`:

  * `uniform`: vote ngang nhau
  * `distance`: điểm gần vote mạnh hơn
* `cv=5`: cross-validation 5 phần
* `n_jobs=-1`: tận dụng toàn bộ CPU

### 5.7. Đánh giá mô hình trên 20% test

```python
y_pred = best_knn.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print("Accuracy:", acc)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
```

* **Accuracy**: tỉ lệ dự đoán đúng toàn bộ test
* **Confusion Matrix**: mô hình nhầm lớp nào sang lớp nào (đường chéo là dự đoán đúng)
* **Classification report**:

  * Precision: trong các mẫu dự đoán là lớp A, bao nhiêu là đúng
  * Recall: trong các mẫu thật là lớp A, mô hình bắt được bao nhiêu
  * F1-score: cân bằng precision và recall
  * Macro avg: trung bình đều các lớp
  * Weighted avg: trung bình có trọng số theo số lượng mẫu

### 5.8. Lưu mô hình để dùng cho GUI

```python
joblib.dump(
    {"knn": best_knn, "kmeans_pack": pack, "target": TARGET},
    OUT_MODEL
)
```

* Lưu `knn` + `kmeans_pack` để GUI dùng lại đúng pipeline preprocess + distances.

---

## 6. Cách chạy chương trình (thứ tự chuẩn)

Chạy theo đúng thứ tự:

```bash
python clean_data.py
python kmeans.py
python knn.py
python gui.py
```

> Lưu ý: GUI sẽ load model từ `obesity_knn_model.joblib`, nên cần chạy `knn.py` trước.

