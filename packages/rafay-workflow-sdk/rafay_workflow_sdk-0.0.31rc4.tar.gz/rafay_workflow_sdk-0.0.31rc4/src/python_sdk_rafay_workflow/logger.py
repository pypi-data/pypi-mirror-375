import logging
import os
import sys

from fastapi import Request

from .activity_logger import ActivityLogHandler
from .const import *

FUNCTION_NAME = os.environ.get('FUNCTION_NAME', 'default-function-name')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_BUFFER_CAPACITY = int(os.environ.get('LOG_BUFFER_CAPACITY', "10"))
LOG_FLUSH_TIMEOUT = int(os.environ.get('LOG_FLUSH_TIMEOUT', "10"))
SKIP_TLS_VERIFY = os.environ.get('skip_tls_verify', "false")

_format = "time=%(asctime)s level=%(levelname)s path=%(pathname)s line=%(lineno)d msg=%(message)s"
_logger = logging.Logger(FUNCTION_NAME)
_handler = logging.StreamHandler(stream=sys.stdout)
_formatter = logging.Formatter(_format)
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)
_handler.setLevel(LOG_LEVEL)


# TODO: check this with new ActivityLogHandler
def log(f):
    async def wrap(request: Request, *args, **kwargs):
        activity_id = request.headers.get(ActivityIDHeader, "")
        environment_id = request.headers.get(EnvironmentIDHeader, "")
        environment_name = request.headers.get(EnvironmentNameHeader, "")
        engine_endpoint = request.headers.get(EngineAPIEndpointHeader)
        file_upload_path = request.headers.get(ActivityFileUploadHeader)

        logger = logging.Logger(activity_id)
        extra = {
            "activity_id": activity_id,
            "environment_id": environment_id,
            "environment_name": environment_name,
        }

        token = request.headers.get(WorkflowTokenHeader)

        endpoint = engine_endpoint + file_upload_path
        logging_handler = ActivityLogHandler(endpoint=endpoint, token=token, capacity=LOG_BUFFER_CAPACITY,
                                             timeout=LOG_FLUSH_TIMEOUT, verify=(SKIP_TLS_VERIFY != "true"))
        logging_handler.setFormatter(logging.Formatter(_format))
        logger.setLevel(LOG_LEVEL)
        logger.addHandler(logging_handler)

        log_format = "time=%(asctime)s level=%(levelname)s path=%(pathname)s line=%(lineno)d environment_name=%(environment_name)s environment_id=%(environment_id)s activity_id=%(activity_id)s  msg=%(message)s"
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.setFormatter(logging.Formatter(log_format))

        logger.addHandler(stdout_handler)
        logger.info(f"invoking function: {FUNCTION_NAME}", extra=extra)

        resp = await f(request=request, logger=logging.LoggerAdapter(logger, extra), *args, **kwargs)
        
        await logging_handler.async_flush()
        await logging_handler.close()
        stdout_handler.close()
        return resp

    return wrap