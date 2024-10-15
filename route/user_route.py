from fastapi import APIRouter, Request, Depends, Form, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Classes.personne import Personne
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


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"]:
        response = RedirectResponse(url="/", status_code=302)
        return response
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/auth", response_class=HTMLResponse)
async def login_post(request: Request, login: str = Form(...), password: str = Form(...)):
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
            "secure": request.url.scheme == "https"
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

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    for key in ["login", "nom", "prenom", "perm"]:
        response.delete_cookie(key=key)
    return response

@router.get("/profil", response_class=HTMLResponse)
async def profil(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if not user_cookies["login"]:
        response = RedirectResponse(url="/login", status_code=302)
        return response
    return templates.TemplateResponse("profil.html", {
        "request": request,
        **user_cookies
    })
