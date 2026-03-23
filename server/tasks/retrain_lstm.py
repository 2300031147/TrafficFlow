import logging
import asyncio
from server.ml.lstm.trainer import LSTMTrainer
from server.tasks.celery_app import celery_app
from server.db.queries.junctions import get_all_junctions

logger = logging.getLogger(__name__)

@celery_app.task
def retrain_lstm_all_junctions():
    """Iterates through active junctions triggering individual offline modeling runs."""
    logger.info("Executing nightly retrain_lstm CRON task.")
    
    # L6, H2, H3: Run loop in worker thread using asyncio.run
    junctions = asyncio.run(get_all_junctions([]))
    for j in junctions:
        LSTMTrainer(j['id']).train()
