from fastapi import APIRouter

router = APIRouter()


@router.get('/', summary='Проверка доступности сервиса')
async def health():
    return {'status': 'ok'}
