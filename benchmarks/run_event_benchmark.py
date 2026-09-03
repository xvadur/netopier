import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np
import yaml

from netopier_v1.benchmark import evaluate_relations, tfidf_vectors
from netopier_v1.config import get_settings
from netopier_v1.database import connection
from netopier_v1.events import EventFeatures, EventRelation, RelationshipDecider


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--dataset", default="benchmarks/event_relation_pairs.yaml")
    result.add_argument("--json", default="benchmarks/results/event-relations.json")
    result.add_argument("--report", default="benchmarks/EVENT_RELATIONS_REPORT.md")
    return result


def similarity_relation(
    score: float, copy_threshold: float, event_threshold: float
) -> EventRelation:
    if score >= copy_threshold:
        return EventRelation.SYNDICATED_COPY
    if score >= event_threshold:
        return EventRelation.SAME_EVENT
    if score >= 0.42:
        return EventRelation.SAME_TOPIC
    return EventRelation.UNRELATED


def lexical_similarity(left: str, right: str) -> float:
    vectors = tfidf_vectors([left, right])
    return float(vectors[0] @ vectors[1])


def measured(name: str, runner) -> dict:
    started = time.perf_counter()
    predictions = runner()
    return {
        "name": name,
        "predictions": [prediction.value for prediction in predictions],
        "runtime_ms": round((time.perf_counter() - started) * 1000, 3),
        "relations": predictions,
    }


def markdown(payload: dict) -> str:
    lines = [
        "# Event relationship benchmark",
        "",
        f"Dataset: `{payload['dataset']}` ({payload['pair_count']} source-linked pairs)",
        f"Review status: **{payload['review_status']}**",
        "",
        "| Method | Accuracy | Merge precision | Merge recall | Merge F1 | "
        "False merges | False splits |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for result in payload["results"]:
        metrics = result["metrics"]
        lines.append(
            f"| {result['name']} | {metrics['accuracy']:.4f} | "
            f"{metrics['automatic_merge_precision']:.4f} | "
            f"{metrics['automatic_merge_recall']:.4f} | "
            f"{metrics['automatic_merge_f1']:.4f} | "
            f"{len(metrics['dangerous_false_merges'])} | {len(metrics['false_splits'])} |"
        )
    lines.extend(
        [
            "",
            "False merge means the method would automatically combine a same-topic "
            "or unrelated pair. ",
            "False split means it would separate a syndicated copy, same event, or event update.",
            "",
            "## Evidence boundary",
            "",
            payload["evidence_boundary"],
            "",
            f"Peak process RSS observed: {payload['peak_rss_mb']:.1f} MiB.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parser().parse_args()
    dataset = yaml.safe_load(Path(args.dataset).read_text(encoding="utf-8"))
    if dataset.get("schema_version") != 1:
        raise SystemExit("unsupported benchmark schema")
    pairs = dataset["pairs"]
    urls = sorted({url for pair in pairs for url in (pair["left_url"], pair["right_url"])})
    settings = get_settings()
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT a.canonical_url, a.normalized_title, a.rss_content_text, a.content_hash,
                   a.published_at, e.embedding::text AS embedding
            FROM articles a JOIN article_embeddings e ON e.article_id = a.id
            WHERE a.canonical_url = ANY(%s) AND e.model_version = %s
            """,
            (urls, settings.embedding_model),
        ).fetchall()
    articles = {row["canonical_url"]: row for row in rows}
    missing = [url for url in urls if url not in articles]
    if missing:
        raise SystemExit(f"benchmark evidence missing from local archive: {missing}")
    lexical_scores: list[float] = []
    embedding_scores: list[float] = []
    hybrid_relations: list[EventRelation] = []
    decider = RelationshipDecider()
    for pair in pairs:
        left, right = articles[pair["left_url"]], articles[pair["right_url"]]
        lexical = lexical_similarity(left["normalized_title"], right["normalized_title"])
        left_vector = np.asarray(json.loads(left["embedding"]), dtype=np.float32)
        right_vector = np.asarray(json.loads(right["embedding"]), dtype=np.float32)
        embedding = float(left_vector @ right_vector) / float(
            np.linalg.norm(left_vector) * np.linalg.norm(right_vector)
        )
        lexical_scores.append(lexical)
        embedding_scores.append(embedding)
        anchors = pair.get("anchors", {})
        hybrid_relations.append(
            decider.decide(
                EventFeatures(
                    canonical_url_match=left["canonical_url"] == right["canonical_url"],
                    content_hash_match=left["content_hash"] == right["content_hash"],
                    normalized_title_match=left["normalized_title"] == right["normalized_title"],
                    title_similarity=lexical,
                    text_similarity=lexical_similarity(
                        left["rss_content_text"], right["rss_content_text"]
                    ),
                    lexical_similarity=lexical,
                    embedding_similarity=embedding,
                    **anchors,
                )
            ).relation
        )
    runs = [
        measured(
            "lexical-baseline",
            lambda: [similarity_relation(score, 0.95, 0.70) for score in lexical_scores],
        ),
        measured(
            "embedding-baseline",
            lambda: [similarity_relation(score, 0.97, 0.83) for score in embedding_scores],
        ),
        measured("hybrid-event-v2", lambda: hybrid_relations),
    ]
    expected = [EventRelation(pair["relation"]) for pair in pairs]
    pair_ids = [pair["id"] for pair in pairs]
    for run in runs:
        run["metrics"] = evaluate_relations(pair_ids, expected, run.pop("relations"))
    payload = {
        "dataset": dataset["name"],
        "review_status": dataset["review_status"],
        "evidence_boundary": dataset["evidence_boundary"],
        "pair_count": len(pairs),
        "embedding_model": settings.embedding_model,
        "results": runs,
        "pairs": pairs,
        "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
    }
    output = json.loads(json.dumps(payload, default=str))
    json_path, report_path = Path(args.json), Path(args.report)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(markdown(output), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
