import glob
from model.Playlist import *
from myutil.Util import *
from JsonUtil import *
from typing import Generic, List, TypeVar

T = TypeVar("T")

class LocalJsonRepository(Generic[T]):
    typeT: T = None
    debug: bool = False
    storagePath: str = "./"

    def __init__(self,
                 typeT: T,
                 debug: bool = False,
                 storagePath: str = "./"):
        self.typeT: bool = typeT
        self.debug: bool = debug
        self.storagePath: str = storagePath

        mkdir(storagePath)

    def add(self, entity: T) -> bool:
        """
        Add a new entity using local JSON files for storage.

        Args:
            entity (T): entity to add
            filename (str): filename to store file in, defaults to id + "".json"

        Returns:
            bool: success = True
        """

        try:
            entityAsJson = JsonUtil.toDict(entity)
            _filename = entity.id + ".json"
            path = os.path.join(self.storagePath, _filename)
            with open(path, "a") as file:
                json.dump(entityAsJson, file, indent=4, default=str)

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
            path = os.path.join(self.storagePath, _filename)
            fileContent = open(path, "r").read()
            if(len(fileContent) < 2):
                return None
            else:
                return JsonUtil.fromJson(fileContent, self.typeT)
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
            all = []
            globPath = glob.glob(f"{self.storagePath}/*.json")
            for file in globPath:
                fileContent = open(file, "r").read()
                if(len(fileContent) > 2):
                    all.append(JsonUtil.fromJson(fileContent, self.typeT))
            
            return all
        except Exception:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error getting all", color=colors["FAIL"])
            return List[T]

    def update(self, id: str) -> bool:
        """
        Update entity using local JSON files for storage.

        Args:
            id (str): id of entity to update

        Returns:
            bool: success = True
        """

        try:
            entity = LocalJsonRepository.get(self, id)
            if(entity == None):
                printS("Error updating ", id, ", entity does not exist", color=colors["FAIL"])
                return False
            
            return True
        except Exception:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error updating ", id, color=colors["FAIL"])
            return False

    def remove(self, id: str) -> bool:
        """
        Remove entity using local JSON files for storage.

        Args:
            id (str): id of entity to remove

        Returns:
            bool: success = True
        """

        try:
            entity = LocalJsonRepository.get(self, id)
            if(entity == None):
                printS("Error removeing ", id, ", entity does not exist", color=colors["FAIL"])
                return False

            _filename = entity.id + ".json"
            path = os.path.join(self.storagePath, _filename)
            os.remove(path)
            
            return True
        except Exception:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error removeing ", id, color=colors["FAIL"])
            return False