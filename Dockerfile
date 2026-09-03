FROM python:3.12.11-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HOME=/var/cache/netopier \
    HF_HOME=/var/cache/netopier/huggingface \
    XDG_CACHE_HOME=/var/cache/netopier \
    HF_HUB_DISABLE_XET=1

WORKDIR /app

RUN addgroup --system netopier \
    && adduser --system --ingroup netopier netopier \
    && mkdir -p /var/cache/netopier/models \
    && chown -R netopier:netopier /var/cache/netopier

COPY pyproject.toml README.md /app/
RUN python -c 'import subprocess,sys,tomllib; p=tomllib.load(open("pyproject.toml","rb")); subprocess.check_call([sys.executable,"-m","pip","install","--no-cache-dir",*p["project"]["dependencies"]])'
COPY src /app/src
COPY migrations /app/migrations
COPY alembic.ini /app/alembic.ini
COPY sources /app/sources
COPY benchmarks /app/benchmarks
COPY scripts /app/scripts
COPY tests /app/tests

RUN pip install --no-cache-dir --no-deps "."

FROM base AS runtime
USER netopier

CMD ["uvicorn", "netopier_v1.api:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS test
RUN python -c 'import subprocess,sys,tomllib; p=tomllib.load(open("pyproject.toml","rb")); subprocess.check_call([sys.executable,"-m","pip","install","--no-cache-dir",*p["project"]["optional-dependencies"]["dev"]])'
CMD ["sh", "-c", "pytest -q && ruff check src tests benchmarks scripts && mypy src/netopier_v1"]
