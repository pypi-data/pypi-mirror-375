import multiprocessing
import os
import sys

import uvicorn
from gunicorn.app.wsgiapp import run

from .app_factory import create_app


def serve_function(handler, host='0.0.0.0', port=5000):
    app = create_app(handler)

    if os.environ.get("fprocess") == "python main.py" or os.environ.get("OPENFAAS") == "true":
        workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count()))
        sys.argv = [
            "gunicorn",
            "main:app",
            "-k", "uvicorn.workers.UvicornWorker",
            "--workers", str(workers),
            "--threads", os.environ.get("GUNICORN_THREADS", "2"),
            "--bind", f'{host}:{port}',
            "--timeout", "0"
        ]
        run()
        return

    uvicorn.run(app, host=host, port=port)
