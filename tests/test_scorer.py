from warm.core.scorer import Scorer

def test_scorer_weights():
    features = {"x": {"match": False}, "y": {"match": True}}
    weights = {"x": 0.5, "y": 0.5}
    scorer = Scorer(weights, thresholds={"benign_max":10,"suspicious_max":50,"malicious_min":51})
    score, label = scorer.compute(features)
    assert score == 100  # only x mismatches => weight 0.5 normalized to 100%
    assert label == "MALICIOUS"

