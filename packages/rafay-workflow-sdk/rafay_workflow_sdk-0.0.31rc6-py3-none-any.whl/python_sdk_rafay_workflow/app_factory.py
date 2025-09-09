import asyncio
import inspect
import json
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .activity_logger import ActivityLogHandler
from .const import *
from .errors import *
from .logger import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    yield
    # Shutdown phase
    for handler in app.logger.handlers:
        if isinstance(handler, ActivityLogHandler):
            await handler.close()


def create_app(handler):
    app = FastAPI(title=os.environ.get('FUNCTION_NAME', 'default-function-name'), lifespan=lifespan)

    # Configure a thread pool for sync handlers
    app.state.executor = ThreadPoolExecutor(
        max_workers=int(os.environ.get("MAX_WORKERS", "50"))
    )

    @app.post("/")
    @log
    async def handle(request: Request, logger=None):
        try:
            payload = await request.json()
                
            payload["metadata"] = {
                "activityID": request.headers.get(ActivityIDHeader),
                "environmentID": request.headers.get(EnvironmentIDHeader),
                "environmentName": request.headers.get(EnvironmentNameHeader),
            }

            # If the handler is async → await it directly
            if inspect.iscoroutinefunction(handler):
                resp = await handler(logger, payload)
            else:
                # If the handler is sync → run it in a thread pool
                loop = asyncio.get_running_loop()
                resp = await loop.run_in_executor(
                    app.state.executor,
                    handler,
                    logger,
                    payload,
                )
            return {"data": resp}

        except ExecuteAgainException as e:
            return JSONResponse(e.__dict__, 500)
        except FailedException as e:
            return JSONResponse(e.__dict__, 500)
        except TransientException as e:
            return JSONResponse(e.__dict__, 500)
        except Exception as e:
            return JSONResponse(
                content={"error_code": ERROR_CODE_FAILED, "message": str(e)},
                status_code=500,
            )

    @app.get("/_/ready")
    async def ready():
        return {"status": "ready"}

    return app
