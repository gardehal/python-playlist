from datetime import datetime
from urllib.parse import parse_qs, urlparse

from grdUtil.StrUtil import maxLen
from grdUtil.DateTimeUtil import getDateTime


class QueueStream:
    def __init__(self,
                 name: str = None,
                 uri: str = None,
                 isWeb: bool = False,
                 streamSourceId: str = None,
                 streamSourceName: str = None,
                 watched: datetime = None,
                 thumbnailUrl: str = None,
                 backgroundContent: bool = False,
                 playtimeSeconds: int = None,
                 publishedAt: datetime = None,
                 deleted: datetime = None,
                 added: datetime = getDateTime(),
                 remoteId: str = None,
                 id: str = None):
        self.name: str = name
        self.uri: str = uri
        self.streamSourceId: str = streamSourceId
        self.streamSourceName: str = streamSourceName
        self.watched: datetime = watched
        self.backgroundContent: bool = backgroundContent
        self.playtimeSeconds: int = playtimeSeconds
        self.publishedAt: int = publishedAt
        self.deleted: datetime = deleted
        self.added: datetime = added
        self.id: str = id

        parsedUri = urlparse(uri) if uri else None
        parsedHost = parsedUri.hostname.lower() if parsedUri and parsedUri.hostname else ""
        isYouTubeUrl = (
            parsedHost == "youtu.be"
            or parsedHost == "youtube.com"
            or parsedHost.endswith(".youtube.com")
            or parsedHost == "youtube-nocookie.com"
            or parsedHost.endswith(".youtube-nocookie.com")
        )

        if(isYouTubeUrl):
            isWeb = True
            pathParts = [part for part in parsedUri.path.split("/") if part]
            if(not remoteId):
                videoIds = parse_qs(parsedUri.query).get("v", [])
                if(videoIds):
                    remoteId = videoIds[0]
                elif(parsedHost == "youtu.be" and pathParts):
                    remoteId = pathParts[0]
                elif(len(pathParts) > 1 and pathParts[0] in {"shorts", "embed", "live", "v"}):
                    remoteId = pathParts[1]

            if(not thumbnailUrl and remoteId):
                thumbnailUrl = f"https://i.ytimg.com/vi/{remoteId}/hqdefault.jpg"

        self.isWeb: bool = isWeb
        self.remoteId: str = remoteId
        self.thumbnailUrl: str = thumbnailUrl

    def default(self):
        self.name: str = "name"
        self.uri: str = "uri"
        self.isWeb: bool = False
        self.streamSourceId: str = "streamSourceId"
        self.streamSourceName: str = "streamSourceName"
        self.watched: datetime = getDateTime()
        self.thumbnailUrl: str = None
        self.backgroundContent: bool = False
        self.deleted: datetime = datetime.now()
        self.added: datetime = getDateTime()
        self.remoteId: str = "remoteId"
        self.id: str = "id"
        return self

    def summaryString(self):
        return "".join(map(str, ["Name: ", self.name,
        ", ID: ", self.id,
        ", URI: ", self.uri]))

    def simpleString(self):
        return "".join(map(str, ["\"", self.name, "\"",
        ", watched" if(self.watched) else "",
        ", is web" if(self.isWeb) else ""]))

    def shortString(self):
        return "".join(map(str, ["\"", maxLen(self.name, 40), "\""]))

    def watchedString(self):
        return "".join(map(str, [self.id,
        ", watched: " + str(self.watched)[0:20] if(self.watched) else "",
        " - \"", maxLen(self.name, 20), "\" - "]))

    def detailsString(self, includeUri: bool = True, includeId: bool = True, includeDatetime: bool = True, includeListCount: bool = True):
        uriString = ", uri: " + self.uri if(includeUri) else ""
        streamSourceIdString = ", streamSourceId: " + str(self.streamSourceId) if(includeId) else ""
        idString = ", id: " + self.id if(includeId) else ""
        watchedString = ", watched: " + str(self.watched) if(includeDatetime) else ""
        deletedString = ", deleted: " + str(self.deleted) if(includeDatetime) else ""
        addedString = ", added: " + str(self.added) if(includeDatetime) else ""

        return "".join(map(str, ["\"", maxLen(self.name, 50), "\"",
        uriString,
        streamSourceIdString,
        ", ", self.streamSourceName, " ",
        watchedString,
        ", ", self.playtimeSeconds, " ",
        ", ", self.publishedAt, " ",
        deletedString,
        addedString,
        idString]))
