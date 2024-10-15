from fastapi import FastAPI, Request, Depends, Cookie, HTTPException, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from connexiondb import Connexdb
from cave import Cave
from etageres import Etagere
from bouteille import Bouteille
from libinteractionuser import (
    ajouter_commentaire, supprimer_commentaire, mettre_a_jour_commentaire, recuperer_commentaire,
    ajouter_notes, supprimer_notes, mettre_a_jour_notes, recuperer_notes,
    recuperer_archives
)
from personne import Personne
from datetime import datetime, timedelta

#########################
##### Configuration #####
#########################

app = FastAPI()
templates = Jinja2Templates(directory="templates")
config_db: dict = {
    "host": 'localhost',
    "port": 27018,
    "username": "root",
    "password": "wm7ze*2b"
}
app.secret_key = 'wm7ze*2b'

# Helper function to build cookie data dictionary for templates
def get_user_cookies(login: str = Cookie(None), perm: str = Cookie(None),
                     nom: str = Cookie(None), prenom: str = Cookie(None), email: str = Cookie(None)) -> dict:
    return {
        "login": login,
        "email": email,
        "perm": perm,
        "nom": nom,
        "prenom": prenom
    }

#######################
##### Main Routes #####
#######################

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    return templates.TemplateResponse("index.html", {
        "request": request,
        **user_cookies
    })

#######################
##### User Routes #####
####################

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"]:
        response = RedirectResponse(url="/", status_code=302)
        return response
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/auth", response_class=HTMLResponse)
async def login_post(request: Request, login: str = Form("login"), password: str = Form("password")):
    user = Personne(
        login=login,
        password=password,
        collections="user",
        config_db=config_db
    )
    auth_result = user.auth()

    if auth_result.get("status") == 200:
        user_data = auth_result.get("user_data", {})
        response = RedirectResponse(url="/", status_code=302)
        cookie_options = {
            "httponly": True,
            "samesite": 'Lax',
            "expires": 3600,
            "secure": request.url.scheme == "http"
        }
        for key in ["login", "perm", "email", "nom", "prenom"]:
            response.set_cookie(key=key, value=user_data.get(key, ""), **cookie_options)
        return response

    error_message = "Authentication failed"
    if auth_result["status"] == 401:
        error_message = "Invalid credentials"
    elif auth_result["status"] == 404:
        error_message = "User not found"
    return templates.TemplateResponse("login.html", {"request": request, "error": error_message})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    for key in ["login", "nom", "prenom", "perm"]:
        response.delete_cookie(key=key)
    return response

@app.get("/profil", response_class=HTMLResponse)
async def profil(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if not user_cookies["login"]:
        response = RedirectResponse(url="/login", status_code=302)
        return response
    return templates.TemplateResponse("profil.html", {
        "request": request,
        **user_cookies
    })

#######################
##### Cave Routes #####
#######################

@app.get("/cave", response_class=HTMLResponse)
async def cave(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/login", status_code=302)
    user = Personne(
        login=user_cookies["login"],
        password="",
        nom=user_cookies["nom"],
        prenom=user_cookies["prenom"],
        perm=user_cookies["perm"],
        collections="user",
        config_db=config_db
    )
    caves_response = user.get_caves()
    print("Caves response:", caves_response)
    caves = caves_response.get("data", {})
    print("User caves:", caves)
    return templates.TemplateResponse("cave.html", {
        "request": request,
        **user_cookies,
        "caves": caves
    })

@app.get("/get_caves")
async def get_caves(user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": "error", "message": "User not logged in"}, status_code=401)

    user = Personne(login=user_cookies["login"], config_db=config_db)
    caves = user.get_caves()
    return JSONResponse(content={"caves": caves})

@app.get("/get_etageres/{cave_id}")
async def get_etageres(request: Request, cave_id: str):
    user_cookies = await get_user_cookies(request)
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": "error", "message": "User not logged in"}, status_code=401)

    cave = Cave(id=cave_id, config_db=config_db)
    etageres = cave.get_etageres()
    return JSONResponse(content={"etageres": etageres})

@app.post("/move_bottle")
async def move_bottle(
    request: Request,
    bottle_name: str = Form(...),
    cave: str = Form(...),
    etagere: str = Form(...)
):
    user_cookies = await get_user_cookies(request)
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": "error", "message": "User not logged in"}, status_code=401)

    bottle = Bouteille(nom=bottle_name, config_db=config_db)
    result = bottle.move_bottle(cave, etagere)

    if result["status"] == 200:
        return JSONResponse(content={"status": "success", "message": "Bottle moved successfully"})
    else:
        return JSONResponse(content={"status": "error", "message": result["message"]}, status_code=result["status"])

@app.get("/add_cave", response_class=HTMLResponse)
async def add_cave_form(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("add_cave.html", {
        "request": request,
        **user_cookies
    })

@app.post("/add_cave")
async def add_cave(request: Request, user_cookies: dict = Depends(get_user_cookies),
                   cave_name: str = Form(...), nb_emplacement: int = Form(...)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/login", status_code=302)
    cave = Cave(config_db=config_db, nom=cave_name, nb_emplacement=nb_emplacement)
    result = cave.create_cave(user_cookies["login"])
    if result["status"] == 200:
        return RedirectResponse(url="/cave", status_code=302)
    else:
        return templates.TemplateResponse("add_cave.html", {
            "request": request,
            **user_cookies,
            "error": result["message"]
        })

@app.get("/delete_cave/{cave_name}")
async def delete_cave(cave_name: str, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/login", status_code=302)
    cave = Cave(config_db=config_db, nom=cave_name)
    result = cave.delete_cave(user_cookies["login"])
    return RedirectResponse(url="/cave", status_code=302)

#############################
##### Collection Routes #####
#############################

@app.get("/collection", response_class=HTMLResponse)
async def collection(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/login", status_code=302)
    user = Personne(
        perm = user_cookies["perm"],
        login = user_cookies["login"],
        password = "",
        nom = user_cookies["nom"],
        prenom = user_cookies["prenom"],
        collections="user",
        config_db = config_db
    )
    bottles_response = user.get_bottles()
    print(bottles_response)
    return templates.TemplateResponse("collection.html", {
        "request": request,
        **user_cookies,
        "bouteilles": bottles_response["data"]
    })

@app.post("/add_bottle")
async def add_bottle(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    nom: str = Form("nom"),
    type: str = Form("type"),
    annee: int = Form("annee"),
    region: str = Form("region"),
    prix: float = Form("prix")
):
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": "error", "message": "User not logged in"}, status_code=401)

    user = Personne(
        perm = user_cookies["perm"],
        login = user_cookies["login"],
        password = "",
        nom = user_cookies["nom"],
        prenom = user_cookies["prenom"],
        collections="user",
        config_db = config_db
    )

    new_bottle = Bouteille(
        nom=nom,
        type=type,
        annee=annee,
        region=region,
        prix=prix,
        config_db=config_db
    )

    result = new_bottle.create_bouteille()

    if result["status"] in [200, 201]:  # Accept both 200 and 201 as success
        # Add the bottle to the user's collection using the bottle name
        update_result = user.add_bottle(nom)
        
        if update_result["status"] == 200:
            print(f"Bottle added successfully. Name: {nom}")
            print(user.get())
            return JSONResponse(content={"status": "success", "message": "Bottle added successfully"})
        else:
            print(f"Failed to update user data: {update_result}")
            return JSONResponse(content={"status": "error", "message": "Failed to update user data"}, status_code=500)
    else:
        print(f"Failed to create bottle: {result}")
        return JSONResponse(content={"status": "error", "message": result.get("message", "Failed to add bottle")}, status_code=result["status"])

# Main entry point to run the FastAPI app
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=15000, reload=True)
