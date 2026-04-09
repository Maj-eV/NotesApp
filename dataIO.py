import json
import bcrypt
from errors import EmptyValueError
from task_collections import Collection
from tasks import TodoTask
import os

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
    if os.path.isfile(f"usrAppData_{user}.json"):
        raise ValueError
    with open(f"usrAppData_{user}.json", "w") as data_handler:
        json.dump({ "pswd": str(bcrypt.hashpw(bytes(password, "utf-8"),salt)), 
                    "collections": [],
                    "number_of_collections":0, 
                    "tasks": []
                    }, data_handler, indent=2)
    return 0

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
    return 0

def add_task(name:str, user:str, content:str, collection:int):
    if (not name) or (not user) or (not content) or (not collection):
        raise EmptyValueError
    if (not isinstance(name,str)) or (not isinstance(user, str)) or (not isinstance(content,str)) or (not isinstance(collection,int)):
        raise TypeError
    with open(f'usrAppData_{user}.json', "r") as file_handler:
        data = json.load(file_handler)

        data["tasks"].append(
            TodoTask.addTask(name, user,content,collection).data
            ) if name not in [
                task["title"] for task in data["tasks"] if (task["collection"] == collection and task["user"] == user)
                ] else None

    with open(f'usrAppData_{user}.json',"w") as file_handler:
        json.dump(data, file_handler, indent=2)
    return 0


def delete_task(name:str, user:str, collection_id:int):
    with open(f'usrAppData_{user}.json', "r") as file_handler:
        data = json.load(file_handler)
        data["tasks"] = [d for d in data["tasks"] if (d["title"] != name or d["collection"] != collection_id)]

    with open(f'usrAppData_{user}.json', "w")as file_handler:
        json.dump(data, file_handler,indent=2)
    return 0

def delete_collection(user:str,collection_id:str):
    with open(f'usrAppData_{user}.json',"r") as file_handler:
        data = json.load(file_handler)
        data["collections"] = [collection for collection in data["collections"] if collection["collection_id"] != collection_id]
    
    with open(f'usrAppData_{user}.json', "w") as file_handler:
        json.dump(data, file_handler, indent=2)
    return 0


def get_collections(user:str) -> list[str]:
    try:
        with open(f'usrAppData_{user}.json',"r") as file_handler:
            data = json.load(file_handler)
            collections = [collection["name"] for collection in data["collections"]]
            return collections
    except:
        return []

def get_collection_records(user:str) -> list[dict]:
    try:
        with open(f'usrAppData_{user}.json', "r") as file_handler:
            data = json.load(file_handler)
            return list(data["collections"])
    except:
        return []

def get_tasks(user:str, collection:str) -> list[dict]:
    try:
        with open(f"usrAppData_{user}.json", "r") as file_handler:
            data = json.load(file_handler)
            tasks = [task for task in data["tasks"] if (task["collection"] == collection and task["user"] == user)]
            return tasks
    except:
        return []

def mark_task_complete(name:str, user:str, collection_id:int, completed:bool):
    with open(f'usrAppData_{user}.json', "r") as file_handler:
        data = json.load(file_handler)
        for task in data["tasks"]:
            if task["title"] == name and task["collection"] == collection_id and task["user"] == user:
                task["completion"] = completed
                break
    with open(f'usrAppData_{user}.json', "w") as file_handler:
        json.dump(data, file_handler, indent=2)
    return 0
