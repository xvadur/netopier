import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np
import yaml

from netopier_v1.benchmark import (
    dbscan_min_samples_one,
    evaluate,
    temporal_centroid,
    tfidf_vectors,
)
from netopier_v1.config import get_settings
from netopier_v1.database import connection


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--dataset", default="benchmarks/slovak_title_clusters.yaml")
    result.add_argument("--json", default="benchmarks/results/slovak-clustering.json")
    result.add_argument("--report", default="benchmarks/SLOVAK_CLUSTERING_REPORT.md")
    return result


def measured(name: str, runner) -> dict:
    started = time.perf_counter()
    labels = runner()
    return {
        "name": name,
        "labels": labels,
        "runtime_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def markdown(payload: dict) -> str:
    lines = [
        "# Slovak clustering benchmark",
        "",
        f"Dataset: `{payload['dataset']}` ({payload['item_count']} public RSS titles)",
        f"Review status: **{payload['review_status']}**",
        "",
        "| Method | Precision | Recall | F1 | False merges | False splits | Runtime ms |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for result in payload["results"]:
        metrics = result["metrics"]
        lines.append(
            f"| {result['name']} | {metrics['pairwise_precision']:.4f} | "
            f"{metrics['pairwise_recall']:.4f} | {metrics['pairwise_f1']:.4f} | "
            f"{len(metrics['false_merge_pairs'])} | {len(metrics['false_split_pairs'])} | "
            f"{result['runtime_ms']:.3f} |"
        )
    lines.extend(
        [
            "",
            f"Selected runtime setting: **{payload['selection']}**.",
            "",
            "The 0.83 result is the selected live title-plus-RSS-text vector path. The lexical "
            "baseline uses word unigram/bigram TF-IDF and DBSCAN with cosine distance, "
            "`min_samples=1`. The 0.79 run is the required parameter comparison.",
            "",
            f"Peak process RSS observed: {payload['peak_rss_mb']:.1f} MiB.",
            "",
            "## Evidence boundary",
            "",
            "Labels are provisional and need Adam's editorial ratification. This window did "
            "not contain a verified article update-over-time example. The dataset stores only "
            "public titles and URLs; full RSS bodies and vectors remain in the ignored local "
            "database. False merges are treated as costlier than false splits.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parser().parse_args()
    dataset_path = Path(args.dataset)
    dataset = yaml.safe_load(dataset_path.read_text(encoding="utf-8"))
    if dataset.get("schema_version") != 1:
        raise SystemExit("unsupported benchmark schema")
    items = dataset["items"]
    urls = [item["url"] for item in items]
    settings = get_settings()
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT a.canonical_url, a.published_at, e.embedding::text AS embedding
            FROM articles a
            JOIN article_embeddings e ON e.article_id = a.id
            WHERE a.canonical_url = ANY(%s) AND e.model_version = %s
            """,
            (urls, settings.embedding_model),
        ).fetchall()
    by_url = {row["canonical_url"]: row for row in rows}
    missing = [url for url in urls if url not in by_url]
    if missing:
        raise SystemExit(f"benchmark articles missing from local archive: {missing}")
    ordered = sorted(items, key=lambda item: (by_url[item["url"]]["published_at"], item["id"]))
    titles = [item["title"] for item in ordered]
    embeddings = np.asarray(
        [json.loads(by_url[item["url"]]["embedding"]) for item in ordered],
        dtype=np.float32,
    )
    runs = [
        measured(
            "tfidf-dbscan@0.34",
            lambda: dbscan_min_samples_one(tfidf_vectors(titles), 0.34),
        ),
        measured(
            f"temporal-centroid@{settings.story_similarity_threshold:.2f}",
            lambda: temporal_centroid(embeddings, settings.story_similarity_threshold),
        ),
        measured(
            "temporal-centroid@0.79",
            lambda: temporal_centroid(embeddings, 0.79),
        ),
    ]
    item_ids = [item["id"] for item in ordered]
    expected = [item["expected_story"] for item in ordered]
    families = [item["source_family"] for item in ordered]
    for run in runs:
        run["metrics"] = evaluate(item_ids, expected, run.pop("labels"), families)
    selected = runs[1]
    payload = {
        "dataset": dataset["name"],
        "review_status": dataset["review_status"],
        "item_count": len(items),
        "embedding_model": settings.embedding_model,
        "selection": selected["name"],
        "results": runs,
        "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
    }
    json_path = Path(args.json)
    report_path = Path(args.report)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    report_path.write_text(markdown(payload), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
