import numpy as np
import re
from progressbar import progressbar as pb
np.set_printoptions(linewidth=99999)

class Word():
    def __init__(self, word):
        self.word = word
        self.in_grid = False
        self.has_matches = False

    def set_match_dict(self, match_dict):
        self.match_dict = match_dict
        self.has_matches = True

    def set_location(self, row, col, a_or_d):
        self.row = row
        self.col = col
        self.a_or_d = a_or_d
        self.in_grid = True

    def __repr__(self):
        return f'WORD_CLASS: {self.word}'

    def __len__(self):
        return len(self.word)

    def __iter__(self):
        return iter(self.word)

    def __getitem__(self, match):
        return self.match_dict[match]

    # def __index__(self):
    #     return self.word


class WordList():
    def __init__(self, wordlist):
        self.wordlist = [Word(word) for word in wordlist]
        self.words = wordlist
        self.lookup_dict = dict(zip(self.words, self.wordlist))

    def lookup(self, word):
        return self.wordlist[word]


    def remove_words_from_grid(self):
        for word in self.wordlist:
            word.in_grid = False

    def remaining_words(self):
        remaining_words = []
        for word in self.wordlist:
            if not word.in_grid:
                remaining_words.append(word)
        return remaining_words

    def __iter__(self):
        return iter(self.wordlist)

    def __getitem__(self, word):
        return self.lookup_dict[word]

    def __repr__(self):
        return str(self.words)


class Grid():
    def __init__(self):
        self.grid = np.full([15, 15], ' ', dtype=np.object)
        self.empty = True

        self.rows = self.grid
        self.cols = self.grid.T
        self.n_words_in_grid = 0

    def __len__(self):
        return self.n_words_in_grid

    def __index__(self):
        return self.grid

    def __repr__(self):
        return str(self.grid)

class Pair():
    def __init__(self, w1: Word, w2: Word=None, line=[]):
        self.words = [w1]
        self.w1 = w1
        if w2:
            self.w2 = w2
            self.words.append(w2)

        self.line = line
        self.num_spaces = self.compute_num_spaces()

    def compute_num_spaces(self):
        num_spaces = 0
        for letter in self.line:
            if letter == ' ':
                num_spaces +=1
        return num_spaces

    def __repr__(self):
        return str(self.line)

    def __iter__(self):
        return iter(self.line)

class Line():
    def __init__(self, i, line, isrow):
        self.line = line
        self.idx = i
        self.isrow = isrow
        self.wildcard = '/'

    def compute_possible_words(self, wordlist):
        self.possible_pairs = []
        for w1 in wordlist:
            if not w1.in_grid:
                if len(w1) >= 14:
                    works, newline = self.check_singleton(w1)
                    if works:
                        self.possible_pairs.append(Pair(w1, line=newline))
                else:
                    for w2 in wordlist:
                        if not w2.in_grid:
                            # print(w2, len(w1) + len(w2))
                            if (w2 != w1) and (len(w1) + len(w2) == 14):
                                works, newline = self.check_pair(w1, w2)
                                if works:
                                    self.possible_pairs.append(Pair(w1, w2, line=newline))

    def check_singleton(self, w1):
        '''only checks words of len 14 with space at the end'''
        newline = []
        current_letter = 0
        for letter in w1:
            if self.line[current_letter] not in [' ', letter]:
                return False, newline
            newline.append(letter)
            current_letter+=1
        if current_letter==13: #if word is len 14
            if self.line[14] != ' ':
                return False, newline
            newline.append(self.wildcard)
        return True, newline

    def check_pair(self, w1, w2):
        newline = []
        current_letter = 0
        for letter in w1:
            if self.line[current_letter] not in [' ', letter]:
                return False, newline
            newline.append(letter)
            current_letter +=1
        if self.line[current_letter] != ' ':
            return False, newline
        newline.append(self.wildcard)
        current_letter += 1
        for letter in w2:
            if self.line[current_letter] not in [' ', letter]:
                return False, newline
            newline.append(letter)
            current_letter +=1
        return True, newline

    def __iter__(self):
        return self.line

    def __index__(self):
        return self.line

    def __repr__(self):
        return str(self.line)


class Filler():
    def __init__(self, wordlist, row_offset, col_offset):
        self.row_offset = 1
        self.col_offset = 1
        self.grid = Grid()
        self.wordlist = WordList(wordlist)
        # self.wordlist.compute_possible_matches()
        self.best_grid = None
        self.rows = [Line(i, line, True) for (i, line) in zip(range(len(self.grid.rows)), self.grid.rows)]
        self.cols = [Line(i, line, False) for (i, line) in zip(range(len(self.grid.cols)), self.grid.cols)]

    def fill(self):
        for i in range(15-min(1, self.row_offset+self.col_offset))[::2]:
            ir = i + row_offset
            breakpoint()
            self.update_line_matches()
            self.insert_pair(self.rows[ir])
            print(self.grid)
            ic = i+col_offset
            self.update_line_matches()
            self.insert_pair(self.cols[ic])
            print(self.grid)

    def insert_pair(self, line):
        idx = line.idx
        isrow = line.isrow
        if line.possible_pairs:
            if isrow:
                self.grid.rows[idx] = [letter for letter in line.possible_pairs[0]]
            else:
                self.grid.cols[idx] = [letter for letter in line.possible_pairs[0]]
            for word in line.possible_pairs[0].words:
                word.in_grid=True

    def update_line_matches(self):
        for i in range(15):
            self.rows[i].compute_possible_words(self.wordlist)
            self.cols[i].compute_possible_words(self.wordlist)

class ProgramState():
    def __init__(self):
        self.idx = 0


def grid_printer(grid):
    listy_grid = [[str(i) for i in list(j)] for j in grid.grid]
    stringy_grid = [str(i) + '//' for i in listy_grid]
    return stringy_grid

def compute_best_match(match_list):
    word_scores = []
    score_to_words = {}
    for word in match_list:
        score = len(word.match_dict.keys())
        word_scores.append(score)
        try:    score_to_words[score].append(word)
        except: score_to_words[score] = [word]
    if word_scores:
        best_matches = score_to_words[sorted(word_scores)[::-1][0]]
        return best_matches
    return False


def main():
    from wordlist import wordlist
    filler = Filler(wordlist)
    filler.fill()


 #TECHNICALLY EVERY WORD SHOULD HAVE A MATCH AT EVERY OTHER LETTER!
 #FUQ
 #THERE SEEM TO BE 29ISH WORDS PER REAL XWORD

if __name__=='__main__':
    main()
