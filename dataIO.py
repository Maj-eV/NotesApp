import json
import bcrypt
from errors import EmptyValueError
from task_collections import Collection
from tasks import TodoTask

def init_local_data(user:str, password:str):
    """
    Initiate user local data files.

    Function creates document asrAppData_{userName}.json in local directory.
    """
    if (not user) or (not password):
        raise EmptyValueError
    if not isinstance(user, str) or not isinstance(password, str):
        raise TypeError
    salt = bcrypt.gensalt()
    with open(f"usrAppData_{user}.json", "w") as data_handler:
        json.dump({ "pswd": str(bcrypt.hashpw(bytes(password, "utf-8"),salt)), 
                    "collections": [],
                    "number_of_collections":0, 
                    "tasks": []
                    }, data_handler, indent=2)

def add_collection(user:str, name:str):
    """
    Add new collection to local json file assigned to user.
    
    Id of created collection is assigned automaticly is is equal to id of the last collection in file +1
    """
    if (not user) or (not name):
        raise EmptyValueError
    if (not isinstance(user,str)) or (not isinstance(name, str)):
        raise TypeError
    with open(f'usrAppData_{user}.json', "r") as file_handler:
        data = json.load(file_handler)
    
    data["collections"].append(Collection(data["number_of_collections"]+1, name, user).data)
    data["number_of_collections"]+=1

    with open(f'usrAppData_{user}.json',"w") as file_handler:
        json.dump(data, file_handler, indent=2)

def add_task(name:str, user:str, content:str, collection:int):
    if (not name) or (not user) or (not content) or (not collection):
        raise EmptyValueError
    if (not isinstance(name,str)) or (not isinstance(user, str)) or (not isinstance(content,str)) or (not isinstance(collection,int)):
        raise TypeError
    with open(f'usrAppData_{user}.json', "r") as file_handler:
        data = json.load(file_handler)
    
        data["tasks"].append(TodoTask.addTask(name, user,content,collection).data)

    with open(f'usrAppData_{user}.json',"w") as file_handler:
        json.dump(data, file_handler, indent=2)


def deleteTask(name:str, user:str):
    with open(f'usrAppData_{user}.json', "r") as file_handler:
        data = json.load(file_handler)
        data["tasks"] = [d for d in data["tasks"] if d["title"] != name]

    with open(f'usrAppData_'):
        pass
