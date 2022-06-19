import os

from dotenv import load_dotenv
from grdUtil.BashColor import BashColor
from grdUtil.PrintUtil import printLists, printS
from QueueStreamService import QueueStreamService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))

class QueueStreamCliController():
    queueStreamService: QueueStreamService = None

    def __init__(self):
        self.queueStreamService = QueueStreamService()
