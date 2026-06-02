from services.llm_service import check_llm
from services.vector_db_service import check_vector_db
from services.db_service import check_database
from services.cache_service import check_cache
from sqlalchemy.orm import Session

async def run_health_checks(db_session: Session, cache_client):
    llm_status = await check_llm()
    vector_db_status = await check_vector_db()
    db_status = check_database(db_session)
    cache_status = check_cache(cache_client)

    return {
        "Overall status" : [
            llm_status,
            vector_db_status,
            db_status,
            cache_status
        ]
    }