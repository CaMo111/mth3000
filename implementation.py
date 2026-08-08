from collections import Counter, deque 
from itertools import permutations, product, combinations 

GLOBAL_POINTVECTOR = set()

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
    print(set(permutations(relation2)))
    for idx, value in enumerate(set(permutations(relation2))):
        relo1 = relation1 
        relo2 = list(value)
        M = []
        #print(idx, relo1, relo2)
        for w1, w2 in zip(relo1,relo2):
            M.append(construct_intersections(w1,w2))

        # cartisian product to get all configurations of intersections for each parallel class 
        cart = product(*M)
        for val in cart:
            pv = tuple(num for group in val for num in group)
            print(pv)
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
    print(len(GLOBAL_POINTVECTOR))
    print(GLOBAL_POINTVECTOR)




if __name__ == "__main__":
    main()
