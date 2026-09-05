import os

# decorator
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

# decorator
def logging(func):
    def wrapper(*args, **kwargs):
        print(f"{func.__name__} called")
        print(f"{func.__name__} finished")
    return wrapper

# colorized terminal print
class TerminalPrinter():
    def __init__(self):
        self.reset = "\033[0m"
        self.green = "\033[32m"
        self.red = "\033[31m"

    def out(self,content:str,lf:bool = True):
        print(f"{self.green}{content}{self.reset}",end = "" if lf == False else "\n" )

    def wout(self,content:str,lf:bool = True):
        print(f"{self.red}{content}{self.reset}",end = "" if lf == False else "\n" )

    def title(self,content:str):
        division = ""
        blank = ""
        for _ in range(len(content)):
            division += "==="
            blank += " "
        print(division)
        print(blank,end="")
        print(content)
        print(division)

    def clear(self):
        print("\033[2J\033[H", end="")
    

#debuger
class Debuger():
    @staticmethod
    def printd(msg):
        print(f"[DBG] {msg}",flush=True)
    @staticmethod
    def printc(msg):
        os.system("cls")
        print(f"[DBG] {msg}",flush = True)