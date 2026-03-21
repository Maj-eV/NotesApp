from dataclasses import dataclass
from errors import EmptyValueError

@dataclass 
class TodoTask:
    taskName: str
    user:str
    content: str
    collection: int
    completion: bool = False
    visible: bool = True

    @classmethod
    def addTask(cls, name:str, user:str, content:str, collection:int):
        try:
            if (not name) or (not content) or (not collection) or not(user):
                raise EmptyValueError
            if not isinstance(name, str) or not isinstance(content, str) or not isinstance(collection, int) or not isinstance(user, str):
                raise TypeError
            return cls(name, user,content, collection)
        except EmptyValueError:
            return cls("None", "None", "None", 0)
        except TypeError:
            return cls(str(name), str(user),str(content),int(collection))
    

    @property
    def title(self):
        """Get task's title."""
        return self.taskName

    @property
    def data(self) -> dict:
        """Get data as dictionary."""
        return {
            "title": self.taskName,
            "user": self.user,
            "content": self.content,
            "collection": self.collection,
            "completion": self.completion,
            "visibility": self.visible
            
        }
    
    def changeContent(self, content:str) -> None:
        """Change task's content"""
        if not content:
            raise EmptyValueError
        if not isinstance(content, str):
            raise TypeError
        self.content = content
    
    def changeTitle(self, title:str) -> None:
        """Change task's title."""
        if not title:
            raise EmptyValueError
        if not isinstance(title, str):
            raise TypeError
        self.taskName = title
    
    def completeTask(self):
        """Set set completion of the task as True."""
        self.completion = True

    def setVisibility(self, visible:bool) -> None:
        """Set task's visibility."""
        if not visible:
            raise EmptyValueError
        if not isinstance(visible,bool):
            raise TypeError
        self.visible = visible
    
        








    



