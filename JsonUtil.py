import json
from typing import TypeVar
from model.VideoSource import VideoSource
from myutil.Util import *
from myutil.DateTimeObject import *

T = TypeVar("T")

class JsonUtil:
    def toDict(obj: object) -> dict:
        """
        Converts objects to dictionaries.
        Source: https://www.codegrepper.com/code-examples/whatever/python+nested+object+to+dict

        Args:
            obj (object): object to convert

        Returns:
            dict: dictionary of input object
        """
        
        if not  hasattr(obj,"__dict__"):
            return obj
        
        result = {}
        for key, val in obj.__dict__.items():
            if key.startswith("_"):
                continue
            
            element = []
            if isinstance(val, list):
                for item in val:
                    element.append(JsonUtil.toDict(item))
            else:
                element = JsonUtil.toDict(val)
                
            result[key] = element
            
        return result
    
    def toJson(obj: object) -> str:
        """
        Converts objects to JSON though dictionaries.

        Args:
            obj (object): object to convert

        Returns:
            str: JSON string
        """
        
        dict = JsonUtil.toDict(obj)
        return json.dumps(dict, default=str)
    
    def writeToJsonFile(filepath: str, obj: object) -> bool:
        """
        Writes object obj to a JSON format in file from filepath.

        Args:
            filepath (str): path to file to store JSON in
            obj (object): object to save

        Returns:
            bool: true = success
        """
        
        asDict = JsonUtil.toDict(obj)
        with open(filepath, "w") as file:
            json.dump(asDict, file, indent=4, default=str)
            
        return True
    
    def readJsonFile(filepath: str, typeT: T) -> T:
        """
        Opens and reads a JSON formatted file, returning object of type T.

        Args:
            filepath (str): path to file to read JSON from
            typeT (T): object to convert to

        Returns:
            T or None: object from JSON file, if file is empty: None
        """
        
        fileContent = open(filepath, "r").read()
        if(len(fileContent) < 2):
            return None
        else:
            return JsonUtil.fromJson(fileContent, typeT)
    
    def fromJson(jsonStr: str, typeT: T) -> T:
        """
        Converts JSON to an object T.

        Args:
            str (str): string to convert
            typeT (T): object to convert to

        Returns:
            T: object from JSON
        """
        
        jsonDict = json.loads(jsonStr)
        asObj = typeT(**jsonDict)

        for fieldName in dir(asObj):
            # Skip default fields and functions
            if(fieldName.startswith('__') or callable(getattr(asObj, fieldName))):
                continue

            field = getattr(asObj, fieldName)
            fieldType = type(field)
            typeTField = getattr(typeT(), fieldName)


            print(type(field))
            print(field)
            print(typeTField)

            if("uuid" in str(fieldType) or "datetime" in str(fieldType)):
                continue
            elif(isinstance(fieldType, list)):
                print("--------------list")
                objList = []
                for listDict in field:
                    if("VideoSource" in str(typeTField)):
                        print(listDict)
                        objList.append(VideoSource(**listDict))
                    #else: other objects

                setattr(asObj, fieldName, objList)
            elif(isinstance(field, dict)):
                obj = {}
                if("VideoSource" in str(typeTField)):
                    obj = VideoSource(**field)
                
                setattr(asObj, fieldName, obj)

        return asObj