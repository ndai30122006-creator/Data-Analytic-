"""Brief router — generate/list/get versioned briefs."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.deps import check_rate_limit, get_current_user

router = APIRouter(tags=["brief"])


class BriefCreateRequest(BaseModel):
    dataset_id: int


@router.post("/brief/{dataset_id}", dependencies=[Depends(check_rate_limit)])
async def create_brief(dataset_id: int, username: str = Depends(get_current_user)):
    import json

    from src.core.database import Brief, Dataset, SessionLocal

    try:
        with SessionLocal() as s:
            ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not ds or ds.username != username:
                raise HTTPException(status_code=404, detail="Dataset not found")
            # Get profile
            profile = {}
            if ds.profile_json:
                try:
                    profile = json.loads(ds.profile_json)
                except Exception:
                    profile = {}
            # AI (BYOK) neu user co key — chi gui profile, khong gui raw
            import logging as _logging

            from src.prompts.briefer import generate_brief_fallback

            _logger = _logging.getLogger(__name__)
            content, model_used = generate_brief_fallback(profile), "rule-based"
            try:
                from src.core.database import get_api_key, get_api_provider
                from src.core.llm_client import complete_model
                from src.prompts.briefer import build_prompt
                from src.prompts.schemas import BriefDoc

                user_key = get_api_key(username)
                if user_key:
                    provider = get_api_provider(username)
                    try:
                        # Structured output: validate schema truoc khi dung
                        doc, model = complete_model(user_key, provider, build_prompt(profile), BriefDoc)
                        content, model_used = doc.brief, f"{provider}:{model}"
                    except Exception as exc:
                        _logger.warning("LLM brief failed (%s), fallback rule-based", type(exc).__name__)
            except Exception as exc:
                _logger.warning("Brief AI path error, fallback rule-based: %s", exc)
            max_v = s.query(Brief).filter(Brief.dataset_id == dataset_id).count()
            b = Brief(dataset_id=dataset_id, version=max_v + 1, content=content, model_used=model_used)
            s.add(b)
            s.commit()
            s.refresh(b)
            return {"brief_id": b.id, "version": b.version, "content": content, "model_used": model_used}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create brief: {exc}")


@router.get("/brief/{dataset_id}", dependencies=[Depends(check_rate_limit)])
async def list_briefs(dataset_id: int, username: str = Depends(get_current_user)):
    from src.core.database import Brief, Dataset, SessionLocal

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not ds or ds.username != username:
            raise HTTPException(status_code=404, detail="Dataset not found")
        briefs = s.query(Brief).filter(Brief.dataset_id == dataset_id).order_by(Brief.version.desc()).all()
        return {
            "briefs": [
                {
                    "version": b.version,
                    "content": b.content[:200],
                    "model_used": b.model_used,
                    "created_at": b.created_at.isoformat() if b.created_at else None,
                }
                for b in briefs
            ]
        }


@router.get("/brief/{dataset_id}/{version}", dependencies=[Depends(check_rate_limit)])
async def get_brief_version(dataset_id: int, version: int, username: str = Depends(get_current_user)):
    from src.core.database import Brief, Dataset, SessionLocal

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not ds or ds.username != username:
            raise HTTPException(status_code=404, detail="Dataset not found")
        b = s.query(Brief).filter(Brief.dataset_id == dataset_id, Brief.version == version).first()
        if not b:
            raise HTTPException(status_code=404, detail="Brief version not found")
        return {"version": b.version, "content": b.content, "model_used": b.model_used}
