from fastapi import APIRouter, Request, Depends, Form, HTTPException, Body
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Classes import Cave, Personne, Etagere
from .dependencies import (
    get_user_cookies, 
    config_db
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Define the add cave route before the dynamic route
@router.get("/add-cave", response_class=HTMLResponse)
async def add_cave_form_html(request: Request, user_cookies: dict = Depends(get_user_cookies)):

    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)

    # Directly render the add cave form without checking for existing cave data
    return templates.TemplateResponse("add_cave.html", {
        "request": request,
        **user_cookies
    })

@router.post("/add-etagere", response_class=JSONResponse)
async def add_etagere(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    nom_cave: str = Body(...), # ... rend le paramètre obligatoire à donner
    num_etagere: int = Body(...),
    nb_place: int = Body(...)
):
    # Check if the user is logged in
    if user_cookies.get("login") is None:
        return JSONResponse(content={"status": 401, "message": "User not logged in"}, status_code=401)

    # Validate num_etagere and nb_place as positive integers
    if num_etagere <= 0 or nb_place <= 0:
        return JSONResponse(content={"status": 400, "message": "num_etagere and nb_place must be positive integers."}, status_code=400)
    
    # Check if the cave exists
    cave = Cave(config_db=config_db, nom=nom_cave)
    cave_info = cave.get_cave()

    if cave_info.get("status") != 200:
        return JSONResponse(content={"status": 404, "message": "Cave not found."}, status_code=404)

    # Create the etagere and add it to the cave
    etagere = Etagere(num=num_etagere, nb_place=nb_place, cave=nom_cave, config_db=config_db)
    result = cave.add_etagere(etagere)

    # Return success or error based on the result
    if result.get("status") == 200:
        return JSONResponse(content={"status": "success", "message": "Étagère ajoutée avec succès."})
    else:
        return JSONResponse(content={"status": "error", "message": result.get("message")}, status_code=400)

@router.get("/get-etageres/{cave_id}")
async def get_etageres(cave_id: str, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": "error", "message": "User not logged in"}, status_code=401)

    cave: Cave = Cave(id=cave_id, config_db=config_db)
    etageres = cave.get_etageres()
    return JSONResponse(content={"etageres": etageres})
    
@router.post("/add-cave", response_class=JSONResponse)
async def add_cave(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    cave_name: str = Form(...),
    nb_emplacement: int = Form(...)
):
    if user_cookies.get("login") is None:
        return JSONResponse(content={"status": 401, "message": "Utilisateur non connecté"}, status_code=401)

    cave = Cave(config_db=config_db, nom=cave_name, nb_emplacement=nb_emplacement)
    result = cave.create_cave(user_cookies["login"])

    if result["status"] == 200:
        return JSONResponse(content={"status": "success", "message": "Cave créée avec succès."})
    else:
        return JSONResponse(content={"status": "error", "message": result["message"]}, status_code=400)

@router.delete("/delete/{cave_name}", response_model=dict)
async def delete_cave(cave_name: str, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)
    cave: Cave = Cave(config_db=config_db, nom=cave_name)
    result = cave.delete_cave(user_cookies["login"])

    if result.get("stay") != 200:
        raise HTTPException(status_code=404, detail="Cave not found")

    return {"status": "success", "message": "Cave deleted successfully"}

@router.get("/get/{nom_cave}", response_class=HTMLResponse)
async def cave_details(request: Request, nom_cave: str, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)
    
    # Create an instance of the Cave class
    cave: Cave = Cave(
        nom=nom_cave,
        config_db=config_db
    )

    # Retrieve cave details from the database
    cave_info = cave.get_cave() # Assuming this method retrieves the cave details

    if cave_info.get("status") != 200:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Cave non trouvée."})

    # Prepare the data for rendering
    cave_data = cave_info['data']
    
    print(cave_data)

    # Render the cave details template
    return templates.TemplateResponse("cave_details.html", {"request": request, "data": cave_data, **user_cookies})
