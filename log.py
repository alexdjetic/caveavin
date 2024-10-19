from fastapi import FastAPI, Request
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

   
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()  # Start timing

        # Log the request details
        logger.info(f"Request: {request.method} {request.url}")
        logger.info(f"Request Headers: {request.headers}")

        # Log the request body if it's a POST or PUT request
        if request.method in ["POST", "PUT"]:
            body = await request.body()
            logger.info(f"Request Body: {body.decode('utf-8')}")

        # Process the request
        response = await call_next(request)

        # Log the response status and headers
        logger.info(f"Response Status: {response.status_code}")
        logger.info(f"Response Headers: {response.headers}")

        # Log the execution time
        duration = time.time() - start_time
        logger.info(f"Processed {request.method} {request.url} in {duration:.2f} seconds")

        return response

