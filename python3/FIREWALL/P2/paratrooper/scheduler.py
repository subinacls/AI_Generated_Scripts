import schedule
import logging
from paratrooper.clientdb import DBHandler

# Setup logger
logger = logging.getLogger(__name__)

def start_clientdb_scheduler():
    """
    Schedules regular saving of the client database.
    """
    db_handler = DBHandler()
    db_handler.open_clientdb()
    schedule.every(1).hour.do(db_handler.save_clientdb)
    logger.info("Client database save scheduled.")
