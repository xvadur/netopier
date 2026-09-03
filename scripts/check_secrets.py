import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__", "var", "data", "private"}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub token": re.compile(r"\bgh[opusr]_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}


def main() -> None:
    ignored = subprocess.run(
        ["git", "check-ignore", "--quiet", ".env"], cwd=ROOT, check=False
    )
    if ignored.returncode != 0:
        raise SystemExit(".env is not ignored")
    findings: list[str] = []
    scanned = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if path.name == ".env":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scanned += 1
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}: {name}")
    if findings:
        raise SystemExit("possible secrets found:\n" + "\n".join(findings))
    print(f"secret scan passed: {scanned} text files; .env ignored")


if __name__ == "__main__":
    main()
