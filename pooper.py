from collections import Counter, deque 
from itertools import permutations, product, combinations 
import copy

class PointVector:
    def __init__(self, v, hist: list=None, rule='init'):
        self.v = v
        self.history = hist + [v, rule] if hist else [v, rule]

    def __hash__(self): return hash(self.v)
    def __repr__(self): return f"PointVector={self.v} \n HISTORY={self.history} \n"
    def __getitem__(self, item): return self.v[item]
    def __iter__(self): return iter(self.v)
    def __len__(self): return len(self.v)
    def __lt__(self, other): return self.v < other.v if isinstance(other, PointVector) else self.v < other
    def __eq__(self, other): return self.v == other.v if isinstance(other, PointVector) else self.v == other

GLOBAL_POINTVECTOR = set()

def is_valid_chunk(chunk):
    n00, n10, n01, n11 = chunk
    return (n10 + n11) > 0 and (n01 + n11) > 0

def is_valid(pv):
    return all(is_valid_chunk(pv[i:i+4]) for i in range(0, 20, 4))

def run_collapse(globalset, f):
    canonical_results = set()
    unprocessed_pool = copy.deepcopy(globalset)
    i = 0
    while unprocessed_pool:
        i += 1 
        curr = unprocessed_pool.pop()
        currmin, currvisited = collapse(curr)
        
        # Valid state check applied *after* collapse traversal
        if currmin and is_valid(currmin):
            canonical_results.add(currmin)
            f.write(f'MIN={currmin.v}\n')
            f.flush()
            print(f'Seed {i} -> Min Found. Total Classes: {len(canonical_results)}')
        
        unprocessed_pool -= currvisited
    
    print(f"Final Count of Equivalence Classes: {len(canonical_results)}")

def collapse(seed_pv):
    queue = deque([seed_pv])
    visited = {seed_pv}
    canonical_min = seed_pv

    while queue:
        current = queue.popleft()
        
        # Only evaluate canonical minimum against valid states
        if is_valid(current) and current < canonical_min:
            canonical_min = current

        # Apply all symmetry operations
        next_states = set()
        next_states.update(parallel_class_permutations(current))
        next_states.add(swap_r1_r2(current))
        next_states.add(symm_diff(current))
        next_states.update(even_complements_r1(current))
        # If R2 complement is valid in your algebra, add: next_states.update(even_complements_r2(current))

        for vec in next_states:
            if vec not in visited:
                visited.add(vec)
                queue.append(vec)

    return canonical_min, visited

def even_complements_r1(pv):
    chunks = [pv[i:i+4] for i in range(0, 20, 4)]
    even_combos = list(combinations(range(5), 2)) + list(combinations(range(5), 4)) # Re-added length 4
    results = set()
    for combo in even_combos:
        combo_set = set(combo)
        new_vector = []
        for idx, chunk in enumerate(chunks):
            if idx in combo_set:
                new_vector.extend((chunk[1], chunk[0], chunk[3], chunk[2]))
            else:
                new_vector.extend(chunk)
        results.add(PointVector(tuple(new_vector), pv.history, 'Complement R1'))
    return results

def parallel_class_permutations(pv):
    chunks = [tuple(pv[i:i+4]) for i in range(0, 20, 4)]
    return {PointVector(tuple(x for c in perm for x in c), pv.history, 'Permute') 
            for perm in permutations(chunks)}

def swap_r1_r2(pv):
    chunks = [list(pv[i:i+4]) for i in range(0, 20, 4)]
    for chunk in chunks:
        chunk[1], chunk[2] = chunk[2], chunk[1]
    return PointVector(tuple(x for c in chunks for x in c), pv.history, 'R1/R2 Swap')

def symm_diff(pv):
    chunks = [list(pv[i:i+4]) for i in range(0, 20, 4)]
    for chunk in chunks:
        chunk[1], chunk[3] = chunk[3], chunk[1]
    return PointVector(tuple(x for c in chunks for x in c), pv.history, 'SymDiff')

class Relation:
    def __init__(self):
        self.A = [2,2,4,4,4]
        self.B = [2,4,4,4,6]
        self.C = [4,4,4,4,4]

def construct_intersections(w1, w2):
    A_min = max(0, w1 + w2 - 10)
    A_max = min(w1, w2)
    
    # Bug Fix: Both branches now correctly generate up to A_max inclusive
    return [
        [10 - (w1 + w2 - A), w1 - A, w2 - A, A]
        for A in range(A_min, A_max + 1) 
    ]

def construct_pairs(relation1, relation2):
    for value in set(permutations(relation2)):
        relo1 = relation1 
        relo2 = list(value)
        M = [construct_intersections(w1, w2) for w1, w2 in zip(relo1, relo2)]
        
        for val in product(*M):
            pv = tuple(num for group in val for num in group)
            GLOBAL_POINTVECTOR.add(pv)

def main():
    with open("pooper.txt", "w") as f:
        relations = Relation()
        pairs = [[relations.A, relations.B]]
        
        for lst in pairs:
            construct_pairs(lst[0], lst[1])

        GLOBAL_POINTVECTOR2 = {PointVector(item, None) for item in GLOBAL_POINTVECTOR}
        run_collapse(GLOBAL_POINTVECTOR2, f)

if __name__ == "__main__":
    main()