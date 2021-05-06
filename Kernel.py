import json
from datetime import datetime

class Kernel:

    def __init__(self, verbose, debug, heritate_class):
        self.__version__ = "1.0.0"
        self.verbose = verbose
        self.debug = debug
        self.heritate_class = heritate_class
        self.date_format = "%m/%d/%Y, %H:%M:%S"
        self.encoding = "utf8"

    def display(self, message):
        if self.verbose:
            print(message)
    
    def display_debug(self, message):
        if self.debug:
            print(message)

    def now(self):
        return datetime.now().strftime(self.date_format)

    def format_message(self, code, message, end="\n"):
        return "{time} | {code} | {message}".format(time=self.now(), code=code, message=message)

    def read_json(self, path):

        content = ""
        if ".json" in path:
            with open(path, 'r', encoding=self.encoding) as f:
                content = json.load(f)
        else:
            raise Exception("Given path is not a json file")

        return content

    