# purpose of this script is to pull out random vectors from the global set
# generate everything that is valid, and then see if for all of these vectors, precisley one vector is shared between the two sets
# this would then infer that preprocessing and case generation is the only thing that could be having problems.
from collections import Counter, deque 
from itertools import permutations, product, combinations 
import copy
import sys
from implementation import PointVector, collapse

EQUIV_CLASSES = set()   

def genVecSpace(pv):
    collapse(pv)
    #takes a single point vector and generates all validly isomorphic things under our 4 rules. If we create something that is invalid, we pass, and do not add to the set.
    

def main():
    with open('logs.txt') as f:
        lines = [line.rstrip() for line in f]
        for idx, line in enumerate(lines):
            str_ = line[4:]
            lines[idx] = tuple(map(int, str_.strip('()').split(',')))
            EQUIV_CLASSES.add(PointVector(lines[idx], None))
            #print()
    
    print(EQUIV_CLASSES)
    print(len(EQUIV_CLASSES))

    genVecSpace(next(iter(EQUIV_CLASSES)))

if __name__ == "__main__":
    main()