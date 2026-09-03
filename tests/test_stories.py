from netopier.config import Settings
from netopier.stories import RANKING_VERSION, StoryEngine, explainable_score


def test_score_rewards_independent_source_families() -> None:
    one_family, _ = explainable_score(article_count=4, source_family_count=1)
    three_families, factors = explainable_score(article_count=4, source_family_count=3)
    assert three_families > one_family
    assert factors["ranking_version"] == RANKING_VERSION
    assert factors["source_family_count"] == 3


def test_score_is_deterministic() -> None:
    assert explainable_score(5, 2) == explainable_score(5, 2)


def test_assignment_version_records_threshold() -> None:
    engine = StoryEngine(None, Settings(story_similarity_threshold=0.83))  # type: ignore[arg-type]
    assert engine.algorithm_version == "temporal-centroid-v1:threshold=0.83"
