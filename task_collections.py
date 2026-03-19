from errors import EmptyValueError
import json


class Collection():
    def __init__(self, collection_id:int, name:str, user:str):
        if (not collection_id) or (not name) or (not user):
            raise EmptyValueError
        if not isinstance(collection_id, int) or not isinstance(name, str) or not isinstance(user, str):
            raise TypeError
        self._id = collection_id
        self._name = name
        self._user = user
    
    @property
    def data(self):
        return {"collection_id": self._id,
                "name": self._name,
                "user": self._user
                }
    
    def getTasks(self):
        with open(f"usrAppData_{self._name}.json","r") as file_handler:
            pass


    
