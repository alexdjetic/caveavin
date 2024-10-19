# route/etagere_route.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from Classes.etageres import Etagere
from route.dependencies import get_user_cookies

router = APIRouter()

@router.get("/get/{num_etagere}&{cave}", response_model=dict)
async def get_etagere(num_etagere: int, cave: str, user_cookies: dict = Depends(get_user_cookies)):
    # Create an instance of Etagere
    etagere = Etagere(num=num_etagere, cave=cave)

    # Fetch the etagere details from the database
    etagere_info = etagere.get_etageres()  # Assuming this method retrieves the etagere details

    if etagere_info.get("status") != 200:
        raise HTTPException(status_code=404, detail="Étagère non trouvée.")

    return JSONResponse(content=etagere_info)

@router.get("/gets/{cave}", response_model=dict)
async def get_all_etageres(cave: str, user_cookies: dict = Depends(get_user_cookies)):
    # Create an instance of Etagere
    etagere = Etagere(cave=cave)

    # Fetch all etageres associated with the cave
    etageres_info = etagere.get_etageres()  # Assuming this method retrieves all etageres for the cave

    if etageres_info.get("status") != 200:
        raise HTTPException(status_code=404, detail="Aucune étagère trouvée pour cette cave.")

    return JSONResponse(content=etageres_info)

@router.delete("/delete/{num_etagere}&{cave}", response_model=dict)
async def delete_etagere(num_etagere: int, cave: str, user_cookies: dict = Depends(get_user_cookies)):
    # Create an instance of Etagere
    etagere = Etagere(num=num_etagere, cave=cave)

    # Delete the etagere
    delete_result = etagere.delete_etageres()

    if delete_result.get("status") != 200:
        raise HTTPException(status_code=404, detail="Étagère non trouvée ou échec de la suppression.")

    return JSONResponse(content=delete_result)

@router.put("/update/{num_etagere}&{cave}", response_model=dict)
async def update_etagere(num_etagere: int, cave: str, etagere_data: Etagere, user_cookies: dict = Depends(get_user_cookies)):
    # Create an instance of Etagere
    etagere = Etagere(num=num_etagere, cave=cave, **etagere_data.model_dump)

    # Update the etagere
    update_result = etagere.update_etageres()

    if update_result.get("status") != 200:
        raise HTTPException(status_code=404, detail="Échec de la mise à jour de l'étagère.")

    return JSONResponse(content=update_result)

