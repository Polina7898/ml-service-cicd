import json
import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

HYPERPARAMS = {"n_estimators": 100, "random_state": 42}
MODEL_PATH = "model.joblib"
METRICS_PATH = "metrics.json"


def train():
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    model = RandomForestClassifier(**HYPERPARAMS).fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    joblib.dump(model, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump({"accuracy": round(accuracy, 4)}, f)
    return accuracy


if __name__ == "__main__":
    print(f"accuracy={train():.4f}")
