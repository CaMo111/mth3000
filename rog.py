from collections import Counter, deque 
from itertools import permutations, product, combinations 
import numpy as np
from scipy.optimize import linprog

GLOBAL_POINTVECTOR = set()
PT = list(product(range(4), repeat=5))
A_MATRIX = np.array(
    [[1] * 1024] + 
    [[p[c] == s for p in PT] for c in range(5) for s in range(4)] + 
    [[p[c1] == s1 and p[c2] == s2 for p in PT] 
     for c1, c2 in combinations(range(5), 2) for s1, s2 in product(range(4), repeat=2)],
    dtype=float
)

def is_valid(pv):
    """Checks if a point vector has a valid non-negative integer solution."""
    # Construct the target b-vector for this specific 20-tuple
    b = [100] + [v * 10 for v in pv] + \
        [pv[c1*4+s1] * pv[c2*4+s2] 
         for c1, c2 in combinations(range(5), 2) for s1, s2 in product(range(4), repeat=2)]
    
    # Run the solver (integrality=1 forces strict integer solutions)
    res = linprog(np.zeros(1024), A_eq=A_MATRIX, b_eq=b, integrality=1, bounds=(0, None))
    print('called', res)
    return res.success

class Relation:
    def __init__(self):
        self.A = [2,2,4,4,4]
        self.B = [2,4,4,4,6]
        self.C = [4,4,4,4,4]

def construct_intersections(w1, w2):
    A_min = max(0, w1 + w2 - 10)
    A_max = min(w1, w2)
    # in the order of (n00, n10, n01, n11)
    intersections = [
        [10 - (w1 + w2 - A), w1 - A, w2 - A, A]
        for A in range(A_min, A_max + 1)
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
        cart = product(*M)
        for val in cart:
            pv = tuple(num for group in val for num in group)
            #print(pv)
            GLOBAL_POINTVECTOR.add(pv)

def main():
    relations = Relation()
    pairs = [
        [relations.A, relations.A],
        [relations.A, relations.B],
        [relations.A, relations.C],
        [relations.B, relations.B],
        [relations.B, relations.C],
        [relations.C, relations.C],
    ]
    #print(combinations((relations.A, relations.B, relations.C)))
    for lst in pairs:
        construct_pairs(lst[0], lst[1])

    #print(len(GLOBAL_POINTVECTOR))
    #print(GLOBAL_POINTVECTOR)
    #for item in GLOBAL_POINTVECTOR:
    #    print(item)
    #print(len(GLOBAL_POINTVECTOR))
    print(GLOBAL_POINTVECTOR)
    valid_configs = {pv for pv in GLOBAL_POINTVECTOR if is_valid(pv)}
    
    print(f"Final valid overlap configurations: {len(valid_configs)}")
    for config in valid_configs:
        print(config)


if __name__ == "__main__":
    main()
