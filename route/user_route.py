from fastapi import APIRouter, Request, Depends, Form, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Classes.personne import Personne
from .dependencies import (
    get_user_cookies, 
    config_db
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
    auth_result: dict = user.auth()

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
    response = RedirectResponse(url="/user/login")
    for key in ["login", "nom", "prenom", "perm"]:
        response.delete_cookie(key=key)
    return response

@router.get("/profil", response_class=HTMLResponse)
async def profil(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if not user_cookies["login"]:
        response = RedirectResponse(url="/user/login", status_code=302)
        return response
    return templates.TemplateResponse("profil.html", {
        "request": request,
        **user_cookies
    })

@router.get("/collection", response_class=HTMLResponse)
async def collection(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)

    user = Personne(
        perm=user_cookies["perm"],
        login=user_cookies["login"],
        password="",  # Password is not needed for fetching caves
        nom=user_cookies["nom"],
        prenom=user_cookies["prenom"],
        collections="user",
        config_db=config_db
    )

    bottles_response = user.get_bottles()  # Fetch reserved bottles
    caves_response = user.get_caves()  # Fetch associated caves

    return templates.TemplateResponse("collection.html", {
        "request": request,
        **user_cookies,
        "bouteilles": bottles_response["data"],
        "caves": caves_response["data"]  # Pass caves data to the template
    })

@router.get("/delete/{user_login}", response_class=HTMLResponse)
async def delete(request: Request, user_login: str, user_cookies: dict = Depends(get_user_cookies)):
    # not working
    if user_cookies["login"] is None:
        return RedirectResponse(url="/", status_code=302)

    user: Personne = Personne(
        login=user_login,
        config_db=config_db,
        collections="user"
    )

    # check user exist first
    user_data: dict = user.get()

    if user_data.get("status") != 200:
        return {
            "message": "l'utilisateur n'éxiste pas dans la base de donnée",
            "status_code": 403
        }

    # delete from database
    user.delete()

    # unset all cookie var
    response = RedirectResponse(url="/user/logout", status_code=302)
    return response


@router.get("/create/", response_class=HTMLResponse)
async def create(request: Request, user_cookies: dict = Depends(get_user_cookies), error: str = None):
    return templates.TemplateResponse("create_user.html", {"request": request, "error": error})


@router.post("/create/", response_class=HTMLResponse)
async def create_post(request: Request,
                     login: str = Form("login"),
                     password: str = Form("password"),
                     nom: str = Form("nom"),
                     prenom: str = Form("prenom"),
                     perm: str = Form("perm"),
                     email: str = Form("email"),
                     user_cookies: dict = Depends(get_user_cookies)):

    user: Personne = Personne(
        login=str(login),
        password=str(password),
        nom=str(nom),
        prenom=str(prenom),
        perm=str(perm),
        email=str(email),
        config_db=config_db,
        collections="user"
    )

    rstatus: dict = user.create()

    print(rstatus)

    if rstatus.get("status") != 200:
        error_message = rstatus.get("message", rstatus.get("message"))
        return templates.TemplateResponse("create_user.html", {"request": request, "error": error_message})

    if user_cookies["login"] is None:
        response = RedirectResponse(url="/user/login", status_code=302)
        return response

    response = RedirectResponse(url="/", status_code=302)
    return response

@router.get("/update", response_class=HTMLResponse)
async def update(request: Request, user_cookies: dict = Depends(get_user_cookies), error: str = None):
    return templates.TemplateResponse("update_user.html", {"request": request, "error": error, **user_cookies})

@router.post("/update", response_class=HTMLResponse)
async def update_post(request: Request,
                     login: str = Form("login"),
                     password: str = Form("password"),
                     nom: str = Form("nom"),
                     prenom: str = Form("prenom"),
                     perm: str = Form("perm"),
                     email: str = Form("email"),
                     user_cookies: dict = Depends(get_user_cookies)):

    if user_cookies["login"] is None:
        response = RedirectResponse(url="/user/login", status_code=302)
        return response

    user: Personne = Personne(
        login=str(login),
        nom=str(nom),
        prenom=str(prenom),
        perm=str(perm),
        email=str(email),
        config_db=config_db,
        collections="user"
    )

    if password:
        user.password = password

    rstatus: dict = user.update_user_info()

    print(rstatus)

    cookie_options = {
        "httponly": True,
        "samesite": 'Lax',
        "expires": 3600,
        "secure": request.url.scheme == "https"
    }

    # update cookie
    response = RedirectResponse(url="/user/profil", status_code=302)
    response.set_cookie(key="nom", value=nom, **cookie_options)
    response.set_cookie(key="prenom", value=prenom, **cookie_options)
    response.set_cookie(key="perm", value=perm, **cookie_options)
    response.set_cookie(key="email", value=email, **cookie_options)
    return response
