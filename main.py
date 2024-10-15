from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from route.user_route import router as user_router
from route.cave_route import router as cave_router
from route.bouteille_route import router as bouteille_router
from route.dependencies import get_user_cookies, config_db

#########################
##### Configuration #####
#########################

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.secret_key = 'wm7ze*2b'

#######################
##### Main Routes #####
#######################

# Include the user and cave routes
app.include_router(user_router, prefix="/user")
app.include_router(cave_router, prefix="/cave")
app.include_router(bouteille_router, prefix="/bottle")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    return templates.TemplateResponse("index.html", {
        "request": request,
        **user_cookies
    })


# Main entry point to run the FastAPI app
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=15000, reload=True)
