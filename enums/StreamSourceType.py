from enum import IntEnum
import os

class StreamSourceType(IntEnum):
    DICTIONARY = 1,
    YOUTUBE = 2,
    ODYSEE = 3,
    RUMBLE = 4,
    BITCHUTE = 5,
    DAILYMOTION = 6,
    VIMEO = 7,
    VK = 8,
    FACEBOOK = 9,
    INSTAGRAM = 10,
    TWITTER = 11,

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
        elif("youtu.be" in source or "youtube" in source):
            return StreamSourceType.YOUTUBE
        elif("odysee" in source):
            return StreamSourceType.ODYSEE
        elif("rumble" in source):
            return StreamSourceType.RUMBLE
        elif("bitchute" in source):
            return StreamSourceType.BITCHUTE
        elif("dailymotion" in source):
            return StreamSourceType.DAILYMOTION
        elif("vimeo" in source):
            return StreamSourceType.VIMEO
        elif("vk" in source):
            return StreamSourceType.VK
        elif("facebook" in source):
            return StreamSourceType.FACEBOOK
        elif("instagram" in source):
            return StreamSourceType.INSTAGRAM
        elif("twitter" in source):
            return StreamSourceType.TWITTER
        
        return None 