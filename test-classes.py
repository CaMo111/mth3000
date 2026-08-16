# purpose of this script is to pull out random vectors from the global set
# generate everything that is valid, and then see if for all of these vectors, precisley one vector is shared between the two sets
# this would then infer that preprocessing and case generation is the only thing that could be having problems.
from collections import Counter, deque 
from itertools import permutations, product, combinations 
import copy
import sys
from implementation import PointVector, collapse, Relation, construct_pairs, isEvenIntersection, isValidSymdiffProfile, is_valid, parallel_class_permutations, swap_r1_r2, symm_diff, even_complements_r1
import random

GLOBAL_POINTVECTOR = set()
EQUIV_CLASSES = set()   

def genVecSpace(pv):
    #takes a single point vector and generates all validly isomorphic things under our 4 rules. If we create something that is invalid, we pass, and do not add to the set.
    queue = deque([pv])
    visited = {pv} # initialise visited with just the seed 

    canonical_min = pv
    print(f'running on configuration point vector: {pv}')
    while queue:
        current = queue.popleft()       
        #print(current.v) 
        if not is_valid(current) or not isValidSymdiffProfile(current):
            pass
        else:
            #expand search size
            if current < canonical_min:
                canonical_min = current

            perms = parallel_class_permutations(current)
            for vec in perms:
                if vec not in visited:
                    visited.add(vec)
                    queue.append(vec)

            r1r2swap = swap_r1_r2(current)
            if r1r2swap not in visited:
                visited.add(r1r2swap)
                queue.append(r1r2swap)

            symdif = symm_diff(current)
            if symdif not in visited:
                visited.add(symdif)
                queue.append(symdif)

            comp = even_complements_r1(current)
            for vec_ in comp:
                if vec_ not in visited:
                    visited.add(vec_)
                    queue.append(vec_)

    print(f'MIN={canonical_min}')
    print(f'visited={len(visited)}')
    return canonical_min, visited

def main():
    with open('logs.txt') as f:
        lines = [line.rstrip() for line in f]
        for idx, line in enumerate(lines):
            str_ = line[4:]
            lines[idx] = tuple(map(int, str_.strip('()').split(',')))
            EQUIV_CLASSES.add(PointVector(lines[idx], None))
            
            
    relations = Relation()
    pairs = [
        [relations.A, relations.A],
        [relations.A, relations.B],
        [relations.A, relations.C],
        [relations.B, relations.B],
        [relations.B, relations.C],
        [relations.C, relations.C]
    ]
    #print(combinations((relations.A, relations.B, relations.C)))
    for lst in pairs:
        construct_pairs(lst[0], lst[1], GLOBAL_POINTVECTOR)

    new_global_set = set()
    for item in GLOBAL_POINTVECTOR:
        tmp = PointVector(item, None)
        new_global_set.add(tmp)

    filter_parity = set()
    for item_ in new_global_set:
        if isEvenIntersection(item_):
            filter_parity.add(item_)
        
    GLOBAL_POINTVECTOR3 = filter_parity
    #GLOBAL_POINTVECTOR3 = list(GLOBAL_POINTVECTOR3)
    #print(list(GLOBAL_POINTVECTOR3))


    filter_sdiff = set()
    for vec in GLOBAL_POINTVECTOR3:
        if isValidSymdiffProfile(vec):
            filter_sdiff.add(vec)

    GLOBAL_POINTVECTOR4 = list(filter_sdiff)


    print(len(GLOBAL_POINTVECTOR4))
    #genVecSpace(GLOBAL_POINTVECTOR4[random.randint(1,len(GLOBAL_POINTVECTOR4))])
    genVecSpace(GLOBAL_POINTVECTOR4[0])

if __name__ == "__main__":
    main()