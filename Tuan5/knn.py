import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

TRAIN_CSV = "obesity_train.csv"
TEST_CSV  = "obesity_test.csv"

KMEANS_PACK = "obesity_kmeans_pack.joblib"
OUT_MODEL = "obesity_knn_model.joblib"

TARGET = "NObeyesdad"

def make_features(df, pack):
    preprocessor = pack["preprocessor"]
    kmeans = pack["kmeans"]

    X = df.drop(columns=[TARGET]).copy()
    Xp = preprocessor.transform(X)              # đã scale + onehot
    D = kmeans.transform(Xp)                    # khoảng cách tới 7 tâm cụm
    X_aug = np.hstack([Xp.toarray() if hasattr(Xp, "toarray") else Xp, D])
    return X_aug

def main():
    pack = joblib.load(KMEANS_PACK)

    train_df = pd.read_csv(TRAIN_CSV)
    test_df  = pd.read_csv(TEST_CSV)

    # y
    y_train = train_df[TARGET].astype(str).values
    y_test  = test_df[TARGET].astype(str).values

    # X kết hợp (gốc + distances)
    X_train = make_features(train_df, pack)
    X_test  = make_features(test_df, pack)

    # Grid search k cho KNN
    param_grid = {
        "n_neighbors": [1,3,5,7,9,11,13,15],
        "weights": ["uniform", "distance"]
    }

    gs = GridSearchCV(KNeighborsClassifier(), param_grid, cv=5, n_jobs=-1)
    gs.fit(X_train, y_train)

    best_knn = gs.best_estimator_
    print("✅ Best params:", gs.best_params_)

    # Evaluate on 20% test
    y_pred = best_knn.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print("\n=== TEST (20%) RESULT ===")
    print("Accuracy:", acc)
    print("\nConfusion matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification report:")
    print(classification_report(y_test, y_pred))

    # Save model pack for GUI
    joblib.dump(
        {"knn": best_knn, "kmeans_pack": pack, "target": TARGET},
        OUT_MODEL
    )
    print(f"\n✅ Saved -> {OUT_MODEL}")

if __name__ == "__main__":
    main()
