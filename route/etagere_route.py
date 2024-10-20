# route/etagere_route.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from Classes.etageres import Etagere
from route.dependencies import get_user_cookies, config_db
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def check_login(user_cookies: dict):
    """Check if the user is logged in."""
    if user_cookies.get("login") is None:
        raise HTTPException(status_code=403, detail="User not logged in.")

@router.get("/", response_class=HTMLResponse)
async def manage_etageres(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    check_login(user_cookies)  # Check if the user is logged in
    
    login = user_cookies.get("login")  # Get the user's login from cookies
    etagere = Etagere(config_db=config_db, login=login)  # Pass login to the Etagere instance
    etageres_info = etagere.get_etageres()  # Call without arguments

    if etageres_info.get("status") != 200:
        raise HTTPException(status_code=404, detail="Aucune étagère trouvée.")

    return templates.TemplateResponse("etagere.html", {
        "request": request,
        "etageres": etageres_info['data'],  # Pass the list of etageres to the template
        **user_cookies
    })

@router.delete("/delete/{num_etagere}", response_model=dict)
async def delete_etagere(num_etagere: int, cave: str, user_cookies: dict = Depends(get_user_cookies)):
    check_login(user_cookies)  # Check if the user is logged in

    login = user_cookies.get("login")  # Get the user's login from cookies
    etagere = Etagere(num=num_etagere, cave=cave, login=login, config_db=config_db)  # Create an instance of Etagere

    # Delete the etagere
    delete_result = etagere.delete_etageres()

    if delete_result.get("status") != 200:
        raise HTTPException(status_code=404, detail="Étagère non trouvée ou échec de la suppression.")

    return JSONResponse(content=delete_result)

@router.get("/get/{num_etagere}", response_model=dict)
async def get_etagere(num_etagere: int, user_cookies: dict = Depends(get_user_cookies)):
    check_login(user_cookies)  # Check if the user is logged in

    login = user_cookies.get("login")  # Get the user's login from cookies
    etagere = Etagere(num=num_etagere, login=login, config_db=config_db)  # Create an instance of Etagere

    # Fetch the etagere details from the database
    etagere_info = etagere.get_etageres()  # Assuming this method retrieves the etagere details

    if etagere_info.get("status") != 200:
        raise HTTPException(status_code=404, detail="Étagère non trouvée.")

    return JSONResponse(content=etagere_info)

@router.get("/gets/", response_model=dict)
async def get_all_etageres(user_cookies: dict = Depends(get_user_cookies)):
    check_login(user_cookies)  # Check if the user is logged in

    login = user_cookies.get("login")  # Get the user's login from cookies
    etagere = Etagere(login=login, config_db=config_db)  # Create an instance of Etagere

    etageres_info = etagere.get_etageres()  # Assuming this method retrieves all etageres

    if etageres_info.get("status") != 200:
        raise HTTPException(status_code=404, detail="Aucune étagère trouvée.")

    return JSONResponse(content=etageres_info)

@router.put("/update/{num_etagere}", response_model=dict)
async def update_etagere(num_etagere: int, etagere_data: Etagere, user_cookies: dict = Depends(get_user_cookies)):
    check_login(user_cookies)  # Check if the user is logged in

    login = user_cookies.get("login")  # Get the user's login from cookies
    etagere = Etagere(num=num_etagere, login=login, **etagere_data.model_dump)  # Create an instance of Etagere

    # Update the etagere
    update_result = etagere.update_etageres()

    if update_result.get("status") != 200:
        raise HTTPException(status_code=404, detail="Échec de la mise à jour de l'étagère.")

    return JSONResponse(content=update_result)
