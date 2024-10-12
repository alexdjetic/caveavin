from pymongo import MongoClient
from pymongo.errors import PyMongoError

class Connexdb:
    """
    A class to manage MongoDB connections and operations.

    Attributes
    ----------
    host : str
        The hostname of the MongoDB server.
    port : int
        The port number of the MongoDB server.
    username : str
        The username to connect to MongoDB.
    password : str
        The password to connect to MongoDB.
    client : MongoClient
        The MongoDB client instance.
    db : Database
        The MongoDB database instance.

    Methods
    -------
    get_all_collection_name() -> dict
        Fetches all collection names from the database.
    get_all_data_from_collection(collection: str) -> dict
        Fetches all data from a specified collection.
    delete_data_from_collection(collection: str, query: dict) -> dict
        Deletes data from a specified collection based on a query.
    update_data_from_collection(collection: str, query: dict, new_data: dict) -> dict
        Updates data in a specified collection based on a query.
    insert_data_into_collection(collection: str, data: dict) -> dict
        Inserts data into a specified collection.
    exist(collection: str, query: dict) -> dict
        Checks if a document exists in a specified collection based on a query.
    close() -> dict
        Closes the MongoDB connection.
    """

    def __init__(self, host='localhost', port=27018, username=None, password=None):
        """
        Initializes the Connexdb class with the provided MongoDB server details.

        Parameters
        ----------
        host : str, optional
            The hostname of the MongoDB server (default is 'localhost').
        port : int, optional
            The port number of the MongoDB server (default is 27018).
        username : str, optional
            The username to connect to MongoDB (default is None).
        password : str, optional
            The password to connect to MongoDB (default is None).
        """
        if username and password:
            self.client = MongoClient(f"mongodb://{username}:{password}@{host}:{port}/")
        else:
            self.client = MongoClient(host=host, port=port)

        self.db = self.client.caveavin

    def get_all_collection_name(self) -> dict:
        """
        Fetches all collection names from the database.

        Returns
        -------
        dict
            A dictionary with status, message, and data (collection names).
        """
        try:
            collections = self.db.list_collection_names()
            return {"status": 200, "message": "Successfully fetched collections", "data": collections}
        except PyMongoError as e:
            return {"status": 500, "message": f"Error fetching collection names: {e}"}

    def get_all_data_from_collection(self, collection: str) -> dict:
        """
        Fetches all data from a specified collection.

        Parameters
        ----------
        collection : str
            The name of the collection to fetch data from.

        Returns
        -------
        dict
            A dictionary with status, message, and data (documents from the collection).
        """
        try:
            data = list(self.db[collection].find())
            return {"status": 200, "message": "Successfully fetched data", "data": data}
        except PyMongoError as e:
            return {"status": 500, "message": f"Error fetching data from collection '{collection}': {e}", "data": []}

    def get_data_from_collection(self, collection: str, query: dict) -> dict:
        """
        Fetches data from a specified collection based on a query.

        Parameters
        ----------
        collection : str
            The name of the collection to fetch data from.
        query : dict
            The query to filter the documents.

        Returns
        -------
        dict
            A dictionary with status, message, and data (matching documents from the collection).
        """
        try:
            data = list(self.db[collection].find(query))
            return {"status": 200, "message": "Successfully fetched data", "data": data}
        except PyMongoError as e:
            return {"status": 500, "message": f"Error fetching data from collection '{collection}': {e}", "data": []}

    def delete_data_from_collection(self, collection: str, query: dict) -> dict:
        """
        Deletes data from a specified collection based on a query.

        Parameters
        ----------
        collection : str
            The name of the collection to delete data from.
        query : dict
            The query to match the document to delete.

        Returns
        -------
        dict
            A dictionary with status and message.
        """
        try:
            self.db[collection].delete_one(query)
            return {"status": 200, "message": "Successfully deleted data"}
        except PyMongoError as e:
            return {"status": 500, "message": f"Error deleting data from collection '{collection}': {e}"}
        except TypeError as e:
            return {"status": 501, "message": f"Type Error: {e}"}

    def update_data_from_collection(self, collection: str, query: dict, new_data: dict) -> dict:
        """
        Updates data in a specified collection based on a query.

        Parameters
        ----------
        collection : str
            The name of the collection to update data in.
        query : dict
            The query to match the document to update.
        new_data : dict
            The new data to set in the matched document.

        Returns
        -------
        dict
            A dictionary with status and message.
        """
        try:
            self.db[collection].update_one(query, {'$set': new_data})
            return {"status": 200, "message": "Successfully updated data"}
        except PyMongoError as e:
            return {"status": 500, "message": f"Error updating data in collection '{collection}': {e}"}
        except TypeError as e:
            return {"status": 501, "message": f"Type Error: {e}"}

    def insert_data_into_collection(self, collection: str, data: dict) -> dict:
        """
        Inserts data into a specified collection.

        Parameters
        ----------
        collection : str
            The name of the collection to insert data into.
        data : dict
            The data to insert as a document.

        Returns
        -------
        dict
            A dictionary with status and message.
        """
        try:
            self.db[collection].insert_one(data)
            return {"status": 200, "message": "Successfully inserted data"}
        except PyMongoError as e:
            return {"status": 500, "message": f"Error inserting data into collection '{collection}': {e}"}
        except TypeError as e:
            return {"status": 501, "message": f"Type Error: {e}"}

    def exist(self, collection: str, query: dict) -> dict:
        """
        Checks if a document exists in a specified collection based on a query.

        Parameters
        ----------
        collection : str
            The name of the collection to check for existence.
        query : dict
            The query to match the document.

        Returns
        -------
        dict
            A dictionary with status and message.
        """
        try:
            exists = self.db[collection].find_one(query) is not None
            return {"status": 200, "message": "Data exists" if exists else "User does not exist"}
        except PyMongoError as e:
            return {"status": 500, "message": f"Error checking existence in collection '{collection}': {e}"}
        except TypeError as e:
            return {"status": 501, "message": f"Type Error: {e}"}

    def close(self) -> dict:
        """
        Closes the MongoDB connection.

        Returns
        -------
        dict
            A dictionary with status and message.
        """
        if self.client:
            self.client.close()
            return {"status": 200, "message": "Connection closed successfully"}

if __name__ == '__main__':
    db_connection = Connexdb(
        host='localhost',
        port=27018,
        username="root",
        password="wm7ze*2b"
    )
    collections: str = 'user'

    # Example Usage
    print(f"Collections: {db_connection.get_all_collection_name()}")

    # Inserting data into the 'bouteille' collection
    new_bouteille: dict = {
        "name": "Chateau Margaux",
        "type": "Rouge",
        "year": 2015,
        "region": "France",
        "price": 150.0,
        "notes": [],
        "comments": [],
        "photo": "binarydatahere"
    }
    insert_result = db_connection.insert_data_into_collection(collections, new_bouteille)
    print(insert_result)

    # Fetching data from the 'bouteille' collection
    bouteille_data = db_connection.get_all_data_from_collection(collections)  # <- Ensure you fetch from 'bouteille'
    print(f"Data in 'bouteille' collection: {bouteille_data}")

    # Checking if the data exists
    existence_check = db_connection.exist(collections, {"name": "Chateau Margaux"})
    print(existence_check)

    # Closing the connection
    close_result = db_connection.close()
    print(close_result)
