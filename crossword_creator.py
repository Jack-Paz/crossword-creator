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

    def __index__(self):
        return self.word


class WordList():
    def __init__(self, wordlist):
        self.wordlist = [Word(word) for word in wordlist]
        self.words = wordlist
        self.lookup_dict = dict(zip(self.words, self.wordlist))

    def lookup(self, word):
        return self.wordlist[word]

    def compute_possible_matches(self):
        words = []
        for word in pb(self.wordlist):
            if not word.has_matches:
                possible_matches = {}
            for i, letter in enumerate(word.word):
                for wordn in self.wordlist:
                    if not wordn==word:
                        for j, lettern in enumerate(wordn.word):
                            if lettern==letter:
                                if wordn in possible_matches:
                                    if i in possible_matches[wordn]:
                                        possible_matches[wordn][i].append(j)
                                    else:
                                        try: possible_matches[wordn][i] = [j]
                                        except: possible_matches[wordn] = {i: [j]}
                                else:
                                    try: possible_matches[wordn] = {i: [j]}
                                    except: possible_matches = {wordn: {i: [j]}}
            if possible_matches:
                word.set_match_dict(possible_matches)

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
        # self.grid = [[' ' for i in range(15)] for i in range(15)]
        self.empty = True

    # def place_first_words(self, wordlist: WordList):
    #     assert self.empty
    #     inserted = []
    #     border_lines = [self.grid[0], self.grid[-1], self.grid[:, 0], self.grid[:, -1]]
    #     for line in border_lines:
    #
    #     self.insert_word(wordlist[wordlist.words[0]], 0,0,'a')
    #
    #     wi+=1
    #     self.empty = False
    #     return word

    def place_first_word(self, word: Word, row, col, a_or_d):
        assert self.empty
        self.insert_word(word, row, col, a_or_d)
        self.empty = False
        return word

    def place_next_word(self, word: Word):
        #try all borders
        for row_placepoint, col_placepoint in [[0,0],[0,14],[14,0],[14,14]]:
            for a_or_d in ['a','d']:
                if a_or_d=='a': #actually going across
                    actual_col = max(0, col_placepoint - (len(word)-1))
                    nl_check = self.check_neighbouring_lines(word, row_placepoint, actual_col, 'd')
                    line = self.grid[row_placepoint, actual_col:min(15, col_placepoint+len(word))+1]
                    l_check = self.check_line(word, a_or_d, row_placepoint, actual_col, line)
                    if nl_check and l_check:
                        self.insert_word(word, row_placepoint, actual_col, a_or_d)
                        return word
                else:
                    actual_row = max(0, row_placepoint - (len(word)-1))
                    nl_check = self.check_neighbouring_lines(word, actual_row, col_placepoint, 'a')
                    line = self.grid[actual_row: min(15, row_placepoint+len(word))+1, col_placepoint]
                    l_check = self.check_line(word, a_or_d, actual_row, col_placepoint, line)
                    if nl_check and l_check:
                        self.insert_word(word, actual_row, col_placepoint, a_or_d)
                        return word

    def place_possible_matches(self, word: Word):
        placed_words = []
        for match in word.match_dict:
            match_object = self.check_grid(word, match)
            if match_object:
                try:
                    self.insert_word(*match_object)
                except:
                    print(f'BROKE ON {word}, {match}')
                placed_words.append(match)
        return placed_words

    def insert_word(self, word: Word, row, col, a_or_d):
        if a_or_d=='a':
            if col+len(word.word)-1 == 14:
                self.grid[row, col:col+len(word.word)] = [l for l in word.word]
            else:
                self.grid[row, col:col+len(word.word)+1] = [l for l in word.word] + ['.']

        elif a_or_d=='d':
            if row+len(word.word)-1 == 14:
                self.grid[row:row+len(word.word), col] = [l for l in word.word]
            else:
                self.grid[row:row+len(word.word)+1, col] = [l for l in word.word] + ['.']
        # if word.word==''
        word.set_location(row, col, a_or_d)
        # print(self.grid)

    def check_grid(self, word, match):
        if match.in_grid:
            return False

        for w_intersect in word[match]:
            if word.a_or_d=='a': #next word goes down
                col_placepoint = w_intersect + word.col
                for m_intersect in word[match][w_intersect]:
                    row_placepoint = word.row - m_intersect
                    if 0 <= row_placepoint and 14 >= (word.row + len(match))-(m_intersect+1):
                        nl_check = self.check_neighbouring_lines(match, row_placepoint, col_placepoint, word.a_or_d)
                        line = self.grid[max(0, row_placepoint-1):min(15, row_placepoint+len(match)+1), col_placepoint]
                        l_check = self.check_line(match, word.a_or_d, word.row, word.col, line)
                        if nl_check and l_check:
                            return [match, row_placepoint, col_placepoint, 'd']

            else:              #next word goes across
                row_placepoint = w_intersect + word.row
                for m_intersect in word[match][w_intersect]:
                    col_placepoint = word.col - m_intersect
                    if 0 <= col_placepoint and 14 >= (word.col + len(match)) - (m_intersect+1):
                        nl_check = self.check_neighbouring_lines(match, row_placepoint, col_placepoint, word.a_or_d)
                        line = self.grid[row_placepoint, max(0, col_placepoint-1):min(15, col_placepoint+len(match)+1)]
                        l_check = self.check_line(match, word.a_or_d, word.row, word.col, line)
                        if nl_check and l_check:
                            return [match, row_placepoint, col_placepoint, 'a']
        return False

    def check_neighbouring_lines(self, match, row, col, a_or_d):
        #DOESNT ALLOW FOR MATCH TO START BEFORE CURRENT WORD, CHECK FAILS
        #ALSO DOESNT ALLOW MATCH TO PASS THROUGH OTHER WORDS
        #Should only return false if TWO CONSECUTIVE letters appear on neighbouring lines
        consec_letters = 0
        if a_or_d=='a':
            for c in [max(0, col-1), min(14, col+1)]: #check left and right cols
                for cell in self.grid[row:row+len(match), c]: #check along the length of the word
                    if cell not in [' ']:
                        consec_letters+=1
                        if consec_letters==2:
                            return False
                    else:
                        consec_letters=0
        else:
            for r in [max(0, row-1), min(14, row+1)]: #check above below rows
                for cell in self.grid[r, col:col+len(match)]:
                    if cell not in [' ']:
                        consec_letters+=1
                        if consec_letters==2:
                            return False
                    else:
                        consec_letters=0
        return True


    def check_line(self, word, a_or_d, row, col, line):
        if a_or_d=='a':
            left_border = False if row==0 else True
            right_border = False if row==14 else True
        else:
            left_border = False if col==0 else True
            right_border = False if col==14 else True
        border_bools = [left_border, right_border]
        borders = [x[0] for x in zip([line[0],line[-1]], border_bools) if x[1]]
        for cell in borders:
            if cell != ' ':
                return False
        left_idx = 1 if left_border else 0
        right_idx = -1 if right_border else 99
        for l, cell in enumerate(line[left_idx:right_idx]):
            if cell not in [' ', word.word[l]]:
                return False

        return True

    def __index__(self):
        return self.grid

    def __repr__(self):
        return str(self.grid)

def grid_printer(grid):
    listy_grid = [[str(i) for i in list(j)] for j in grid.grid]
    stringy_grid = [str(i) + '//' for i in listy_grid]
    return stringy_grid


def generate_grids():
    from wordlist import wordlist
    wl = WordList(wordlist)
    wl.compute_possible_matches()

    grid = Grid()
    matched_words = []
    gidx = 0
    grids = {}
    n_words = {}
    # for word in wl:
    go = True
    i=0
    while go:
        # breakpoint()
        words = wordlist[i:i+4]
        if not words:
            go = False
        for word in words:
            new_word = grid.place_next_word(wl[word])
            if new_word:
                matched_words.extend(grid.place_possible_matches(new_word))
        while matched_words:
            w = matched_words[0]
            matched_words.extend(grid.place_possible_matches(w))
            matched_words.pop(0)
        placed_words = sum([1 if x.in_grid else 0 for x in wl])
        grids[gidx] = (placed_words, grid)
        n_words[gidx] = placed_words
        i+=1
        gidx +=1
        grid = Grid()
        matched_words = []
        wl.remove_words_from_grid()
    return grids

def main():
    grids = generate_grids()
    top_grids = {k: v for k, v in sorted(n_words.items(), key=lambda item: item[1])[::-1]}
    np.set_printoptions()
    for g in list(top_grids.keys())[:5]:
        print(f'placed_words: {grids[g][0]}')
        neat_grid = grid_printer(grids[g][1])
        print(f'{neat_grid}')
    print('total generated grids: ', gidx)
#TO DO:

 #TECHNICALLY EVERY WORD SHOULD HAVE A MATCH AT EVERY OTHER LETTER!
 #FUQ
 #THERE SEEM TO BE 29ISH WORDS PER REAL XWORD

if __name__=='__main__':
    main()
