from collections import Counter, deque 
from itertools import permutations, product, combinations 
import copy
import sys

class PointVector:
    def __init__(self, v, hist: list, rule='init'):
        # rule = 1. permute, 2 r1r2swap 3. symdiff 4.even complement
        self.v = v
        if hist != None:
            self.history = hist + [v, rule]
        else:
            self.history = [v, rule]

    def __hash__(self):
        return hash(self.v)
    
    def __repr__(self):
        return f"PointVector={self.v} \n HISTORY={self.history} \n"

    def __getitem__(self, item):
        return self.v[item]

    # --- MAKES ITERATION & LENGTH WORK ---
    def __iter__(self):
        return iter(self.v)

    def __len__(self):
        return len(self.v)

    # --- MAKES COMPARISONS WORK (for canonical_min check) ---
    def __lt__(self, other):
        if isinstance(other, PointVector):
            return self.v < other.v
        return self.v < other

    def __eq__(self, other):
        if isinstance(other, PointVector):
            return self.v == other.v
        return self.v == other

GLOBAL_POINTVECTOR = set()

LEGAL = [
(2,2,4,4,4),
(2,4,4,4,6),
(4,4,4,4,4)
]

WEIGHTDISTRIBUTIONS = []

def normalize_profile(profile):
    normalized = [min(x, 10 - x) for x in profile]
    return sorted(normalized)

def isValidSymdiffProfile(pv):
    chunks = [tuple(pv[i:i+4]) for i in range(0, 20, 4)]
    profile = tuple(sorted(chunk[1] + chunk[2] for chunk in chunks))
    # print('profile=', normalize_profile(profile))
    # print('normalised relations', normalize_profile(list(profile)), normalize_profile(LEGAL[0]), normalize_profile(LEGAL[1]), normalize_profile(LEGAL[2]))
    # need to ensure profile after symmdiff still retains relational structure? 
    if normalize_profile(list(profile)) == normalize_profile(LEGAL[0]) or normalize_profile(list(profile)) == normalize_profile(LEGAL[1]) or normalize_profile(list(profile)) == normalize_profile(LEGAL[2]):
        #print('valid')
        return True
    else:
        return False
    # return (profile in LEGAL, profile)

def isEvenIntersection(pv):
    chunks = [tuple(pv[i:i+4]) for i in range(0, 20, 4)]
    ev = 0
    for tup_ in chunks:
        ev += tup_[3]
    
    return not bool(ev%2) # 0 returns True because it's even


def run_collapse(globalset, f):
    canonical_results = set()
    unprocessed_pool = copy.deepcopy(globalset)
    i=0
    while len(unprocessed_pool) > 0:
        i += 1 

        curr = unprocessed_pool.pop()
        currmin, currvisited = collapse(curr)
        if currmin == None:
            unprocessed_pool -= currvisited
            print('invalid seed')
            print(i, len(canonical_results), len(unprocessed_pool))
        else:
            unprocessed_pool -= currvisited
            canonical_results.add(currmin)
            print('min=', currmin)
            f.write(f'MIN={currmin.v}\n')
            f.flush()
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
    print('Starting collapse on seed vector', seed_pv, type(seed_pv))
    queue = deque([seed_pv])
    visited = {seed_pv} # initialise visited with just the seed 

    canonical_min = seed_pv
    mincount = 0
    while queue:
        current = queue.popleft()
        if isEvenIntersection(current)==False:
            print('Odd intersection', isEvenIntersection(current))
        
        if not isValidSymdiffProfile(current):
            print('curr symdiff corrupt', current)
            return None, visited

        if not is_valid(current):
            print('current not valid', current)
            return None, visited

        if current < canonical_min:
            mincount+=1
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

    print(f'total visited {len(visited)}')
    return canonical_min, visited

def even_complements_r1(pv):
    chunks = [pv[i:i+4] for i in range(0, 20, 4)]
    even_combos = []
    # for k in (0, 2, 4):
    even_combos.extend(combinations(range(5), 2))
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

        clean =  PointVector(tuple(new_vector), pv.history, 'Complement')
        # if is_valid(clean):
        results.add(clean)
        
    return results

def parallel_class_permutations(pv):
    # takes as input a single pv ie length 20 vector (n00, n10, n01, n11, ...) for i=1:5
    # outputs the 120 possible output permutations of swapping as a set
    chunks = [tuple(pv[i:i+4]) for i in range(0, 20, 4)]
    vecs = {PointVector(tuple(x for c in perm for x in c), pv.history, 'Permute') for perm in permutations(chunks)}
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

    retp_ = PointVector(ret, pv.history, 'R1/R2 Swap')
    # print(ret)
    return retp_

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

    retp_ = PointVector(ret, pv.history, 'SymDiff')
    # if is_valid(retp_):
    return retp_
    # else:
    #     return None

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

def construct_pairs(relation1, relation2, sk_l=None):
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
            if sk_l != None:
                sk_l.add(pv)

def main():
    with open("implementation.txt", "w") as f:
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
            construct_pairs(lst[0], lst[1])

        #collapse(next(my_iterator))  # Grabs the second item and passes it in
        new_global_set = set()
        for item in GLOBAL_POINTVECTOR:
            tmp = PointVector(item, None)
            new_global_set.add(tmp)

        filter_parity = set()
        for item_ in new_global_set:
            if isEvenIntersection(item_):
                filter_parity.add(item_)
            
        GLOBAL_POINTVECTOR2 = new_global_set
        GLOBAL_POINTVECTOR3 = filter_parity


        # try filter out invalid symmdiff?
        filter_sdiff = set()
        for vec in GLOBAL_POINTVECTOR3:
            if isValidSymdiffProfile(vec):
                filter_sdiff.add(vec)

        GLOBAL_POINTVECTOR4 = filter_sdiff        
        run_collapse(GLOBAL_POINTVECTOR4, f)

        #print(len(GLOBAL_POINTVECTOR3))


if __name__ == "__main__":
    main()
