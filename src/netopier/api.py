from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query

from netopier import __version__
from netopier.database import connection
from netopier.feed import EventQuery, FeedProjector

app = FastAPI(
    title="Netopier v2",
    description="Local-first Slovak public-source news intelligence backend",
    version=__version__,
)


@app.get("/health")
def health() -> dict:
    with connection() as conn:
        return FeedProjector(conn).health()


@app.get("/feed")
def feed(
    limit: int = Query(default=50, ge=1, le=200), cursor: str | None = Query(default=None)
) -> dict:
    with connection() as conn:
        try:
            return FeedProjector(conn).snapshot(limit=limit, cursor=cursor)
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=400, detail="invalid cursor") from exc


@app.get("/stories/{story_id}")
def story(story_id: UUID) -> dict:
    with connection() as conn:
        result = FeedProjector(conn).story(story_id)
        if result is None:
            raise HTTPException(status_code=404, detail="story not found")
        return result


@app.get("/sources")
def sources() -> list[dict]:
    with connection() as conn:
        return FeedProjector(conn).sources()


@app.get("/events")
def events(
    person: Annotated[list[str] | None, Query()] = None,
    organization: Annotated[list[str] | None, Query()] = None,
    public_institution: Annotated[list[str] | None, Query()] = None,
    geography: str | None = Query(default=None),
    since: str | None = Query(default=None),
    until: str | None = Query(default=None),
    action_type: Annotated[list[str] | None, Query()] = None,
    institutional_status: str | None = Query(default=None),
    min_independent_sources: int = Query(default=0, ge=0),
    novelty: str | None = Query(default=None),
    evidence_strength: str | None = Query(default=None),
    coverage: str | None = Query(default=None),
    min_articles: int = Query(default=0, ge=0),
    has_conflicts: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict:
    try:
        event_query = EventQuery(
            people=tuple(person or ()),
            organizations=tuple(organization or ()),
            public_institutions=tuple(public_institution or ()),
            geography=geography,
            since=datetime.fromisoformat(since) if since else None,
            until=datetime.fromisoformat(until) if until else None,
            action_types=tuple(action_type or ()),
            institutional_status=institutional_status,
            min_independent_sources=min_independent_sources,
            novelty=novelty,
            evidence_strength=evidence_strength,
            coverage=coverage,
            min_articles=min_articles,
            has_conflicts=has_conflicts,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid event filter") from exc
    with connection() as conn:
        try:
            return FeedProjector(conn).events(event_query)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
