from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/", summary="Проверка доступности сервиса")
async def health():
    return {"status": "ok"}
