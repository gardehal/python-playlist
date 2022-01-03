from enum import IntEnum
import os

class StreamSourceType(IntEnum):
    DICTIONARY = 1,
    YOUTUBE = 2,
    

class StreamSourceTypeUtil():
    def strToStreamSourceType(source: str) -> StreamSourceType:
        """
        Get StreamSourceType from string (path or url).

        Args:
            source (str): path or url to source of videos

        Returns:
            StreamSourceType: StreamSourceType if a fitting StreamSourceType was found, else None
        """
        
        if(os.path.isdir(source)):
            return StreamSourceType.DICTIONARY
        elif("https://youtu.be" in source or "https://www.youtube.com" in source):
            return StreamSourceType.YOUTUBE
        
        return None 