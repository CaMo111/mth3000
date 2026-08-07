from collections import Counter # for checking permutations
from itertools import permutations, product # for constructing all permutations and getting cartisian product for Mk matrix  

# THE PURPOSE OF THIS SCRIPT IS TO TAKE THE 3 FORMS OF WEIGHT DISTRIBUTION AND ENUMERATE 
# TO FIND ALL DIFFERENT 'CASES' OF 3 MOLS 10 THAT SATISFY 2 RELATIONS.
# we eliminate via permutations, complements and SD.

def is_permutation(tuple1, tuple2):
    return Counter(tuple1) == Counter(tuple2)

def generate_configs(ordering1, ordering2):
    # takes two orderings (eg output from construct type arrays), zips them together while calling get_overlaps to construct all possible 
    # configurations. Eg the cartisian product of these two weight distributions. 
    M = []
    for i, (c1, c2) in enumerate(zip(ordering1, ordering2)):
        M.append(get_overlaps(c1,c2))
    
    cartesian_product = product(*M)
    return list(cartesian_product)

def construct_type_arrays(t):
    # wrapping in 'set' yields distinct, unique permutations of type arrays 
    # for p in set(permutations(t)):
    #     print(p)
    #print('All possible relation permutations (unique): ', list(set(permutations(t))))
    return list(set(permutations(t)))

def get_overlaps(c1, c2):
    # takes single class counts as input parameters. Eg weight(R)=2 and weight(K)=4, gives c1=2, c2=4 
    Mk_possible = []
    for overlap in range(0, min(c1,c2)+1):
        n11 = overlap # intersection of parallel lines eg in both R1 and R2 
        n10 = c1 - n11
        n01 = c2 - n11 
        n00 = 10 - (n11+n10+n01)
        #print(n00, n10, n01, n11)
        Mk_possible.append((n00, n10, n01, n11))

    # the output are all possible Mk tuples
    #print('All possible intersection tuples. This is in the form of n00, n10, n01 and n11: \n', Mk_possible)
    return Mk_possible

def construct_profiles(pairs):
    val = []
    for pair in pairs:
        relA = construct_type_arrays(pair[0])
        relB = construct_type_arrays(pair[1])
        for weight_distribution1 in relA:
            for weight_distribution2 in relB:
                val.append(generate_configs(weight_distribution1, weight_distribution2))

    print(len(val))
    print(val[0])
    flatten = [element for row in val for element in row]
    print(len(flatten))
    print('very first candidate profile, eg relation A, relation A permutation 1 with itself yields; ', flatten[0])
    return flatten

def main():
    # Comes in 3 forms; (2^2)(4^3), 2(4^3)6, 4^5
    RELATION_A = [2,2,4,4,4]
    RELATION_B = [2,4,4,4,6]
    RELATION_C = [4,4,4,4,4]

    PAIRS = [
        [RELATION_A, RELATION_A],
        [RELATION_A, RELATION_B],
        [RELATION_A, RELATION_C],
        [RELATION_B, RELATION_B],
        [RELATION_B, RELATION_C],
        [RELATION_C, RELATION_C]
    ]

    """
    each k-net will be represented like k an element of (R, K, l1, l2, l3) ==> (M1, M2, M3, M4, M5)
    where Mk = (n00, n10, n01, n11) eg contributes to 0 relations, contributes to first but not second
    second but not first or contributes to both. The Sum of Mk stricly = 10.
    """
    # print(get_overlaps(4, 4))
    get_overlaps(2,4)
    rel = construct_type_arrays(RELATION_A)
    #print('rel', rel)
    cfgs = generate_configs(rel[0], rel[1])


    #print(len(cfgs))
    #print('\n candidate profile; ')
    #print(cfgs[0:1]) # this is one sample k-net! 
    construct_profiles(PAIRS) # currently at some 870,000~ candidate profiles; 
    # need to somehow collapse these into the 120~ unique profiles via
    # 1. permutation equviliance, 2. complement equviliance, 3. symmetric difference equviliance.

if __name__ == '__main__':
    main()