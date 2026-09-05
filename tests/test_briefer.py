"""Tests for briefer (P2) — mock AI + fallback."""

import json


def test_build_prompt_profile_only():
    from src.prompts.briefer import build_prompt

    profile = {"table": "raw.t", "rows": 10, "cols": 2, "columns": {"a": {"type": "int"}}}
    prompt = build_prompt(profile)
    assert len(prompt) == 2
    assert "profile" in prompt[1]["content"]
    # Ensure no raw data leak
    assert "raw.t" in prompt[1]["content"] or "a" in prompt[1]["content"]


def test_fallback_rule_based():
    from src.prompts.briefer import generate_brief_fallback

    profile = {"rows": 100, "cols": 3, "quality_score": 0.8, "issues": {"high_missing": ["a"]}}
    brief = generate_brief_fallback(profile)
    assert isinstance(brief, str)
    assert "100" in brief or "Dataset" in brief


def test_brief_versioning(tmp_path):
    from src.core.database import Brief, Dataset, SessionLocal

    # Create temp dataset
    with SessionLocal() as s:
        ds = Dataset(username="test_brief_user", dataset_name="test_brief_ds", rows=10, cols=2)
        s.add(ds)
        s.commit()
        s.refresh(ds)
        ds_id = ds.id

        # Create 2 brief versions
        b1 = Brief(dataset_id=ds_id, version=1, content="v1", model_used="rule-based")
        s.add(b1)
        s.commit()
        b2 = Brief(dataset_id=ds_id, version=2, content="v2", model_used="rule-based")
        s.add(b2)
        s.commit()

        briefs = s.query(Brief).filter(Brief.dataset_id == ds_id).order_by(Brief.version).all()
        assert len(briefs) == 2
        assert briefs[1].version == 2

        # Cleanup
        s.query(Brief).filter(Brief.dataset_id == ds_id).delete()
        s.query(Dataset).filter(Dataset.id == ds_id).delete()
        s.commit()
