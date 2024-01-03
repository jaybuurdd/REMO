import remo
from services.database import config_rds_db
from services.logging import config_logging


config_logging()
db = config_rds_db()
# run the bot
remo.run_remo_bot()