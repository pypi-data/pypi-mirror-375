from mlsort.data import synthesize_dataset
from mlsort.model import evaluate_model, fit_model


def test_training_pipeline_small():
    samples = synthesize_dataset(num_samples=60, max_n=1500, seed=123)
    X = [s.X for s in samples]
    y = [s.y for s in samples]
    artifacts = fit_model(X, y, random_state=123)
    metrics = evaluate_model(artifacts.model, X, y)
    # Overfit small set should be > 0.5 accuracy
    assert metrics["accuracy"] > 0.5
