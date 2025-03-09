import sys
from loguru import logger
from app.config.app_settings import settings


# remove previous log handler to keep only our custom handler
logger.remove(0)

# Add the custom logger handler
logger_settings = settings.logger.model_dump()
res = logger.add(sink=sys.stderr, **logger_settings)

logger.debug("Logger configured successfully")
