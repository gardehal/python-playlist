from model.Playlist import *
from myutil.Util import *
from JsonUtil import *
from typing import List, TypeVar

T = TypeVar("T")

class LocalJsonRepository():
    debug: bool = False
    storagePath: str = "./"

    def __init__(self, 
                 debug: bool = False,
                 storagePath: str = "./"):
        LocalJsonRepository.debug: bool = debug
        LocalJsonRepository.storagePath: str = storagePath

    def add(self, entity: T, filename: str = None) -> bool:
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
            _filename = filename
            if(_filename == None):
                _filename = entity.id + ".json"

            path = os.path.join(LocalJsonRepository.storagePath, _filename)
            with open(path, "a") as file:
                json.dump(entityAsJson, file, indent=4, default=str)

            return True
        except Exception:
            if(LocalJsonRepository.debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error adding", color=colors["FAIL"])
            return False

    def get(id: uuid) -> T:
        """
        Get entity using local JSON files for storage.

        Args:
            id (uuid): id of entity to get

        Returns:
            T: entity if any, else None
        """

        try:
            
            return None
        except Exception:
            if(debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error getting", color=colors["FAIL"])
            return None

    def getAll() -> List[T]:
        """
        Get all entities using local JSON files for storage.

        Returns:
            List[T]: entities if any, else empty list
        """

        try:
            
            return List[T]
        except Exception:
            if(debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error getting all", color=colors["FAIL"])
            return List[T]

    def update(id: uuid) -> bool:
        """
        Update entity using local JSON files for storage.

        Args:
            id (uuid): id of entity to update

        Returns:
            bool: success = True
        """

        try:
            
            return True
        except Exception:
            if(debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error updating", color=colors["FAIL"])
            return False

    def remove(id: uuid) -> bool:
        """
        Remove entity using local JSON files for storage.

        Args:
            id (uuid): id of entity to remove

        Returns:
            bool: success = True
        """

        try:
            
            return True
        except Exception:
            if(debug): printS(sys.exc_info(), color=colors["WARNING"])
            printS("Error removeing", color=colors["FAIL"])
            return False