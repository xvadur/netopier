import argparse
import json

from netopier_v1.config import get_settings
from netopier_v1.database import connection
from netopier_v1.pipeline import process_pending, reconcile_once, run_forever
from netopier_v1.sources import SourceRegistry, bootstrap_miniflux, load_source_manifest


def _print(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="netopier-v1")
    sub = parser.add_subparsers(dest="command", required=True)

    sources = sub.add_parser("sources")
    source_sub = sources.add_subparsers(dest="source_command", required=True)
    import_parser = source_sub.add_parser("import")
    import_parser.add_argument("manifest")
    bootstrap_parser = source_sub.add_parser("bootstrap-miniflux")
    bootstrap_parser.add_argument("manifest")

    sub.add_parser("reconcile")
    sub.add_parser("process")
    worker = sub.add_parser("worker")
    worker.add_argument("--forever", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = get_settings()
    if args.command == "sources":
        specs = load_source_manifest(args.manifest)
        if args.source_command == "import":
            with connection() as conn:
                _print(SourceRegistry(conn).import_specs(specs))
            return
        if not settings.miniflux_admin_password:
            raise SystemExit("MINIFLUX_ADMIN_PASSWORD is required")
        result = bootstrap_miniflux(specs, settings)
        with connection() as conn:
            result["bound_sources"] = SourceRegistry(conn).bind_miniflux(result)
        _print(result)
        return
    if args.command == "reconcile":
        _print(reconcile_once(settings))
        return
    if args.command == "process":
        _print(process_pending(settings))
        return
    if args.command == "worker":
        if args.forever:
            run_forever(settings)
        else:
            _print(reconcile_once(settings))
