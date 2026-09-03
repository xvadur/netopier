import json

from netopier.database import connection
from netopier.feed import FeedProjector


def main() -> None:
    with connection() as conn:
        first_page = FeedProjector(conn).snapshot(limit=7)
        snapshot_id = first_page["snapshot_id"]
        target = conn.execute(
            """
            SELECT story_id
            FROM feed_snapshot_items
            WHERE snapshot_id = %s
            ORDER BY position DESC
            LIMIT 1
            """,
            (snapshot_id,),
        ).fetchone()
        assert target is not None
        target_id = target["story_id"]
        conn.execute("UPDATE stories SET score = score + 1000 WHERE id = %s", (target_id,))
        inserted = conn.execute(
            """
            INSERT INTO stories (
                representative_article_id, title, centroid, first_published_at,
                last_published_at, article_count, source_family_count, score,
                score_factors, algorithm_version, ranking_version
            )
            SELECT
                representative_article_id, '[snapshot mutation probe]', centroid,
                first_published_at, last_published_at, 1, 1, score + 500,
                score_factors, algorithm_version, ranking_version
            FROM stories
            WHERE id = %s
            RETURNING id
            """,
            (target_id,),
        ).fetchone()
        assert inserted is not None
        inserted_id = inserted["id"]

    try:
        ids = [item["id"] for item in first_page["items"]]
        cursor = first_page["next_cursor"]
        while cursor:
            with connection() as conn:
                page = FeedProjector(conn).snapshot(limit=7, cursor=cursor)
            ids.extend(item["id"] for item in page["items"])
            cursor = page["next_cursor"]
        if len(ids) != first_page["story_count"] or len(ids) != len(set(ids)):
            raise SystemExit("snapshot traversal changed after live rescoring")
        print(
            json.dumps(
                {
                    "status": "passed",
                    "snapshot_id": str(snapshot_id),
                    "stories_traversed": len(ids),
                    "unique_stories": len(set(ids)),
                    "rescored_story": str(target_id),
                    "concurrent_story_fixture": str(inserted_id),
                },
                indent=2,
            )
        )
    finally:
        with connection() as conn:
            conn.execute("UPDATE stories SET score = score - 1000 WHERE id = %s", (target_id,))
            conn.execute("DELETE FROM stories WHERE id = %s", (inserted_id,))


if __name__ == "__main__":
    main()
