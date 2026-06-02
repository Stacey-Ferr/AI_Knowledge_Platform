from fastapi import APIRouter, Depends
from services.health_service import run_health_checks
from db.dependencies import get_db
from sqlalchemy.orm import Session
from cache.dependencies import get_cache

router = APIRouter()

@router.get("/health")
async def health_check(
                        db: Session = Depends(get_db), 
                        cache_client = Depends(get_cache)
                    ):
    result = await run_health_checks(db, cache_client)
    return result