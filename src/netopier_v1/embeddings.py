from collections.abc import Iterable
from uuid import UUID

from fastembed import TextEmbedding

from netopier_v1.config import Settings
from netopier_v1.database import DbConnection
from netopier_v1.domain import EmbeddingReceipt


def _vector_literal(values: Iterable[float]) -> str:
    return "[" + ",".join(f"{float(value):.9g}" for value in values) + "]"


class EmbeddingIndex:
    def __init__(
        self,
        conn: DbConnection,
        settings: Settings,
        model: TextEmbedding | None = None,
    ) -> None:
        self._conn = conn
        self._settings = settings
        self._model = model

    @property
    def model_version(self) -> str:
        return self._settings.embedding_model

    def _get_model(self) -> TextEmbedding:
        if self._model is None:
            self._model = TextEmbedding(
                model_name=self._settings.embedding_model,
                cache_dir=self._settings.embedding_cache_dir,
            )
        return self._model

    def embed(self, article_ids: Iterable[UUID]) -> EmbeddingReceipt:
        ids = tuple(article_ids)
        if not ids:
            return EmbeddingReceipt(article_ids=(), model_version=self.model_version)
        rows = self._conn.execute(
            """
            SELECT id, title, rss_content_text
            FROM articles
            WHERE id = ANY(%s)
            ORDER BY published_at, id
            """,
            (list(ids),),
        ).fetchall()
        texts = [f"passage: {row['title']}\n{row['rss_content_text'][:4000]}" for row in rows]
        vectors = list(self._get_model().embed(texts))
        embedded: list[UUID] = []
        for row, vector in zip(rows, vectors, strict=True):
            if len(vector) != self._settings.embedding_dimensions:
                raise ValueError(
                    f"model returned {len(vector)} dimensions; "
                    f"expected {self._settings.embedding_dimensions}"
                )
            self._conn.execute(
                """
                INSERT INTO article_embeddings (
                    article_id, model_version, dimensions, embedding
                ) VALUES (%s, %s, %s, %s::vector)
                ON CONFLICT (article_id, model_version) DO UPDATE SET
                    dimensions = EXCLUDED.dimensions,
                    embedding = EXCLUDED.embedding,
                    created_at = now()
                """,
                (
                    row["id"],
                    self.model_version,
                    self._settings.embedding_dimensions,
                    _vector_literal(vector),
                ),
            )
            embedded.append(row["id"])
        return EmbeddingReceipt(article_ids=tuple(embedded), model_version=self.model_version)

    def embed_pending(self, limit: int = 500) -> EmbeddingReceipt:
        rows = self._conn.execute(
            """
            SELECT a.id
            FROM articles a
            LEFT JOIN article_embeddings e
              ON e.article_id = a.id AND e.model_version = %s
            WHERE e.article_id IS NULL
            ORDER BY a.published_at, a.id
            LIMIT %s
            """,
            (self.model_version, limit),
        ).fetchall()
        return self.embed(row["id"] for row in rows)
