import joblib
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

MODEL_PATH = "obesity_knn_model.joblib"

OPTIONS = {
    "Gender": ["Male", "Female"],
    "family_history_with_overweight": ["yes", "no"],
    "FAVC": ["yes", "no"],
    "CAEC": ["no", "Sometimes", "Frequently", "Always"],
    "SMOKE": ["yes", "no"],
    "SCC": ["yes", "no"],
    "CALC": ["no", "Sometimes", "Frequently", "Always"],
    "MTRANS": ["Public_Transportation", "Automobile", "Walking", "Motorbike", "Bike"],
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Obesity Prediction - KMeans + KNN Demo")
        self.geometry("920x560")

        pack = joblib.load(MODEL_PATH)
        self.knn = pack["knn"]
        self.kmeans_pack = pack["kmeans_pack"]
        self.preprocessor = self.kmeans_pack["preprocessor"]
        self.kmeans = self.kmeans_pack["kmeans"]
        self.num_cols = self.kmeans_pack["num_cols"]
        self.cat_cols = self.kmeans_pack["cat_cols"]
        self.k = self.kmeans_pack.get("best_k", 7)

        self.num_vars = {}
        self.cat_vars = {}

        self._build_ui()

    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        ttk.Label(
            root,
            text="Dự đoán mức độ béo phì (KMeans + KNN)\nNhập/chọn đầy đủ các trường rồi bấm Predict",
            font=("Arial", 13, "bold")
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        # ===== Numeric inputs =====
        num_frame = ttk.LabelFrame(root, text="Numeric (số)", padding=10)
        num_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(0, 10))

        for i, col in enumerate(self.num_cols):
            ttk.Label(num_frame, text=col).grid(row=i, column=0, sticky="w", pady=5)
            v = tk.StringVar(value="")
            self.num_vars[col] = v
            ttk.Entry(num_frame, textvariable=v, width=20).grid(row=i, column=1, sticky="w", pady=5)

        # ===== Categorical inputs =====
        cat_frame = ttk.LabelFrame(root, text="Categorical (chọn)", padding=10)
        cat_frame.grid(row=1, column=2, columnspan=2, sticky="nsew")

        for i, col in enumerate(self.cat_cols):
            ttk.Label(cat_frame, text=col).grid(row=i, column=0, sticky="w", pady=5)
            v = tk.StringVar(value="")
            self.cat_vars[col] = v

            values = OPTIONS.get(col, [])
            cb = ttk.Combobox(cat_frame, textvariable=v, values=values, width=25, state="readonly")
            cb.grid(row=i, column=1, sticky="w", pady=5)

        # Buttons
        btn_frame = ttk.Frame(root)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="w", pady=(12, 0))

        ttk.Button(btn_frame, text="Predict", command=self.predict).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(btn_frame, text="Clear", command=self.clear_all).grid(row=0, column=1)

        self.result = tk.StringVar(value="Kết quả sẽ hiển thị ở đây.")
        ttk.Label(root, textvariable=self.result, foreground="blue", wraplength=880).grid(
            row=3, column=0, columnspan=4, sticky="w", pady=(14, 0)
        )


    def clear_all(self):
        for v in self.num_vars.values():
            v.set("")
        for v in self.cat_vars.values():
            v.set("")
        self.result.set("Đã xoá hết dữ liệu nhập.")

    def _build_row_df(self):
        row = {}

        # numeric
        for col in self.num_cols:
            s = self.num_vars[col].get().strip()
            if s == "":
                raise ValueError(f"Thiếu giá trị số: {col}")
            row[col] = float(s)

        # categorical
        for col in self.cat_cols:
            s = self.cat_vars[col].get().strip()
            if s == "":
                raise ValueError(f"Chưa chọn: {col}")
            row[col] = s

        return pd.DataFrame([row])

    def predict(self):
        try:
            df_one = self._build_row_df()

            # Transform giống lúc train (one-hot + scale)
            Xp = self.preprocessor.transform(df_one)

            # KMeans: distances (để kết hợp feature)
            D = self.kmeans.transform(Xp)  # (1, k)

            # Kết hợp feature: [Xp, D]
            X_dense = Xp.toarray() if hasattr(Xp, "toarray") else Xp
            X_aug = np.hstack([X_dense, D])

            # KNN predict
            pred = self.knn.predict(X_aug)[0]

            # ✅ Chỉ hiển thị kết quả dự đoán mức độ
            self.result.set(f"Dự đoán mức độ: {pred}")

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


if __name__ == "__main__":
    app = App()
    app.mainloop()
