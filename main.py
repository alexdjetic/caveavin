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

app = FastAPI()  # Création de l'application FastAPI

# Insertion des routes d'étagère
app.include_router(etagere_router, prefix="/etagere", tags=["etagere"])
templates = Jinja2Templates(directory="templates")  # Configuration du moteur de templates Jinja2
app.secret_key = 'wm7ze*2b'  # Clé secrète pour l'application
app.add_middleware(RequestLoggingMiddleware)  # Ajout du middleware pour l'enregistrement des requêtes

#######################
##### Main Routes #####
#######################

# Insertion des routes utilisateur et cave
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(bouteille_router, prefix="/bottle", tags=["bottle"])
app.include_router(etagere_router, prefix="/etagere", tags=["etagere"])
app.include_router(cave_router, prefix="/cave", tags=["cave"])

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    """
    Route principale qui affiche la page d'accueil.

    Parameters
    ----------
    request : Request
        L'objet de requête FastAPI représentant la requête HTTP entrante.
    user_cookies : dict
        Un dictionnaire contenant les cookies de l'utilisateur.

    Returns
    -------
    HTMLResponse
        La réponse contenant le rendu du template index.html.
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        **user_cookies  # Inclusion des cookies de l'utilisateur dans le contexte du template
    })

@app.get("/error", response_class=HTMLResponse)
async def not_found(request: Request):
    """
    Route qui renvoie une page d'erreur 404.

    Parameters
    ----------
    request : Request
        L'objet de requête FastAPI représentant la requête HTTP entrante.

    Returns
    -------
    HTMLResponse
        La réponse contenant le rendu du template error.html.
    """
    print(f"<!> 404 error for request: {request.method} {request.url}")
    return templates.TemplateResponse("error.html", {"request": request})

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """
    Gestionnaire d'erreur personnalisé pour les erreurs 404.

    Parameters
    ----------
    request : Request
        L'objet de requête FastAPI représentant la requête HTTP entrante.
    exc : Exception
        L'exception levée, ici une erreur 404.

    Returns
    -------
    HTMLResponse
        La réponse contenant le rendu du template error.html avec un statut 404.
    """
    print(f"<!> 404 error for request: {request.method} {request.url} <!>")
    return templates.TemplateResponse("error.html", {"request": request}, status_code=404)

# Définition du gestionnaire d'exception HTTP par défaut
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Gestionnaire d'exception pour les erreurs HTTP.

    Parameters
    ----------
    request : Request
        L'objet de requête FastAPI représentant la requête HTTP entrante.
    exc : HTTPException
        L'exception HTTP levée.

    Returns
    -------
    HTMLResponse
        La réponse contenant le rendu du template error.html avec le code d'état de l'exception.
    """
    return templates.TemplateResponse("error.html", {"request": request}, status_code=exc.status_code)

# Gestionnaire d'erreur personnalisé pour 403 Forbidden
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Gestionnaire d'exception personnalisé pour les erreurs HTTP.

    Parameters
    ----------
    request : Request
        L'objet de requête FastAPI représentant la requête HTTP entrante.
    exc : HTTPException
        L'exception HTTP levée.

    Returns
    -------
    HTMLResponse
        La réponse contenant le rendu du template notallow.html pour les erreurs 403.
        Sinon, utilise le gestionnaire d'exception HTTP par défaut.
    """
    if exc.status_code == 403:
        return templates.TemplateResponse("notallow.html", {"request": request}, status_code=403)
    # Pour d'autres exceptions HTTP, utilise le gestionnaire par défaut
    return await http_exception_handler(request, exc)

# Exemple de route qui génère une erreur 403
@app.get("/restricted")
async def restricted_route():
    """
    Route restreinte qui lève une erreur 403.

    Raises
    ------
    HTTPException
        Une exception HTTP avec un statut 403.
    """
    raise HTTPException(status_code=403, detail="Accès interdit")

# Autres routes et logique de l'application...

# Point d'entrée principal pour exécuter l'application FastAPI
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=15000, reload=True)
