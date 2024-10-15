from fastapi import FastAPI, Request, Depends, Cookie, HTTPException, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

from connexiondb import Connexdb
from usager import Usager
from proprietaire import Proprietaire
from cave import Cave
from etageres import Etagere
from bouteille import Bouteille
from libinteractionuser import (
    ajouter_commentaire,supprimer_commentaire, mettre_a_jour_commentaire, recuperer_commentaire,
    ajouter_notes, supprimer_notes, mettre_a_jour_notes, recuperer_notes,
    recuperer_archives
)


app = FastAPI()
templates = Jinja2Templates(directory="templates")
config_db: dict = {
    "host": 'localhost',
    "port": 27018,
    "username": "root",
    "password": "wm7ze*2b"
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, login: str = Cookie(None)):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/collection", response_class=HTMLResponse)
async def collection(request: Request, login: str = Cookie(None)):
    return templates.TemplateResponse("collection.html", {"request": request})

@app.get("/cave", response_class=HTMLResponse)
async def cave(request: Request, login: str = Cookie(None)):
    return templates.TemplateResponse("cave.html", {"request": request})

@app.get("/profil", response_class=HTMLResponse)
async def profil(request: Request, login: str = Cookie(None)):
    if not login:
        response = RedirectResponse(url="/login", status_code=302)
        return response

    return templates.TemplateResponse("profil.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request, login: str = Cookie(None)):
    if login:
        response = RedirectResponse(url="/", status_code=302)
        return response

    return templates.TemplateResponse("login.html", {"request" : request})


@app.post("/auth", response_class=HTMLResponse)
async def auth_post(request: Request, login: str = Form("login"), password: str = Form("password")):
    # Placeholder for authentication logic
    if login != "admin" or password != "password":  # Replace this with real authentication logic
        error = "Invalid username or password"
        return templates.TemplateResponse("login.html", {"request": request, "error": error})

    # If authentication is successful
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="num", value="test")
    response.set_cookie(key="login", value=login)
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="login")
    response.delete_cookie(key="num")
    return response



# Main entry point to run the FastAPI app
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=15000, reload=True)
