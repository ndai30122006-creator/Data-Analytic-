"""Analysis + lineage routers."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.deps import check_rate_limit, get_current_user
from src.core.database import get_dataset as db_get_dataset

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analysis"])


class AnalysisRequest(BaseModel):
    dataset_name: str
    analysis_type: str
    params: Dict[str, Any] = {}


def _dispatch_analysis(analysis_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Map analysis_type to real computation via src/core/statistical_tests."""
    import numpy as np

    from src.core.statistical_tests import (
        run_anova,
        run_bootstrap,
        run_kruskal,
        run_mannwhitney,
        run_ttest_independent,
        run_ttest_onesample,
        run_ttest_paired,
        run_two_proportion_ztest,
    )

    at = analysis_type.strip().lower()

    if at in ("ttest_independent", "ttest", "independent_ttest"):
        a = np.asarray(params.get("group_a") or params.get("data_a") or params.get("s1"), dtype=float)
        b = np.asarray(params.get("group_b") or params.get("data_b") or params.get("s2"), dtype=float)
        if a.size == 0 or b.size == 0:
            raise ValueError("group_a and group_b are required (non-empty arrays)")
        return run_ttest_independent(a, b)

    if at in ("ttest_onesample", "one_sample_ttest"):
        data = np.asarray(params.get("data") or params.get("group_a") or [], dtype=float)
        mu0 = float(params.get("mu0", params.get("mu", 0)))
        if data.size == 0:
            raise ValueError("data is required")
        return run_ttest_onesample(data, mu0)

    if at in ("ttest_paired", "paired_ttest"):
        before = np.asarray(params.get("before") or params.get("group_a") or [], dtype=float)
        after = np.asarray(params.get("after") or params.get("group_b") or [], dtype=float)
        if before.size == 0 or after.size == 0:
            raise ValueError("before and after are required")
        return run_ttest_paired(before, after)

    if at == "anova":
        groups_raw = params.get("groups")
        if not groups_raw or not isinstance(groups_raw, list):
            raise ValueError("groups (list of arrays) is required for ANOVA")
        groups = [np.asarray(g, dtype=float) for g in groups_raw]
        return run_anova(*groups)

    if at in ("mannwhitney", "mann_whitney", "mannwhitney_u"):
        a = np.asarray(params.get("group_a") or [], dtype=float)
        b = np.asarray(params.get("group_b") or [], dtype=float)
        if a.size == 0 or b.size == 0:
            raise ValueError("group_a and group_b are required")
        return run_mannwhitney(a, b)

    if at in ("kruskal", "kruskal_wallis"):
        groups_raw = params.get("groups")
        if not groups_raw or not isinstance(groups_raw, list):
            raise ValueError("groups is required for Kruskal-Wallis")
        groups = [np.asarray(g, dtype=float) for g in groups_raw]
        return run_kruskal(*groups)

    if at == "bootstrap":
        data = np.asarray(params.get("data") or params.get("group_a") or [], dtype=float)
        if data.size == 0:
            raise ValueError("data is required for bootstrap")
        n_iter = int(params.get("n_iter", 1000))
        conf_level = int(params.get("conf_level", 95))
        result = run_bootstrap(data, n_iter=n_iter, conf_level=conf_level)
        # Convert ndarray to list for JSON serialization
        result["boot_stats"] = (
            result["boot_stats"].tolist() if hasattr(result["boot_stats"], "tolist") else result["boot_stats"]
        )
        return result

    if at in ("ab_test", "two_proportion", "two_proportion_ztest", "abtest"):
        sa = int(params["successes_a"])
        ta = int(params["total_a"])
        sb = int(params["successes_b"])
        tb = int(params["total_b"])
        return run_two_proportion_ztest(sa, ta, sb, tb)

    if at in ("overview", "summary", "descriptive"):
        # Generic descriptive fallback — expects data array
        data = params.get("data")
        if data is not None:
            arr = np.asarray(data, dtype=float)
            return {
                "count": int(arr.size),
                "mean": float(np.mean(arr)) if arr.size else 0,
                "std": float(np.std(arr)) if arr.size else 0,
                "min": float(np.min(arr)) if arr.size else 0,
                "max": float(np.max(arr)) if arr.size else 0,
            }
        return {"message": "No data provided for overview", "params": params}

    raise ValueError(f"Unknown analysis_type: {analysis_type}")


@router.post("/analysis/run", dependencies=[Depends(check_rate_limit)])
async def run_analysis(
    request: AnalysisRequest,
    username: str = Depends(get_current_user),
):
    if not request.dataset_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dataset_name is required",
        )
    if not request.analysis_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="analysis_type is required",
        )
    # If dataset_name is not "inline" and not "demo", verify it exists for this user
    if request.dataset_name not in ("inline", "demo", "__inline__"):
        ds = db_get_dataset(username, request.dataset_name)
        if ds is None:
            # Allow inline computation even when dataset not found — require data in params
            has_inline_data = any(k in request.params for k in ("data", "group_a", "groups", "successes_a"))
            if not has_inline_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dataset '{request.dataset_name}' not found. Create it via POST /datasets or use dataset_name='inline' with data in params.",
                )
    try:
        results = _dispatch_analysis(request.analysis_type, request.params)
        # Ensure JSON serializable (convert numpy types)
        import numpy as np

        def _to_python(obj):
            import math

            if isinstance(obj, np.generic):
                obj = obj.item()
            if isinstance(obj, np.ndarray):
                return _to_python(obj.tolist())
            if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
                return None
            if isinstance(obj, dict):
                return {k: _to_python(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_to_python(v) for v in obj]
            return obj

        results = _to_python(results)
        return {
            "status": "success",
            "username": username,
            "dataset": request.dataset_name,
            "analysis_type": request.analysis_type,
            "results": results,
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error("Analysis failed (%s): %s", request.analysis_type, exc, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Analysis failed")


@router.get("/lineage/{dataset_id}", dependencies=[Depends(check_rate_limit)])
async def get_lineage_endpoint(dataset_id: int, username: str = Depends(get_current_user)):
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not ds or ds.username != username:
            raise HTTPException(status_code=404, detail="Dataset not found")
    from src.warehouse.lineage import get_lineage

    lin = get_lineage(dataset_id)
    return lin
