from fastapi import FastAPI

from app.handlers.exceptions import APIException, api_exception_handler
from app.views.routes import router

description = """A REST API for JSON content with zero coding.

Technologies::
* Python 3.13
* FastAPI 0.116
"""
app = FastAPI(
    version="1.4.0",
    title="Yet Another JSON Server",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    contact={
        "name": "Adriano Vieira",
        "url": "https://www.adrianovieira.eng.br/",
    },
    description=description,
    openapi_tags=[{"name": "API"}],
)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(FileNotFoundError, api_exception_handler)
app.add_exception_handler(NotImplementedError, api_exception_handler)
app.add_exception_handler(Exception, api_exception_handler)

app.include_router(router)
