import multiprocessing
import os

import uvicorn

from .app_factory import create_app


def serve_function(handler, host='0.0.0.0', port=5000):
    app = create_app(handler)

    # For production/OpenFaaS environments, use gunicorn with uvicorn workers
    if os.environ.get("fprocess") == "python main.py" or os.environ.get("OPENFAAS") == "true":
        from gunicorn.app.base import BaseApplication
        
        class StandaloneApplication(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        options = {
            'bind': f'{host}:{port}',
            'workers': int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count())),
            'worker_class': 'uvicorn.workers.UvicornWorker',
            'threads': int(os.environ.get("GUNICORN_THREADS", "2")),
            'timeout': 0,
        }
        
        StandaloneApplication(app, options).run()
        return

    # For development, use uvicorn directly
    uvicorn.run(app, host=host, port=port)
