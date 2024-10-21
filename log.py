from fastapi import FastAPI, Request
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware

# Configuration de base du logger pour afficher les messages d'information
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour enregistrer les détails des requêtes et des réponses.

    Ce middleware enregistre les informations sur les requêtes entrantes, 
    y compris les en-têtes, le corps, le statut de la réponse et le temps d'exécution.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Intercepte la requête, enregistre les détails, et traite la réponse.

        Parameters
        ----------
        request : Request
            L'objet de requête FastAPI représentant la requête HTTP entrante.
        call_next : Callable
            Fonction qui traite la requête et retourne la réponse.

        Returns
        -------
        Response
            La réponse HTTP retournée après le traitement de la requête.
        """
        start_time = time.time()  # Démarre le chronomètre pour le temps de traitement

        # Enregistre les détails de la requête
        logger.info(f"Request: {request.method} {request.url}")
        logger.info(f"Request Headers: {request.headers}")

        # Enregistre le corps de la requête pour les méthodes POST, PUT, et DELETE
        if request.method in ["POST", "PUT", "DELETE"]:
            body = await request.body()
            logger.info(f"Request Body: {body.decode('utf-8')}")

        # Traite la requête en appelant la fonction suivante dans la chaîne de middleware
        response = await call_next(request)

        # Enregistre le statut et les en-têtes de la réponse
        logger.info(f"Response Status: {response.status_code}")
        logger.info(f"Response Headers: {response.headers}")

        # Calcule et enregistre le temps d'exécution total de la requête
        duration = time.time() - start_time
        logger.info(f"Processed {request.method} {request.url} in {duration:.2f} seconds")

        return response
