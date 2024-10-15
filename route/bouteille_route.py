from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Classes import Bouteille, Personne
from .dependencies import config_db, get_user_cookies

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/add", response_class=JSONResponse)
async def add_bouteille(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    nom: str = Form(...),
    type: str = Form(...),
    annee: int = Form(...),
    region: str = Form(...),
    prix: float = Form(...)
):
    if not user_cookies["login"]:
        raise HTTPException(status_code=401, detail="User not logged in")

    user = Personne(
        login=user_cookies["login"],
        password="",
        nom=user_cookies["nom"],
        prenom=user_cookies["prenom"],
        perm=user_cookies["perm"],
        collections="user",
        config_db=config_db
    )

    bouteille = Bouteille(
        nom=nom,
        type=type,
        annee=annee,
        region=region,
        prix=prix,
        config_db=config_db
    )

    result = user.add_bouteille(bouteille)

    if result.get("status") == 200:
        return JSONResponse(content={"status": "success", "message": "Bottle added successfully"})
    else:
        return JSONResponse(content={"status": "error", "message": result.get("message", "Failed to add bottle")})

@router.get("/{nom_bouteille}", response_class=HTMLResponse)
async def get_bouteille(request: Request, nom_bouteille: str, user_cookies: dict = Depends(get_user_cookies)):
    if not user_cookies["login"]:
        return RedirectResponse(url="/user/login", status_code=302)

    bouteille = Bouteille(nom=nom_bouteille, config_db=config_db)
    bottle_data = bouteille.get_details()

    return templates.TemplateResponse("bottle_details.html", {
        "request": request,
        **user_cookies,
        "bouteille": bottle_data
    })

@router.post("/move", response_class=JSONResponse)
async def move_bouteille(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    bottle_name: str = Form(...),
    cave: str = Form(...),
    etagere: str = Form(...)
):
    if not user_cookies["login"]:
        raise HTTPException(status_code=401, detail="User not logged in")

    bouteille = Bouteille(nom=bottle_name, config_db=config_db)
    result = bouteille.move_bottle(cave, etagere)

    if result.get("status") == 200:
        return JSONResponse(content={"status": "success", "message": "Bottle moved successfully"})
    else:
        return JSONResponse(content={"status": "error", "message": result.get("message", "Failed to move bottle")})

# Add more bottle-related routes as needed

