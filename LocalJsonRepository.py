from model.Playlist import *
from myutil.Util import *
from typing import List, TypeVar

T = TypeVar("T")

class PlaylistService:
    debug: bool = False
    storagePath: str = None

    def add(entity: T) -> bool:
        """
        Add a new entity using local JSON files for storage.

        Args:
            entity (T): entity to add

        Returns:
            bool: success = True
        """

        try:

            return True
        except Exception:
            if(debug): printS("Debug: Error adding", color=colors["FAIL"])
            printS(sys.exc_info(), color=colors["WARNING"])
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
            if(debug): printS("Debug: Error getting", color=colors["FAIL"])
            printS(sys.exc_info(), color=colors["WARNING"])
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
            if(debug): printS("Debug: Error getting all", color=colors["FAIL"])
            printS(sys.exc_info(), color=colors["WARNING"])
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
            if(debug): printS("Debug: Error updating", color=colors["FAIL"])
            printS(sys.exc_info(), color=colors["WARNING"])
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
            if(debug): printS("Debug: Error removeing", color=colors["FAIL"])
            printS(sys.exc_info(), color=colors["WARNING"])
            return False