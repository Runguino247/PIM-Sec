from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.db.session import SessionLocal
from app.models.repository import Repository
from app.models.baseline import Baseline
from app.fim.scanner import run_scan
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def scheduled_scan_job():
    db = SessionLocal()
    try:
        repos = db.query(Repository).filter(Repository.is_active == True).all()
        for repo in repos:
            # Obtener la línea base activa
            baseline = db.query(Baseline).filter(
                Baseline.repository_id == repo.id,
                Baseline.status == "ACTIVE"
            ).first()
            
            if baseline:
                try:
                    logger.info(f"Iniciando escaneo programado para repo {repo.id}")
                    run_scan(db, repo.id, baseline.id, initiated_by=None)
                except Exception as e:
                    logger.error(f"Error en escaneo programado del repo {repo.id}: {e}")
    finally:
        db.close()

def start_scheduler():
    # Ejecutar cada 30 minutos
    scheduler.add_job(
        scheduled_scan_job,
        trigger=IntervalTrigger(minutes=30),
        id="fim_scheduled_scan",
        replace_existing=True
    )
    scheduler.start()
    logger.info("APScheduler iniciado (escaneos cada 30 min).")