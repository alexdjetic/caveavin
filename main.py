from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from route.user_route import router as user_router
from route.cave_route import router as cave_router
from route.bouteille_route import router as bouteille_router
from route.etagere_route import router as etagere_router
from route.dependencies import get_user_cookies, config_db
from log import RequestLoggingMiddleware
import logging

#########################
##### Configuration #####
#########################

app = FastAPI()

# Include the etagere routes
app.include_router(etagere_router, prefix="/etagere", tags=["etagere"])
templates = Jinja2Templates(directory="templates")
app.secret_key = 'wm7ze*2b'
app.add_middleware(RequestLoggingMiddleware)

#######################
##### Main Routes #####
#######################

# Include the user and cave routes
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(bouteille_router, prefix="/bottle", tags=["bottle"])
app.include_router(etagere_router, prefix="/etagere", tags=["etagere"])
app.include_router(cave_router, prefix="/cave", tags=["cave"])


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    return templates.TemplateResponse("index.html", {
        "request": request,
        **user_cookies
    })


@app.get("/error", response_class=HTMLResponse)
async def not_found(request: Request):
    print(f"<!> 404 error for request: {request.method} {request.url}")
    return templates.TemplateResponse("error.html", {"request": request})


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    print(f"<!> 404 error for request: {request.method} {request.url} <!>")
    return templates.TemplateResponse("error.html", {"request": request}, status_code=404)

# Define the default HTTP exception handler
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {"request": request}, status_code=exc.status_code)

# Custom error handler for 403 Forbidden
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 403:
        return templates.TemplateResponse("notallow.html", {"request": request}, status_code=403)
    # For other HTTP exceptions, use the default handler
    return await http_exception_handler(request, exc)

# Example route that raises a 403 error
@app.get("/restricted")
async def restricted_route():
    raise HTTPException(status_code=403, detail="Access forbidden")

# Other routes and application logic...

# Main entry point to run the FastAPI app
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=15000, reload=True)
