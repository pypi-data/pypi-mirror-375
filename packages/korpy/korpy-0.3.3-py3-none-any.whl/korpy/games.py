from __future__ import annotations
from .core import words, fully_korean
from random import choice
from copy import deepcopy
class ConcludingRemarksGame:
    def __init__(self, *, words_preset: list[str] = None):
        """
        a game object for concluding remarks game (끝말있기)
        """
        if words_preset == None:
            words_preset = words()
        if not fully_korean("".join(words_preset)):
            raise ValueError("not korean or it's a sentence")
        self.words = words_preset
        self.used_words = []
        self.last = None
    def able_to_put(self, word: str) -> bool:
        """
        checks if able to put
        """
        if not fully_korean(word):
            raise ValueError("not korean or it's a sentence")
        if word not in self.words:
            return False
        if word in self.used_words:
            return False
        if self.last == None:
            return True
        else:
            return self.last[-1] == word[0]
    def put(self, word: str, *, check_if_able_to_put: bool = False):
        """
        puts a word
        """
        if not self.able_to_put(word) and check_if_able_to_put:
            raise ValueError("not able to put")
        self.used_words.append(word)
        self.last = word
    def reset(self):
        """
        resets the game
        """
        self.used_words=[]
        self.last=None
    def set_words(self, allowed_words: list[str] = None):
        """
        set the words
        """
        if allowed_words == None:
            allowed_words = words()
        for word in self.used_words:
            if word not in allowed_words:
                raise ValueError("not able to change because found a not-matching word in used words")
        self.words = allowed_words
        if self.words == []:
            self.last = None
        else:
            self.last = self.words[-1]
    def __add__(self, other: ConcludingRemarksGame):
        words_preset = list(set(self.words+other.words))
        used_words_preset = list(set(self.used_words+other.used_words))
        last = used_words_preset[-1]
        game = ConcludingRemarksGame(words_preset=words_preset)
        game.used_words=used_words_preset
        game.last = last
        return game

class ConcludingRemarksRobot:
    def __init__(self, game: ConcludingRemarksGame):
        """
        concluding remarks game (끝말있기)'s robot 
        """
        self.game = game
    def put_choice(self)->str:
        """
        finds choice, and put & return it
        """
        alloweds = []
        for allowed_word in self.game.words:
            if self.game.able_to_put(allowed_word):
                alloweds.append(allowed_word)
        self.game.put(choice(alloweds))
        return self.game.last
    def is_gameover(self)->bool:
        """
        finds if game is over
        """
        return True not in list(map(self.game.able_to_put, self.game.words))
    def play_game(self)->list:
        """
        plays the game itself
        """
        test_self = deepcopy(self)
        while not test_self.is_gameover():
            test_self.put_choice()
        return test_self.game.used_words