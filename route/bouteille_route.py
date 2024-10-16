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
    nom: str = Form("nom"),
    type: str = Form("type"),
    annee: int = Form("annee"),
    region: str = Form("region"),
    prix: float = Form("prix")
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

    # Create the bottle
    rstatus: dict = bouteille.create()

    print(rstatus)

    if rstatus.get("status") != 200:
        return {
            "message": rstatus.get("message"),
            "status": rstatus.get("status")
        }

    # Add the bottle to the user's reserved bottles
    result = user.add_bottle(nom)

    print(result)

    if result.get("status") == 200:
        return JSONResponse(content={"status": "success", "message": "Bottle added successfully"})
    else:
        return JSONResponse(content={"status": "error", "message": result.get("message", "Failed to add bottle")})

@router.get("/{nom_bouteille}", response_class=HTMLResponse)
async def get_bouteille(request: Request, nom_bouteille: str, user_cookies: dict = Depends(get_user_cookies)):
    if not user_cookies["login"]:
        return RedirectResponse(url="/user/login", status_code=302)

    bouteille = Bouteille(nom=nom_bouteille, config_db=config_db)
    bottle_data = bouteille.get_all_information()

    return templates.TemplateResponse("bottle_details.html", {
        "request": request,
        **user_cookies,
        "data": bottle_data["data"]
    })

@router.get("/delete/{nom_bouteille}", response_class=HTMLResponse)
async def get_bouteille(request: Request, nom_bouteille: str, user_cookies: dict = Depends(get_user_cookies)):
    if not user_cookies["login"]:
        return RedirectResponse(url="/user/login", status_code=302)

    bouteille = Bouteille(nom=nom_bouteille, config_db=config_db)
    bottle_data = bouteille.delete()

    if bottle_data.get("status") != 200:
        return {
            "message": f"La suppression de la bouteille à échoué !",
            "status": bottle_data.get("status")
        }

    return RedirectResponse(url="/user/collection", status_code=302)


@router.get("/update/{nom_bouteille}", response_class=HTMLResponse)
async def get_update_bouteille(request: Request, nom_bouteille: str, user_cookies: dict = Depends(get_user_cookies)):
    if not user_cookies["login"]:
        return RedirectResponse(url="/user/login", status_code=302)

    bouteille = Bouteille(nom=nom_bouteille, config_db=config_db)
    bottle_data = bouteille.get_all_information()

    if bottle_data.get("status") != 200:
        return templates.TemplateResponse("error.html", {
            "request": request,
            **user_cookies,
            "message": "Failed to retrieve bottle information",
        })

    return templates.TemplateResponse("update_bouteille.html", {
        "request": request,
        **user_cookies,
        "bouteille": bottle_data["data"]
    })


@router.post("/update/{nom_bouteille}", response_class=JSONResponse)
async def post_update_bouteille(
    request: Request,
    nom_bouteille: str,
    user_cookies: dict = Depends(get_user_cookies),
    type: str = Form("type"),
    annee: int = Form("annee"),
    region: str = Form("region"),
    prix: float = Form("prix")
):
    if not user_cookies["login"]:
        raise HTTPException(status_code=401, detail="User not logged in")

    bouteille = Bouteille(
        nom=nom_bouteille,
        config_db=config_db
    )

    data: dict = {
        "type": type,
        "annee": annee,
        "region": region,
        "prix": prix
    }

    # Update the bouteille with the new details
    update_status = bouteille.update(data)

    if update_status.get("status") != 200:
        return JSONResponse(content={"status": "error", "message": "Failed to update bottle"})

    return RedirectResponse(url="/user/collection", status_code=302)


@router.get("/{nom_bouteille}", response_class=HTMLResponse)
async def get_bouteille(request: Request, nom_bouteille: str, user_cookies: dict = Depends(get_user_cookies)):
    if not user_cookies["login"]:
        return RedirectResponse(url="/user/login", status_code=302)

    bouteille = Bouteille(nom=nom_bouteille, config_db=config_db)
    bottle_data = bouteille.get_all_information()

    return templates.TemplateResponse("bottle_details.html", {
        "request": request,
        **user_cookies,
        "data": bottle_data
    })

@router.post("/move", response_class=JSONResponse)
async def move_bouteille(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    bottle_name: str = Form(...),
    nom_cave: str = Form(...),
    num_etagere: str = Form(...)
):
    if not user_cookies["login"]:
        raise HTTPException(status_code=401, detail="User not logged in")

    bouteille = Bouteille(nom=bottle_name, config_db=config_db)
    result = bouteille.move_bottle(nom_cave, num_etagere)

    if result.get("status") == 200:
        return JSONResponse(content={"status": "success", "message": "Bottle moved successfully"})
    else:
        return JSONResponse(content={"status": "error", "message": result.get("message", "Failed to move bottle")})
