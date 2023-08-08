"""Utilities related to Boggle game."""

from random import choice
import string
from collections import OrderedDict
import json 

class Boggle():

    def __init__(self, size=5):
        self.words = self.read_dict("words.txt")
        self.tree = self.build_word_tree()

    def build_word_tree(self):
        tree = WordTree()
        for word in self.words:
            node = tree.root
            for idx, char in enumerate(word.upper()):
                if char not in node.children:
                    new_node = WordNode(char, None, idx == len(word) - 1)
                    node.children.setdefault(char, new_node)
                node = node.children[char]
                if idx == len(word) - 1:
                    node.is_word = True
                    node.word = word.upper()
                
        return tree

    def read_dict(self, dict_path):
        """Read and return all words in dictionary."""

        dict_file = open(dict_path)
        words = [w.strip() for w in dict_file]
        dict_file.close()
        return words

    def make_board(self, size=5):
        """Make and return a random boggle board."""
        board = []

        for y in range(size):
            row = [choice(string.ascii_uppercase) for i in range(size)]
            board.append(row)

        return board

    def check_valid_word(self, board, word):
        """Check if a word is a valid word in the dictionary and/or the boggle board"""

        word_exists = word in self.words
        valid_word = self.find(board, word.upper())

        if word_exists and valid_word:
            result = "ok"
        elif word_exists and not valid_word:
            result = "not-on-board"
        else:
            result = "not-word"

        return result

    def find_from(self, board, word, y, x, seen):
        size = len(board)
        """Can we find a word on board, starting at x, y?"""
        if x > size - 1 or y > size - 1:
            return []

        # This is called recursively to find smaller and smaller words
        # until all tries are exhausted or until success.

        # Base case: this isn't the letter we're looking for.
        if board[y][x] != word[0]:
            return False
        

        # Base case: we've used this letter before in this current path

        if (y, x) in seen:
            return False

        # Base case: we are down to the last letter --- so we win!

        if len(word) == 1:
            return [(y, x)]

        # Otherwise, this letter is good, so note that we've seen it,
        # and try of all of its neighbors for the first letter of the
        # rest of the word
        # This next line is a bit tricky: we want to note that we've seen the
        # letter at this location. However, we only want the child calls of this
        # to get that, and if we used `seen.add(...)` to add it to our set,
        # *all* calls would get that, since the set is passed around. That would
        # mean that once we try a letter in one call, it could never be tried again,
        # even in a totally different path. Therefore, we want to create a *new*
        # seen set that is equal to this set plus the new letter. Being a new
        # object, rather than a mutated shared object, calls that don't descend
        # from us won't have this `y,x` point in their seen.
        #
        # To do this, we use the | (set-union) operator, read this line as
        # "rebind seen to the union of the current seen and the set of point(y,x))."
        #
        # (this could be written with an augmented operator as "seen |= {(y, x)}",
        # in the same way "x = x + 2" can be written as "x += 2", but that would seem
        # harder to understand).

        seen = seen | {(y, x)}

        # adding diagonals

        if y > 0:
            result = self.find_from(board, word[1:], y - 1, x, seen)
            if result:
                result.insert(0, (y, x))
                return result

        if y < size - 1:
            result = self.find_from(board, word[1:], y + 1, x, seen)
            if result:
                result.insert(0, (y, x))
                return result

        if x > 0:
            result = self.find_from(board, word[1:], y, x - 1, seen)
            if result:
                result.insert(0, (y, x))
                return result

        if x < size - 1:
            result = self.find_from(board, word[1:], y, x + 1, seen)
            if result:
                result.insert(0, (y, x))
                return result

        # diagonals
        if y > 0 and x > 0:
            result = self.find_from(board, word[1:], y - 1, x - 1, seen)
            if result:
                result.insert(0, (y, x))
                return result

        if y < size - 1 and x < size - 1:
            result = self.find_from(board, word[1:], y + 1, x + 1, seen)
            if result:
                result.insert(0, (y, x))
                return result

        if x > 0 and y < size - 1:
            result = self.find_from(board, word[1:], y + 1, x - 1, seen)
            if result:
                result.insert(0, (y, x))
                return result

        if x < size - 1 and y > 0:
            result = self.find_from(board, word[1:], y - 1, x + 1, seen)
            if result:
                result.insert(0, (y, x))
                return result
        # Couldn't find the next letter, so this path is dead

        return False

    def find(self, board, word):
        size = len(board)
        """Can word be found in board?"""

        # Find starting letter --- try every spot on board and,
        # win fast, should we find the word at that place.

        for y in range(0, size):
            for x in range(0, size):
                result = self.find_from(board, word, y, x, seen=set())
                if result:
                    return result

        # We've tried every path from every starting square w/o luck.
        # Sad panda.

        return False
    
    def find_possible_words(self, board):
        word_set = set()
        size = len(board)
        for y in range(0, size):
            for x in range(0, size):
                words = self.find_words_from(board, y, x, OrderedDict(), self.tree.root, set())
                word_set = word_set.union(words)
    
        return list(map(lambda word_seq: json.loads(word_seq), list(word_set)))

    def find_words_from(self, board, y, x, seen: OrderedDict, node: 'WordNode', found):
        size = len(board)
        """Base case: cell already visited"""
        if (y, x) in seen:
            return found
        """Base case: out of board"""
        if y < 0 or y >= size or x < 0 or x >= size:
            return found
        
        if board[y][x].upper() in node.children:
            seen[(y, x)] = None
            child = node.get_child(board[y][x])
            if child.is_word:
                found.add(json.dumps(list(seen.keys())))
            
            self.find_words_from(board, y, x+1, seen.copy(), child, found)
            self.find_words_from(board, y, x-1, seen.copy(), child, found)
            self.find_words_from(board, y+1, x, seen.copy(), child, found)
            self.find_words_from(board, y-1, x, seen.copy(), child, found)
            self.find_words_from(board, y+1, x+1, seen.copy(), child, found)
            self.find_words_from(board, y-1, x-1, seen.copy(), child, found)
            self.find_words_from(board, y+1, x-1, seen.copy(), child, found)
            self.find_words_from(board, y-1, x+1, seen.copy(), child, found)


        return found

class WordNode:
    def __init__(self, value: str, children: dict[str, 'WordNode'] = None, is_word = False):
        self.value = value.upper()
        self.children = children if children is not None else {}
        self.is_word = is_word
        self.word = None
    def get_child(self, char: str):
        return self.children[char.upper()]

class WordTree:
    def __init__(self, root: WordNode = WordNode('', None, False)):
        self.root = root



        
