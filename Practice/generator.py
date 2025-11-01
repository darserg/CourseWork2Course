from random import randint, choice, shuffle
import string

class Generator:
    def __init__(self, lenth=4):
        self.lenth = lenth
        self.alph = list(string.ascii_uppercase)
        
    def generate_numbers(self) -> str:
        number = randint(0, 10 ** self.lenth)
        result = str(number)
        while len(result) < self.lenth:
            result = "0" + result
        return str(result)
    
    def generate_chars(self) -> str:
        result = ""
        while len(result) < self.lenth:
            result += str(choice(self.alph))
        return str(result)
