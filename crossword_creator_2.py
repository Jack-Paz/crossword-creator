import numpy as np
import re
from progressbar import progressbar as pb
import copy
import nltk
np.set_printoptions(linewidth=99999)

GRID_SIZE = 11
WORDLIST_PAD_SIZE = 0

class Word(object):
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


class WordList():
    def __init__(self, wordlist):
        extra_words = nltk.corpus.words.words()
        while len(wordlist) < WORDLIST_PAD_SIZE:
            random_word = np.random.randint(len(extra_words))
            new_word = extra_words[random_word]
            if (GRID_SIZE >= len(new_word) >= 3) and (new_word not in wordlist):
                wordlist.append(new_word.upper())
                print(f'ADDED RANDOM WORD: {new_word.upper()}')
        wordlist = list(set(wordlist)) #remove duplicates
        self.words = [word for word in wordlist if len(word) <= GRID_SIZE]
        self.wordlist = [Word(word) for word in wordlist if len(word) <= GRID_SIZE]

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

    def __len__(self):
        return len(self.wordlist)

    def __repr__(self):
        return str(self.words)

class Line(object):
    def __init__(self, i, isrow):
        # self.line = line
        self.idx = i
        self.isrow = isrow
        self.wildcard = '/'
        self.pairs_tried = 0
        self.possible_pairs = []

    def compute_possible_words(self, wordlist, line):
        for w1 in wordlist:
            # print(w1)]
            words_in_line = []
            pairline = []
            pairline = self.check_first_word(w1, line, pairline)
            words_in_line.append(w1)
            self.recursive_search(pairline, line, wordlist, words_in_line)

    def check_first_word(self, w1, line, pairline):
        if not w1.in_grid:
            if len(w1) == GRID_SIZE:
                pairline = [l for l in w1]
                self.check(pairline, line, [w1])
                return pairline
            elif len(w1) == GRID_SIZE-1:
                for pairline in self.insert_wildcards([l for l in w1]):
                    self.check(pairline, line, [w1])
                return pairline
            else:
                return [l for l in w1] + [self.wildcard]
        return [' ']*15

    def insert_wildcards(self, pairline):
        line_1 = [self.wildcard] + pairline
        line_2 = pairline + [self.wildcard]
        return [line_1, line_2]

    def recursive_search(self, pairline, line, wordlist, words_in_line):
        remaining_letters = GRID_SIZE - len(pairline)
        for wn in [w for w in wordlist if len(w) <= remaining_letters]:
            if (not wn.in_grid) and (wn not in words_in_line):
                newline = pairline + [i for i in wn]
                new_words_in_line = words_in_line + [wn]
                if len(newline) == GRID_SIZE:
                    self.check(newline, line, new_words_in_line)
                elif len(newline) == GRID_SIZE-1:
                    for pl in self.insert_wildcards(newline):
                        self.check(pl, line, new_words_in_line)
                elif len(newline) >= GRID_SIZE - 4: #we go agen
                    newline += [self.wildcard]
                    self.recursive_search(newline, line, wordlist, new_words_in_line)
                else:
                    pass #try next word

    def check(self, pairline, line, words_in_line):
        for i, letter in enumerate(line):
            if letter not in [' ', pairline[i]]:
                return
        self.possible_pairs.append(Pair(words_in_line, pairline))

    def __repr__(self):
        return str(self.idx) + str(self.isrow)

class Grid():
    def __init__(self):
        self.grid = np.full([GRID_SIZE, GRID_SIZE], ' ', dtype=np.object)
        self.empty = True

        self.rows = self.grid
        self.cols = self.grid.T
        self.n_words_in_grid = 0

    def insert_row(self, idx, pairline):
        self.grid[idx] = pairline
        self.rows[idx] = pairline
        for i, line in enumerate(self.cols):
            line[idx] = pairline[i]
        # pairs_tried = self.rows[idx].pairs_tried
        # self.rows[idx] = Line(idx, pairline, True)
        # self.rows[idx].pairs_tried += (pairs_tried + 1)

    def insert_col(self, idx, pairline):
        self.grid[:, idx] = pairline
        self.cols[idx] = pairline
        for i, line in enumerate(self.rows):
            line[idx] = pairline[i]
        # pairs_tried = self.cols[idx].pairs_tried
        # self.cols[idx] = Line(idx, pairline, False)
        # self.cols[idx].pairs_tried += (pairs_tried + 1)
        # for i, line in enumerate(self.rows):
        #     line.line[idx] = pairline[i]

    def __len__(self):
        return self.n_words_in_grid

    def __index__(self):
        return self.grid

    def __repr__(self):
        return str(self.grid)

class Pair():
    def __init__(self, words_in_line, line=[]):
        self.words = words_in_line
        self.line = line
    #     self.num_spaces = self.compute_num_spaces()
    #
    # def compute_num_spaces(self):
    #     num_spaces = 0
    #     for letter in self.line:
    #         if letter == ' ':
    #             num_spaces +=1
    #     return num_spaces

    def __repr__(self):
        return str(self.line)

    def __iter__(self):
        return iter(self.line)

class ProgramState(object):
    def __init__(self, wordlist):

        self.grid_state = []
        self.wordlist_state = []
        self.best_grid_state = []

        grid = Grid()
        wl = WordList(wordlist)
        best_grid = None

        self.set_state(grid, wl, best_grid)
        self.increment_state(grid, wl, best_grid)
        # breakpoint()

    def get_state(self, idx):
        return self.grid_state[idx], self.wordlist_state[idx], self.best_grid_state[idx]

    def previous_state(self):
        # print('REVERTING TO PREVIOUS STATE')
        self.destroy_states(1)
        self.set_state(*self.get_state(-1))
        # print(self.grid)
        # breakpoint()

    def next_state(self):
        # print('SETTING NEXT STATE')
        new_state = self.copy_state()
        self.increment_state(*new_state)
        self.set_state(*new_state)

    def increment_state(self, grid, wordlist, best_grid):
        self.grid_state.append(grid)
        self.wordlist_state.append(wordlist)
        self.best_grid_state.append(best_grid)
        # self.rows_state.append(rows)
        # self.cols_state.append(cols)

    def copy_state(self):
        newgrid = copy.deepcopy(self.grid)
        newwordlist = copy.deepcopy(self.wordlist)
        newbestgrid = copy.deepcopy(self.best_grid)
        # newrows = copy.deepcopy(self.rows)
        # newcols = copy.deepcopy(self.cols)
        return newgrid, newwordlist, newbestgrid

    def set_state(self, grid, wordlist, best_grid):
        self.grid = grid
        self.wordlist = wordlist
        self.best_grid = best_grid
        # self.rows = rows
        # self.cols = cols

    def destroy_states(self, n_states):
        del(self.grid_state[0-n_states:])
        del(self.wordlist_state[0-n_states:])
        del(self.best_grid_state[0-n_states:])


class Filler(ProgramState):
    def __init__(self, wordlist, row_offset, col_offset):
        self.row_offset = row_offset
        self.col_offset = col_offset
        self.num_states = (GRID_SIZE-row_offset)+(GRID_SIZE-col_offset)
        super().__init__(wordlist)

        self.best_state = 0

    def fill(self):
        go = True
        # self.update_line_matches
        current_state = 0
        lines = np.arange(self.row_offset, min(GRID_SIZE, GRID_SIZE-self.row_offset))[::2].repeat(2)
        line_info = list(zip(lines, [True if x%2==0 else False for x in range(len(lines))]))
        linelist = [None]*len(lines)
        while go:
            if current_state == self.num_states-1:
                print('WE DID IT REDDIT: \n')
                print(self.grid)
                go = False
            # breakpoint()
            self.grid, self.wordlist, _ = self.get_state(current_state)
            tempgrid, tempwordlist, _ = self.copy_state()

            if linelist[current_state]==None:
                #going forwards, create new line
                current_line = Line(*line_info[current_state])
                if current_line.isrow:
                    current_line.compute_possible_words(tempwordlist, tempgrid.rows[current_line.idx]) #compute pairs for current line
                else:
                    current_line.compute_possible_words(tempwordlist, tempgrid.cols[current_line.idx])
                pairs = current_line.possible_pairs
                linelist[current_state] = current_line
            else:
                #gone back, check next pair
                current_line = linelist[current_state]
                pairs = current_line.possible_pairs[current_line.pairs_tried:]
            inserted = self.insert_pair(current_line.idx, current_line.isrow, pairs, tempgrid, tempwordlist)

            if inserted:
                current_line.pairs_tried += 1
                current_state +=1
                # self.next_state()
                self.set_state(tempgrid, tempwordlist, _)
                self.increment_state(tempgrid, tempwordlist, _)
                if current_state > self.best_state:
                    self.best_state = current_state
                    print('improvement: \n')
                    print(self.grid)
                # elif current_state == self.best_state:
                #     print('equal best: \n')
                #     print(self.grid)

            else:
                linelist[current_state] = None
                current_state -= 1
                self.previous_state()
                # breakpoint()



    def insert_pair(self, idx, isrow, pairs, grid, wordlist):
        if pairs:
            if isrow:
                grid.insert_row(idx, [letter for letter in pairs[0]])
                # self.rows[idx] = [letter for letter in pairs[0]]
            else:
                grid.insert_col(idx, [letter for letter in pairs[0]])
                # self.cols[idx] = [letter for letter in pairs[0]]
            for word in pairs[0].words:
                wordlist[word.word].in_grid=True
            # self.update_line_matches()
            # self.next_state()
            return True
        else:
            return False


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
    filler = Filler(wordlist, row_offset=1, col_offset=1)
    filler.fill()


if __name__=='__main__':
    main()
