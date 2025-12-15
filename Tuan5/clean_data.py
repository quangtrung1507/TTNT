import pandas as pd
from sklearn.model_selection import train_test_split

INPUT_CSV = "ObesityDataSet_raw_and_data_sinthetic.csv"

TRAIN_OUT = "obesity_train.csv"
TEST_OUT  = "obesity_test.csv"

TARGET = "NObeyesdad"  # nhãn mức độ béo phì

def main():
    df = pd.read_csv(INPUT_CSV)
    df.columns = [c.strip() for c in df.columns]

    if TARGET not in df.columns:
        raise ValueError(f"Không thấy cột target '{TARGET}'. Cột hiện có: {list(df.columns)}")

    # --- Clean cơ bản ---
    before = len(df)

    # strip các cột dạng object
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].astype(str).str.strip()

    # ép numeric cho các cột số nếu có (Age/Height/Weight thường là số)
    # (để an toàn: thử convert, lỗi thì giữ nguyên)
    for c in df.columns:
        if c != TARGET and df[c].dtype != "object":
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # drop NA và trùng
    df = df.dropna().drop_duplicates()

    after = len(df)
    print(f"Rows before: {before} | after clean: {after} | removed: {before-after}")
    print("\nLabel counts:")
    print(df[TARGET].value_counts())

    # --- Split 80/20 (stratify) ---
    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df[TARGET]
    )

    train_df.to_csv(TRAIN_OUT, index=False)
    test_df.to_csv(TEST_OUT, index=False)

    print("\n✅ Saved:")
    print(" -", TRAIN_OUT, "| rows:", len(train_df))
    print(" -", TEST_OUT,  "| rows:", len(test_df))

    print("\nLabel distribution (train):")
    print(train_df[TARGET].value_counts(normalize=True))

    print("\nLabel distribution (test):")
    print(test_df[TARGET].value_counts(normalize=True))

if __name__ == "__main__":
    main()
