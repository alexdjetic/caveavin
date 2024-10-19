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
    print("\n<!> add_cave_get route accessed <!>\n")

    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)

    # Directly render the add cave form without checking for existing cave data
    return templates.TemplateResponse("add_cave.html", {
        "request": request,
        **user_cookies
    })

@router.get("/", response_class=HTMLResponse)
async def cave_index(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)
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
    caves = caves_response.get("data", {})
    return templates.TemplateResponse("cave.html", {
        "request": request,
        **user_cookies,
        "caves": caves
    })


@router.get("/{nom_cave}", response_class=HTMLResponse)
async def cave_details(request: Request, nom_cave: str, user_cookies: dict = Depends(get_user_cookies)):
    print(f"\n<!> cave_details route accessed for {nom_cave} <!>\n")

    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)
    
    # Create an instance of the Cave class
    cave_instance: Cave = Cave(
        nom=nom_cave,
        config_db=config_db
    )

    # Retrieve cave details from the database
    cave_info = cave_instance.get_cave()  # Assuming this method retrieves the cave details
    print(f"<!> get_cave method called <!>")  # Debugging line

    if cave_info.get("status") != 200:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Cave non trouvée."})

    # Prepare the data for rendering
    cave_data = cave_info['data']
    
    # Fetch the shelves (etagere) associated with the cave
    etageres_info = cave_instance.get_etageres() 

    print(f"information étagère: {etageres_info}")

    if etageres_info.get("status") != 200:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Étagères non trouvées."})

    # Combine cave data and shelves data
    cave_data['etageres'] = etageres_info['data']

    # Render the cave details template
    return templates.TemplateResponse("cave_details.html", {"request": request, "data": cave_data,**user_cookies})

@router.post("/add_etagere")
async def add_etagere(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    nom_cave: str = Form("nom_cave"),
    num_etagere: int = Form("num_etagere"),
    nb_place: int = Form("nb_place")
):
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": 401, "message": "User not logged in"}, status_code=401)
    
    if num_etagere <= 0 or nb_place <= 0:
        raise HTTPException(status_code=400, detail="num_etagere and nb_place must be positive integers.")

    # Create an instance of the Cave class
    cave: Cave = Cave(config_db=config_db, nom=nom_cave)

    # Create an instance of the Etagere class
    etagere: Etagere = Etagere(num=num_etagere, nb_place=nb_place, cave=nom_cave, config_db=config_db)

    # Add the etagere to the cave
    result: dict = cave.add_etagere(etagere)

    if result.get("status") == 200:
        return JSONResponse(content={"status": "success", "message": "Étagère ajoutée avec succès."})
    else:
        return JSONResponse(content={"status": "error", "message": result["message"]}, status_code=400)

@router.get("/get_caves")
async def get_caves_get_api_json(user_cookies: dict = Depends(get_user_cookies)):
    print("get_caves route called")
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": "error", "message": "User not logged in"}, status_code=401)

    user = Personne(login=user_cookies["login"], config_db=config_db)
    caves = user.get_caves()
    return JSONResponse(content={"caves": caves})

@router.get("/get_etageres/{cave_id}")
async def get_etageres(cave_id: str, user_cookies: dict = Depends(get_user_cookies)):
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": "error", "message": "User not logged in"}, status_code=401)

    cave: Cave = Cave(id=cave_id, config_db=config_db)
    etageres = cave.get_etageres()
    return JSONResponse(content={"etageres": etageres})
    
@router.post("/add-cave")
async def add_cave(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    cave_name: str = Form("cave_name"),
    nb_emplacement: int = Form("nb_emplacement")
):
    print("\n<!> add_cave_post route accessed <!>\n")

    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)
    cave: Cave = Cave(config_db=config_db, nom=cave_name, nb_emplacement=nb_emplacement)
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
        return RedirectResponse(url="/user/login", status_code=302)
    cave: Cave = Cave(config_db=config_db, nom=cave_name)
    result = cave.delete_cave(user_cookies["login"])
    return RedirectResponse(url="/cave", status_code=302)
