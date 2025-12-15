import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans

TRAIN_CSV = "obesity_train.csv"
OUT_WITH_CLUSTER = "obesity_train_with_cluster.csv"
OUT_PACK = "obesity_kmeans_pack.joblib"

TARGET = "NObeyesdad"

NUM_COLS = ["Age", "Height", "Weight", "FCVC", "NCP", "CH2O", "FAF", "TUE"]
CAT_COLS = ["Gender", "family_history_with_overweight", "FAVC", "CAEC", "SMOKE",
            "SCC", "CALC", "MTRANS"]

K = 7  # ✅ cố định bằng số mức độ béo phì

def main():
    df = pd.read_csv(TRAIN_CSV)
    df.columns = [c.strip() for c in df.columns]

    if TARGET not in df.columns:
        raise ValueError(f"Không thấy cột target {TARGET}. Cột hiện có: {list(df.columns)}")

    missing = [c for c in NUM_COLS + CAT_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Thiếu cột: {missing}. Cột hiện có: {list(df.columns)}")

    X = df.drop(columns=[TARGET]).copy()

    for c in NUM_COLS:
        X[c] = pd.to_numeric(X[c], errors="coerce")
    X = X.dropna(subset=NUM_COLS + CAT_COLS)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUM_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
        ],
        remainder="drop"
    )

    Xp = preprocessor.fit_transform(X)

    kmeans = KMeans(n_clusters=K, random_state=42, n_init="auto")
    cluster_id = kmeans.fit_predict(Xp)

    print(f"✅ Fixed K = {K}")

    out_df = df.loc[X.index].copy()
    out_df["Cluster"] = cluster_id
    out_df.to_csv(OUT_WITH_CLUSTER, index=False)
    print(f"✅ Saved -> {OUT_WITH_CLUSTER}")

    print("\nCluster vs Label (count):")
    print(pd.crosstab(out_df["Cluster"], out_df[TARGET]))

    joblib.dump(
        {
            "preprocessor": preprocessor,
            "kmeans": kmeans,
            "best_k": K,
            "num_cols": NUM_COLS,
            "cat_cols": CAT_COLS,
            "target": TARGET
        },
        OUT_PACK
    )
    print(f"\n✅ Saved KMeans pack -> {OUT_PACK}")

if __name__ == "__main__":
    main()
