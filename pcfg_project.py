# Full Name: Zulipiye Yusupujiang
# Date: April 18th, 2018
# Assignment: Syntactic Parsing Assignment 4

from sys import argv, stderr

from os.path import exists
#from __future__ import division
from collections import Counter, defaultdict
from json import loads, dumps
from time import time
#from stat_parser.word_classes import word_class


class PCFG:
    RARE_WORD_COUNT = 5
    
    def __init__(self):
        self.q1 = defaultdict(float)
        self.q2 = defaultdict(float)
        self.q3 = defaultdict(float)
        self.well_known_words = set()
    
    def norm_word(self, word):
        return word if word in self.well_known_words else "_RARE_" #word_class(word)
    
    def __build_caches(self):
        self.N = set()
        self.binary_rules = defaultdict(list)
        self.unary_rules = defaultdict(list)
        
        for x, _ in self.q1.keys():
            self.N.add(x)
        
        for x, y1, y2 in self.q2.keys():
            self.N.update(set([x, y1, y2]))
            self.binary_rules[x].append((y1, y2))  
      
        for x, y1 in self.q3.keys():
            self.N.update(set([x, y1]))
            self.unary_rules[x].append((y1))

    def learn_from_treebank(self, treebank):
        self.sym_count = Counter()
        self.unary_count = Counter()
        self.binary_count = Counter()
        self.words_count = Counter()
        self.unitproduction_count = Counter()
        
        for s in open(treebank):
            self.count(loads(s))
        
        # Words
        for word, count in self.words_count.items():
            if count >= PCFG.RARE_WORD_COUNT:
                self.well_known_words.add(word)
        
        # Normalise the unary rules count
        norm = Counter()
        for (x, word), count in self.unary_count.items():
            norm[(x, self.norm_word(word))] += count
        self.unary_count = norm
        
        # Q1
        for (x, word), count in self.unary_count.items():
            self.q1[x, word] = self.unary_count[x, word] / self.sym_count[x]
        
        # Q2
        for (x, y1, y2), count in self.binary_count.items():
            self.q2[x, y1, y2] = self.binary_count[x, y1, y2] / self.sym_count[x]

        # Q3
        for (x, y1), count in self.unitproduction_count.items():
            self.q3[x, y1] = self.unitproduction_count[x, y1] / self.sym_count[x]
        
        self.__build_caches()
    
    def count(self, tree):
        # Base case: terminal symbol
        if isinstance(tree, str): return
        
        # Count the non-terminal symbols
        sym = tree[0]
        self.sym_count[sym] += 1
        
        if len(tree) == 3:
            # Binary Rule
            y1, y2 = (tree[1][0], tree[2][0])
            self.binary_count[(sym, y1, y2)] += 1
            
            # Recursively count the children
            self.count(tree[1])
            self.count(tree[2])
        
        elif len(tree) == 2:
            # unit production
            if isinstance(tree[1], list):
                if isinstance(tree[1][1], str):
                    y1 = tree[1][0]
                    self.unitproduction_count[(sym, y1)] += 1
                    self.sym_count[y1] += 1
                    self.count(tree[1])

            # # Unary Rule
            if isinstance(tree[1], str):
                word = tree[1]
                self.unary_count[(sym, word)] += 1
                self.words_count[word] += 1


    def save_model(self, path):
        with open(path, 'w') as model:
            for (x, word), p in self.q1.items():
                model.write(dumps(['Q1', x, word, p]) + '\n')
            
            for (x, y1, y2), p in self.q2.items():
                model.write(dumps(['Q2', x, y1, y2, p]) + '\n')

            # Q3
            for (x, y1), p in self.q3.items():
                model.write(dumps(['Q3', x, y1, p]) + '\n')

            
            model.write(dumps(['WORDS', list(self.well_known_words)]) + '\n')
    

    def load_model(self, path):
        with open(path) as model:
            for line in model:
                data = loads(line)
                if data[0] == 'Q1':
                    _, x, word, p = data
                    self.q1[x, word] = p
                
                elif data[0] == 'Q2':
                    _, x, y1, y2, p = data
                    self.q2[x, y1, y2] = p
                
                elif data[0] == 'Q3':
                    _, x, y1, p = data
                    self.q3[x, y1] = p
                
                elif data[0] == 'WORDS':
                    self.well_known_words = data[1]
        
        self.__build_caches()


if __name__ == "__main__":

    if len(argv) != 3:
        print("usage: python3 pcfg.py TREEBANK GRAMMAR")
        exit()

    treebank_file = argv[1]
    grammar_file = argv[2]
 
    start = time()
    print("Extracting grammar from " + treebank_file + " ...", file=stderr)
    pcfg = PCFG()
    pcfg.learn_from_treebank(treebank_file)
    print("Saving grammar to " + grammar_file + " ...", file=stderr)
    pcfg.save_model(grammar_file)
    print("Time: %.2fs\n" % (time() - start), file=stderr)
