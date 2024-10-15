from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Classes import Cave, Personne, Bouteille
from .dependencies import (
    get_user_cookies, 
    config_db, 
    effectuer_operation_db,
    ajouter_commentaire,
    supprimer_commentaire,
    mettre_a_jour_commentaire,
    recuperer_commentaire,
    ajouter_notes,
    supprimer_notes,
    mettre_a_jour_notes,
    recuperer_notes,
    recuperer_archives
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
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

@router.get("/get_caves")
async def get_caves(user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": "error", "message": "User not logged in"}, status_code=401)

    user = Personne(login=user_cookies["login"], config_db=config_db)
    caves = user.get_caves()
    return JSONResponse(content={"caves": caves})

@router.get("/get_etageres/{cave_id}")
async def get_etageres(cave_id: str, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": "error", "message": "User not logged in"}, status_code=401)

    cave = Cave(id=cave_id, config_db=config_db)
    etageres = cave.get_etageres()
    return JSONResponse(content={"etageres": etageres})

@router.get("/add", response_class=HTMLResponse)
async def add_cave_form(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("add_cave.html", {
        "request": request,
        **user_cookies
    })

@router.post("/add")
async def add_cave(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    cave_name: str = Form(...),
    nb_emplacement: int = Form(...)
):
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

@router.get("/delete/{cave_name}")
async def delete_cave(cave_name: str, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/login", status_code=302)
    cave = Cave(config_db=config_db, nom=cave_name)
    result = cave.delete_cave(user_cookies["login"])
    return RedirectResponse(url="/cave", status_code=302)

