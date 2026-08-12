from collections import Counter, deque 
from itertools import permutations, product, combinations 
import copy
#from sage.all import PermutationGroup

GLOBAL_POINTVECTOR = set()

def isIllegal(pv):
    chunks = [tuple(pv[i:i+4]) for i in range(0, 20, 4)]
    rel1, rel2 = [], []
    for tup_ in chunks:
        rel1.append(tup_[1] + tup_[3])
        rel2.append(tup_[2] + tup_[3])
    
    print(rel1, rel2)
    # return true if rel1 or rel2 are a permutation of the illegal 2^3 4 6 
    return 1 #rel1, rel2


def run_collapse(globalset):
    canonical_results = set()
    unprocessed_pool = copy.deepcopy(globalset)
    i=0
    while len(unprocessed_pool) > 0:
        i += 1 

        curr = unprocessed_pool.pop()
        currmin, currvisited = collapse(curr)
        #print(currmin, currvisited, len(unprocessed_pool))
        unprocessed_pool -= currvisited
        canonical_results.add(currmin)
        print('min=', currmin)
        print(i, len(canonical_results), len(unprocessed_pool))

def is_valid_chunk(chunk):
    n00, n10, n01, n11 = chunk
    w1 = n10 + n11
    w2 = n01 + n11
    return w1 > 0 and w2 > 0   # neither relation is empty in this class

def is_valid(pv):
    chunks = [pv[i:i+4] for i in range(0, 20, 4)]
    return all(is_valid_chunk(c) for c in chunks)

def collapse(seed_pv):
    # start with a seed point vector 
    print('Starting collapse on seed vector', seed_pv)
    queue = deque([seed_pv])
    visited = {seed_pv} # initialise visited with just the seed 

    canonical_min = seed_pv
    mincount = 0
    while queue:
        current = queue.popleft()
        if not is_valid(current):
            print('current not valid', current)

        if current < canonical_min:
            mincount+=1
            canonical_min = current

        perms = parallel_class_permutations(current)
        for vec in perms:
            if vec not in visited and is_valid(vec):
                visited.add(vec)
                queue.append(vec)

        r1r2swap = swap_r1_r2(current)
        if r1r2swap not in visited and is_valid(r1r2swap):
            visited.add(r1r2swap)
            queue.append(r1r2swap)

        symdif = symm_diff(current)
        if not is_valid(symdif):
            print('symm diff constructed invalid', symdif)

        if symdif not in visited and is_valid(symdif):
            visited.add(symdif)
            queue.append(symdif)

        comp = even_complements_r1(current)
        for vec_ in comp:
            if not is_valid(vec_):
                print('vec not valid', vec_)
            if vec_ not in visited and is_valid(vec_):
                visited.add(vec_)
                queue.append(vec_)
        # if comp not in visited:
        #     visited.add(comp)
        #     queue.append(comp)

    # print(f'total minimise count {mincount}')
    print(f'total visited {len(visited)}')
    return canonical_min, visited

def even_complements_r1(pv):
    chunks = [pv[i:i+4] for i in range(0, 20, 4)]
    even_combos = []
    for k in (0, 2, 4):
        even_combos.extend(combinations(range(5), k))
    results = set()
    for combo in even_combos:
        combo_set = set(combo)
        new_vector = []
        
        for idx, chunk in enumerate(chunks):
            if idx in combo_set:
                # Swap index 0 <-> 1 and index 2 <-> 3
                complemented_chunk = (chunk[1], chunk[0], chunk[3], chunk[2])
                new_vector.extend(complemented_chunk)
            else:
                new_vector.extend(chunk)
                
        results.add(tuple(new_vector))
        
    return results

def parallel_class_permutations(pv):
    # takes as input a single pv ie length 20 vector (n00, n10, n01, n11, ...) for i=1:5
    # outputs the 120 possible output permutations of swapping as a set
    chunks = [tuple(pv[i:i+4]) for i in range(0, 20, 4)]
    vecs = {tuple(x for c in perm for x in c) for perm in permutations(chunks)}
    return vecs  # compiles all 5!=120 permutations of parallel classes of a single point vector (knet)

def swap_r1_r2(pv):
    # takes as input single pv length 20; chunks into each parallel class and swaps n10 with n01 ie idx 1 <-> 2 
    # outputs single pv after transformation
    chunks = [tuple(pv[i:i+4]) for i in range(0, 20, 4)]
    ret = tuple()
    for idx, tup in enumerate(chunks):
        temp = list(tup)
        temp[1], temp[2] = temp[2], temp[1]
        tup_ = temp
        ret += *tup_,

    # print(ret)
    return ret

def symm_diff(pv):
    # takes as input a single pv ie length 20 vector (n00, n10, n01, n11, ...) for i=1:5; chunks into each paralell class and then
    # applies symmetric difference by replacing r2 by symm diff r1 and r2, ie n10 and n11 swap 
    # outputs single pv after transformation
    chunks = [tuple(pv[i:i+4]) for i in range(0, 20, 4)]
    ret = tuple()
    for idx, tup in enumerate(chunks):
        temp = list(tup)
        temp[1], temp[3] = temp[3], temp[1]
        tup_ = temp
        ret += *tup_,

    return ret

class Relation:
    def __init__(self):
        self.A = [2,2,4,4,4]
        self.B = [2,4,4,4,6]
        self.C = [4,4,4,4,4]

def construct_intersections(w1, w2):
    A_min = max(0, w1 + w2 - 10)
    A_max = min(w1, w2)
    # in the order of (n00, n10, n01, n11)
    if w1 != w2:
        intersections = [
            [10 - (w1 + w2 - A), w1 - A, w2 - A, A]
            for A in range(A_min, A_max + 1)
        ]
    else:
        intersections = [
            [10 - (w1 + w2 - A), w1 - A, w2 - A, A]
            for A in range(A_min, A_max)
        ]

    return intersections

def construct_pairs(relation1, relation2):
    for idx, value in enumerate(set(permutations(relation2))):
        relo1 = relation1 
        relo2 = list(value)
        M = []

        for w1, w2 in zip(relo1,relo2):
            M.append(construct_intersections(w1,w2))

        # cartisian product to get all configurations of intersections for each parallel class 
        # i think this is a bit dodgy 
        cart = product(*M)
        for val in cart:
            pv = tuple(num for group in val for num in group)
            GLOBAL_POINTVECTOR.add(pv)

def main():
    relations = Relation()
    pairs = [
        [relations.A, relations.B],
        [relations.A, relations.B],
        [relations.A, relations.C],
        [relations.B, relations.B],
        [relations.B, relations.C],
        [relations.C, relations.C]
    ]
    #print(combinations((relations.A, relations.B, relations.C)))
    for lst in pairs:
        construct_pairs(lst[0], lst[1])


    #collapse(next(my_iterator))  # Grabs the second item and passes it in
    run_collapse(GLOBAL_POINTVECTOR)


if __name__ == "__main__":
    main()
