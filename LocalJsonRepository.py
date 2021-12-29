import glob
from model.Playlist import *
from myutil.Util import *
from JsonUtil import *
from typing import Generic, List, TypeVar

T = TypeVar("T")

class LocalJsonRepository(Generic[T]):
    debug: bool = False
    storagePath: str = "."

    def __init__(self,
                 typeT: type,
                 debug: bool = False,
                 storagePath: str = "."):
        self.typeT: type = typeT
        self.debug: bool = debug
        self.storagePath: str = storagePath

        mkdir(storagePath)

    def add(self, entity: T) -> bool:
        """
        Add a new entity using local JSON files for storage.

        Args:
            entity (T): entity to add

        Returns:
            bool: success = True
        """

        _entity = LocalJsonRepository.get(self, entity.id)
        if(_entity != None):
            if(self.debug): printS("Error adding ", entity.id, ", ID already exists", color=colors["FAIL"])
            return False

        try:
            _newEntityDict = JsonUtil.toDict(entity)
            _filename = entity.id + ".json"
            _path = os.path.join(self.storagePath, _filename)
            with open(_path, "a") as file:
                json.dump(_newEntityDict, file, indent=4, default=str)

            return True
        except Exception:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error adding ", entity.id, color=colors["FAIL"])
            return False

    def get(self, id: str) -> T:
        """
        Get entity using local JSON files for storage.

        Args:
            id (str): id of entity to get

        Returns:
            T: entity if any, else None
        """

        try:
            _filename = id + ".json"
            _path = os.path.join(self.storagePath, _filename)
            if(not os.path.isfile(_path)):
                return None

            _fileContent = open(_path, "r").read()
            if(len(_fileContent) < 2):
                return None
            else:
                return JsonUtil.fromJson(_fileContent, self.typeT)
        except Exception:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error getting", color=colors["FAIL"])
            return None

    def getAll(self) -> List[T]:
        """
        Get all entities using local JSON files for storage.

        Returns:
            List[T]: entities if any, else empty list
        """

        try:
            _all = []
            _globPath = glob.glob(f"{self.storagePath}/*.json")
            for file in _globPath:
                fileContent = open(file, "r").read()
                if(len(fileContent) > 2):
                    _all.append(JsonUtil.fromJson(fileContent, self.typeT))
            
            return _all
        except Exception:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error getting all", color=colors["FAIL"])
            return List[T]

    def update(self, entity: T) -> bool:
        """
        Update entity using local JSON files for storage.

        Args:
            entity (T): entity to update

        Returns:
            bool: success = True
        """

        _entity = LocalJsonRepository.get(self, entity.id)
        if(_entity == None):
            printS("Error updating ", entity.id, ", entity does not exist", color=colors["FAIL"])
            return False

        try:
            _updatedEntityDict = JsonUtil.toDict(entity)
            _filename = _entity.id + ".json"
            _path = os.path.join(self.storagePath, _filename)
            with open(_path, "w") as file:
                json.dump(_updatedEntityDict, file, indent=4, default=str)
            
            return True
        except Exception:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error updating ", entity.id, color=colors["FAIL"])
            return False

    def remove(self, id: str) -> bool:
        """
        Remove entity using local JSON files for storage.

        Args:
            id (str): id of entity to remove

        Returns:
            bool: success = True
        """

        _entity = LocalJsonRepository.get(self, id)
        if(_entity == None):
            printS("Error removeing ", id, ", entity does not exist", color=colors["FAIL"])
            return False

        try:
            _filename = _entity.id + ".json"
            path = os.path.join(self.storagePath, _filename)
            os.remove(path)
            
            return True
        except Exception:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error removeing ", id, color=colors["FAIL"])
            return False