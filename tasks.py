from dataclasses import dataclass
from errors import EmptyValueError

@dataclass 
class TodoTask():
    taskName: str
    content: str
    completion: bool = False
    visible: bool = True

    def addTask(self, name:str, content:str):
        try:
            if (not name or not content):
                raise EmptyValueError
            if (name is not str) or (content is not str):
                raise TypeError
            return TodoTask(name, content), 0
        except EmptyValueError:
            return TodoTask("None", "None")
        except TypeError:
            return TodoTask(str(name), str(content))
    
    @property
    def content(self) -> str:
        """Get task's content."""
        return self.content

    @property
    def title(self):
        """Get task's title."""
        return self.taskName

    @property
    def data(self) -> dict:
        """Get data as dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "completion": self.completion,
            "visibility": self.visibility
        }
    
    def changeContent(self, content:str) -> None:
        """Change task's content"""
        if not content:
            raise EmptyValueError
        if content is not str:
            raise TypeError
        self.content = content
    
    def changeTitle(self, title:str) -> None:
        """Change task's title."""
        if not title:
            raise EmptyValueError
        if title is not str:
            raise TypeError
        self.title = title
    
    def completeTask(self):
        """Set set completion of the task as True."""
        self.completion = True

    def visibility(self, visible:bool) -> None:
        """Set task's visibility."""
        if not visible:
            raise EmptyValueError
        if visible is not bool:
            raise TypeError
        
    






    



