from netopier.text import canonicalize_url, content_hash, html_to_text, normalize_title


def test_canonicalize_url_removes_fragment_and_tracking() -> None:
    value = "HTTPS://DennikN.sk/clanok/?utm_source=x&b=2&a=1#diskusia"
    assert canonicalize_url(value) == "https://dennikn.sk/clanok?b=2&a=1"


def test_normalization_preserves_slovak_letters() -> None:
    assert normalize_title("  Štát: nový zákon!  ") == "štát nový zákon"


def test_html_to_text_keeps_visible_rss_text() -> None:
    assert html_to_text("<p>Prvá&nbsp;veta.</p><p>Druhá veta.</p>") == "Prvá veta. Druhá veta."


def test_content_hash_is_stable() -> None:
    assert content_hash("a", "b") == content_hash("a", "b")
    assert content_hash("a", "b") != content_hash("a", "c")

