from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Classes import Bouteille, Personne
from .dependencies import config_db, get_user_cookies, effectuer_operation_db, ajouter_commentaire, ajouter_notes
from datetime import datetime

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

    if bottle_data.get("status") != 200:
        return templates.TemplateResponse("error.html", {
            "request": request,
            **user_cookies,
            "message": bottle_data.get("message", "Failed to retrieve bottle information"),
        })

    return templates.TemplateResponse("bottle_details.html", {
        "request": request,
        **user_cookies,
        "data": bottle_data["data"]
    })

@router.get("/delete/{nom_bouteille}", response_class=HTMLResponse)
async def del_bouteille(request: Request, nom_bouteille: str, user_cookies: dict = Depends(get_user_cookies)):
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

    if bottle_data.get("status") != 200:
        return templates.TemplateResponse("error.html", {
            "request": request,
            **user_cookies,
            "message": bottle_data.get("message", "Failed to retrieve bottle information"),
        })

    return templates.TemplateResponse("bottle_details.html", {
        "request": request,
        **user_cookies,
        "data": bottle_data["data"]
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


@router.post("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    filtre: str = "",
    user_cookies: dict = Depends(get_user_cookies)
):
    # Transform the filter string into a regex pattern
    regex_pattern = f".*{filtre}.*"  # Automatically wraps the input with '.*' for regex matching

    # Create a query to search for the bottle using the transformed filter
    query: dict = {"nom": {"$regex": regex_pattern, "$options": "i"}}  # Using regex for case-insensitive search
    
    # Call the effectuer_operation_db function to fetch data from the database
    response = effectuer_operation_db(config_db, "bouteille", "get", query=query)
    
    # Check for errors in the response
    if response.get("status") != 200:
        error_message = response.get("message", "Une erreur s'est produite lors de la récupération des bouteilles.")
        return templates.TemplateResponse("search_bouteille.html", {
            "request": request,
            **user_cookies,
            "data": [],  # No data to show in case of an error
            "error_message": error_message  # Pass the error message to the template
        })

    # Extract data from the response if successful
    data = response.get("data", [])

    # Print data for debugging
    print(data)

    # Check if data is empty and prepare the message accordingly
    if not data:
        message = "Aucune bouteille n'a été trouvée pour ce filtre."
    else:
        message = ""

    return templates.TemplateResponse("search_bouteille.html", {
        "request": request,
        **user_cookies,
        "data": data,
        "message": message,  # Pass the message to the template
        "error_message": "",  # Clear error message if there are no errors
        "filtre": filtre
    })

@router.post("/commentandpair", response_class=JSONResponse)
async def comment_and_pair(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    comment: str = Form(...),  # Ensure to use ... to require this field
    rating: float = Form(...),  # Ensure to use ... to require this field
    nom_bouteille: str = Form(...)
):
    if not user_cookies["login"]:
        raise HTTPException(status_code=401, detail="User not logged in")

    # Use the login as the unique identifier for the user
    login = user_cookies["login"]

    # Get the current date in the desired format (e.g., YYYY-MM-DD)
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Add the comment to the database
    comment_response = ajouter_commentaire(config_db, nom_bouteille, comment, login, date=current_date)

    # Check if the comment was added successfully
    if comment_response.get("status") != 200:
        return JSONResponse(content={"status": "error", "message": comment_response.get("message")})

    # Add the rating to the database
    rating_response = ajouter_notes(config_db, nom_bouteille, rating, login)

    # Check if the rating was added successfully
    if rating_response.get("status") != 200:
        return JSONResponse(content={"status": "error", "message": rating_response.get("message")})

    # Redirect to the bottle details page
    return RedirectResponse(url=f"/bottle/{nom_bouteille}", status_code=302)
