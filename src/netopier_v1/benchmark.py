import math
from collections import Counter
from collections.abc import Sequence

import numpy as np

from netopier_v1.events import EventRelation
from netopier_v1.text import normalize_title


def tfidf_vectors(texts: Sequence[str]) -> np.ndarray:
    documents: list[list[str]] = []
    for text in texts:
        words = normalize_title(text).split()
        documents.append(
            words + [f"{a}_{b}" for a, b in zip(words, words[1:], strict=False)]
        )
    vocabulary = sorted({token for document in documents for token in document})
    positions = {token: index for index, token in enumerate(vocabulary)}
    document_frequency = Counter(
        token for document in documents for token in set(document)
    )
    matrix = np.zeros((len(documents), len(vocabulary)), dtype=np.float32)
    for row, document in enumerate(documents):
        counts = Counter(document)
        for token, count in counts.items():
            inverse_document_frequency = math.log(
                (1 + len(documents)) / (1 + document_frequency[token])
            ) + 1
            matrix[row, positions[token]] = count * inverse_document_frequency
    return normalize_vectors(matrix)


def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return vectors / norms


def dbscan_min_samples_one(vectors: np.ndarray, threshold: float) -> list[int]:
    """DBSCAN with cosine distance and min_samples=1, expressed as components."""
    similarities = normalize_vectors(vectors) @ normalize_vectors(vectors).T
    labels = [-1] * len(vectors)
    cluster = 0
    for start in range(len(vectors)):
        if labels[start] != -1:
            continue
        labels[start] = cluster
        stack = [start]
        while stack:
            current = stack.pop()
            neighbors = np.flatnonzero(similarities[current] >= threshold)
            for neighbor in neighbors:
                index = int(neighbor)
                if labels[index] == -1:
                    labels[index] = cluster
                    stack.append(index)
        cluster += 1
    return labels


def temporal_centroid(vectors: np.ndarray, threshold: float) -> list[int]:
    normalized = normalize_vectors(vectors)
    centroids: list[np.ndarray] = []
    members: list[list[int]] = []
    labels: list[int] = []
    for vector in normalized:
        if not centroids:
            choice = -1
            similarity = -1.0
        else:
            scores = [float(vector @ centroid) for centroid in centroids]
            choice = int(np.argmax(scores))
            similarity = scores[choice]
        if choice == -1 or similarity < threshold:
            choice = len(centroids)
            members.append([len(labels)])
            centroids.append(vector)
        else:
            members[choice].append(len(labels))
            centroid = np.mean(normalized[members[choice]], axis=0, keepdims=True)
            centroids[choice] = normalize_vectors(centroid)[0]
        labels.append(choice)
    return labels


def evaluate(
    item_ids: Sequence[str],
    expected: Sequence[str],
    predicted: Sequence[int],
    source_families: Sequence[str],
) -> dict:
    true_pairs: set[tuple[int, int]] = set()
    predicted_pairs: set[tuple[int, int]] = set()
    for left in range(len(expected)):
        for right in range(left + 1, len(expected)):
            if expected[left] == expected[right]:
                true_pairs.add((left, right))
            if predicted[left] == predicted[right]:
                predicted_pairs.add((left, right))
    true_positive = len(true_pairs & predicted_pairs)
    false_positive = len(predicted_pairs - true_pairs)
    precision = true_positive / (true_positive + false_positive) if predicted_pairs else 1.0
    recall = true_positive / len(true_pairs) if true_pairs else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    cluster_members: dict[int, list[int]] = {}
    for index, label in enumerate(predicted):
        cluster_members.setdefault(label, []).append(index)
    singletons = sum(len(indices) == 1 for indices in cluster_members.values())
    multi_source = sum(
        len({source_families[index] for index in indices}) > 1
        for indices in cluster_members.values()
    )

    def named_pairs(pairs: set[tuple[int, int]]) -> list[list[str]]:
        return [[item_ids[left], item_ids[right]] for left, right in sorted(pairs)]

    return {
        "pairwise_precision": round(precision, 4),
        "pairwise_recall": round(recall, 4),
        "pairwise_f1": round(f1, 4),
        "true_positive_pairs": true_positive,
        "false_merge_pairs": named_pairs(predicted_pairs - true_pairs),
        "false_split_pairs": named_pairs(true_pairs - predicted_pairs),
        "cluster_count": len(cluster_members),
        "singleton_rate": round(singletons / len(cluster_members), 4),
        "multi_source_cluster_rate": round(multi_source / len(cluster_members), 4),
    }


MERGE_RELATIONS = {
    EventRelation.SYNDICATED_COPY,
    EventRelation.SAME_EVENT,
    EventRelation.EVENT_UPDATE,
}


def evaluate_relations(
    pair_ids: Sequence[str],
    expected: Sequence[EventRelation],
    predicted: Sequence[EventRelation],
) -> dict:
    if not (len(pair_ids) == len(expected) == len(predicted)):
        raise ValueError("pair ids, expected relations and predictions must have equal length")
    classes = list(EventRelation)
    per_class: dict[str, dict[str, float | int]] = {}
    for relation in classes:
        true_positive = sum(
            truth is relation and guess is relation
            for truth, guess in zip(expected, predicted, strict=True)
        )
        false_positive = sum(
            truth is not relation and guess is relation
            for truth, guess in zip(expected, predicted, strict=True)
        )
        false_negative = sum(
            truth is relation and guess is not relation
            for truth, guess in zip(expected, predicted, strict=True)
        )
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 1.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 1.0
        )
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[relation.value] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": sum(truth is relation for truth in expected),
        }
    true_merges = {index for index, relation in enumerate(expected) if relation in MERGE_RELATIONS}
    predicted_merges = {
        index for index, relation in enumerate(predicted) if relation in MERGE_RELATIONS
    }
    true_positive_merges = len(true_merges & predicted_merges)
    merge_precision = (
        true_positive_merges / len(predicted_merges) if predicted_merges else 1.0
    )
    merge_recall = true_positive_merges / len(true_merges) if true_merges else 1.0
    merge_f1 = (
        2 * merge_precision * merge_recall / (merge_precision + merge_recall)
        if merge_precision + merge_recall
        else 0.0
    )
    return {
        "accuracy": round(
            sum(truth is guess for truth, guess in zip(expected, predicted, strict=True))
            / len(expected),
            4,
        ) if expected else 1.0,
        "automatic_merge_precision": round(merge_precision, 4),
        "automatic_merge_recall": round(merge_recall, 4),
        "automatic_merge_f1": round(merge_f1, 4),
        "dangerous_false_merges": [
            pair_ids[index] for index in sorted(predicted_merges - true_merges)
        ],
        "false_splits": [pair_ids[index] for index in sorted(true_merges - predicted_merges)],
        "per_class": per_class,
    }
