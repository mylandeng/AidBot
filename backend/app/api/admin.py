from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def admin_status() -> dict[str, str]:
    return {"status": "not_configured", "next": "phase_1_admin_baseline"}
