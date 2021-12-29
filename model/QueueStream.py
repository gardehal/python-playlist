from datetime import datetime
import uuid

class QueueStream:
    def __init__(self, 
                 name: str = None, 
                 uri: str = None, 
                 isWeb: bool = False, 
                 watched: datetime = None, 
                 datetimeAdded: datetime = datetime.now(),
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.uri: str = uri
        self.isWeb: bool = isWeb
        self.watched: datetime = watched
        self.datetimeAdded: datetime = datetimeAdded
        self.id: str = id