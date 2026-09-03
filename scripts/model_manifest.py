import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from netopier.config import get_settings


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    settings = get_settings()
    root = Path(settings.embedding_cache_dir)
    files = []
    aggregate = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        relative = str(path.relative_to(root))
        digest = sha256(path)
        size = path.stat().st_size
        files.append({"path": relative, "size": size, "sha256": digest})
        aggregate.update(f"{relative}\0{size}\0{digest}\n".encode())
    if not files:
        raise SystemExit(f"no model files found in {root}")
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "model": settings.embedding_model,
        "dimensions": settings.embedding_dimensions,
        "file_count": len(files),
        "total_bytes": sum(item["size"] for item in files),
        "aggregate_sha256": aggregate.hexdigest(),
        "files": files,
    }
    output = Path("artifacts/model-manifest.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "written",
                "output": str(output),
                "file_count": len(files),
                "total_bytes": payload["total_bytes"],
                "aggregate_sha256": payload["aggregate_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
