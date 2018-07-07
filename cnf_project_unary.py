# Allows unit productions in the treebank file

from sys import stdin, stderr
from json import loads, dumps

def cnf(tree):
    #eliminating n-ary branching subtrees by inserting additional nodes:
    subtree = tree[1:]
    n = len(subtree)
    if n == 2:
        lst = subtree[0]
        rst = subtree[1]
        return [tree[0], cnf(lst), cnf(rst)]
    if n > 2:
        lst = subtree[0]
        rst = subtree[1:]
        del tree[2:]
        node = str(tree[0]) + "|" + str(lst[0])
        rst.insert(0, node)
        tree.insert(2, rst)
        return [tree[0], cnf(lst), cnf(rst)]


def is_cnf(tree):
    n = len(tree)
    if n == 2:
        return tree
    if n == 3:
        return is_cnf(tree[1]) and is_cnf(tree[2])
    else:
        return False

def words(tree):
    if isinstance(tree, str):
        return [tree]
    else:
        ws = []
        for t in tree[1:]:
            ws = ws + words(t)
        return ws

if __name__ == "__main__":

    for line in stdin:
        tree = loads(line)
        sentence = words(tree)
        input = str(dumps(tree))
        cnf(tree)
        if is_cnf(tree) and words(tree) == sentence:
            print(dumps(tree))
        else:
            print("Something went wrong!", file=stderr)
            print("Sentence: " + " ".join(sentence), file=stderr)
            print("Input: " + input, file=stderr)
            print("Output: " + str(dumps(tree)), file=stderr)
            exit()


