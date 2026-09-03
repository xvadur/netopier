import numpy as np

from netopier.benchmark import (
    dbscan_min_samples_one,
    evaluate,
    evaluate_relations,
    temporal_centroid,
    tfidf_vectors,
)
from netopier.events import EventRelation


def test_lexical_baseline_groups_near_duplicate_titles() -> None:
    vectors = tfidf_vectors(
        [
            "Brusel sa nedohodol na sankciách proti Rusku",
            "EÚ sa nedohodla na sankciách voči Rusku",
            "Slovan získal nového obrancu",
        ]
    )
    labels = dbscan_min_samples_one(vectors, 0.2)
    assert labels[0] == labels[1]
    assert labels[0] != labels[2]


def test_temporal_centroid_and_metrics_report_false_split() -> None:
    vectors = np.asarray([[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]], dtype=np.float32)
    predicted = temporal_centroid(vectors, 0.999)
    metrics = evaluate(
        ["a", "b", "c"],
        ["same", "same", "different"],
        predicted,
        ["one", "two", "three"],
    )
    assert metrics["pairwise_precision"] == 1.0
    assert metrics["pairwise_recall"] == 0.0
    assert metrics["false_split_pairs"] == [["a", "b"]]


def test_relation_metrics_separate_dangerous_false_merges_and_splits() -> None:
    expected = [
        EventRelation.SAME_EVENT,
        EventRelation.SAME_TOPIC,
        EventRelation.UNRELATED,
    ]
    predicted = [
        EventRelation.SAME_TOPIC,
        EventRelation.SAME_EVENT,
        EventRelation.UNRELATED,
    ]

    metrics = evaluate_relations(["split", "merge", "ok"], expected, predicted)

    assert metrics["automatic_merge_precision"] == 0.0
    assert metrics["automatic_merge_recall"] == 0.0
    assert metrics["dangerous_false_merges"] == ["merge"]
    assert metrics["false_splits"] == ["split"]
    assert metrics["per_class"]["unrelated"]["f1"] == 1.0
