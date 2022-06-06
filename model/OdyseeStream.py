from datetime import datetime


class OdyseeStream:
    def __init__(self, 
                 title: str = None,
                 pubDate: datetime = None,
                 link: str = None,
                 guid: str = None):
        self.title: str = title
        self.pubDate: str = pubDate
        self.link: str = link
        self.guid: str = guid
        