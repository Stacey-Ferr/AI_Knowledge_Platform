from core.logging import logger
from schemas.responses import HealthResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

def check_database(db_session: Session):
    try:
        result = db_session.execute(text("SELECT 1;"))
        print("Database result: ", result.scalar())
        logger.info("Postgresql database is Healthy.")
        return HealthResponse(**{ "service" : "Postgresql database", "status" : "healthy"})
    except Exception as e:
        logger.error(f"Postgresql database is Unhealthy.\nException occured: {e}")
        return HealthResponse(**{ "service" : "Postgresql database", "status" : "unhealthy"})