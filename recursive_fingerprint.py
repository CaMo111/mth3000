from collections import Counter, deque # for checking permutations
from itertools import permutations, product, combinations # for constructing all permutations and getting cartisian product for Mk matrix  

# THE PURPOSE OF THIS SCRIPT IS TO TAKE THE 3 FORMS OF WEIGHT DISTRIBUTION AND ENUMERATE 
# TO FIND ALL DIFFERENT 'CASES' OF 3 MOLS 10 THAT SATISFY 2 RELATIONS.
# we eliminate via permutations, complements and SD.

positions = [0, 1, 2, 3, 4]
even_lengths = [2, 4]
VALID_COMBOS = []
for length in even_lengths:
    for combo in combinations(positions, length):
        VALID_COMBOS.append(combo)

def apply_transforms(knet):
    base_transforms = []
    base_transforms.append(knet)
    base_transforms.append(apply_r1_equals_r2(knet))
    base_transforms.append(apply_symmetric_difference(knet))
    base_transforms.extend(apply_even_complements(knet))

    # Apply class permutations to all transformed states
    output = []
    for state in base_transforms:
        for perm in permutations(state):
            # Sorting the 5 classes gives us a canonical order for this specific state
            output.append(tuple(sorted(perm)))

    return output

def apply_permutations(knet):
    perms = list(permutations(knet)) 
    return perms 

def apply_r1_equals_r2(knet):
    perms_r1r2swap = list(knet)
    for idx, tup in enumerate(perms_r1r2swap):
        temp = list(tup)
        temp[1], temp[2] = temp[2], temp[1]
        tup_ = tuple(temp)
        perms_r1r2swap[idx] = tup_
    
    return tuple(perms_r1r2swap)

def apply_symmetric_difference(knet):
    perms_symdiff = list(knet)
    for idx, tup in enumerate(perms_symdiff):
        temp = list(tup)
        temp[1], temp[3] = temp[3], temp[1]
        tup_ = tuple(temp)
        perms_symdiff[idx] = tup_

    return tuple(perms_symdiff)

def apply_even_complements(knet):
    acc = []
    for tupletransform in VALID_COMBOS:
        net_p = knet 
        perms_complement = list(knet)
        for idx in tupletransform:
            # swap r1 with r2  and r3 with r4 
            temp = list(net_p[idx])
            temp[0], temp[1] = temp[1], temp[0]
            temp[2], temp[3] = temp[3], temp[2]
            tup_ = tuple(temp)
            perms_complement[idx] = tup_
        acc.append(tuple(perms_complement))

    return tuple(acc)

#apply_even_complements(((0, 2, 4, 4), (1, 3, 3, 3), (1, 3, 3, 3), (1, 7, 1, 1), (2, 4, 2, 2)))

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
    return list(set(permutations(t)))

def get_overlaps(c1, c2):
    # takes single class counts as input parameters. Eg weight(R)=2 and weight(K)=4, gives c1=2, c2=4 
    Mk_possible = []
    min_overlap = max(0, c1 + c2 - 10)
    max_overlap = min(c1, c2)
    for overlap in range(min_overlap, max_overlap+1):
        n11 = overlap # intersection of parallel lines eg in both R1 and R2 
        n10 = c1 - n11
        n01 = c2 - n11 
        n00 = 10 - (n11+n10+n01)
        if n00 % 2 == 0 and n10 % 2 == 0 and n01 % 2 == 0 and n11 % 2 == 0:
            Mk_possible.append((n00, n10, n01, n11))

    # the output are all possible Mk tuples
    #print('All possible intersection tuples. This is in the form of n00, n10, n01 and n11: \n', Mk_possible)
    # think i need to reconsider this, 
    # firstly each point needs to be even so this is generating a bunch of horse shit 
    return Mk_possible

print(get_overlaps(4,2))

def construct_profiles(pairs):
    val = []
    for pair in pairs:
        relA = construct_type_arrays(pair[0])
        relB = construct_type_arrays(pair[1])
        for weight_distribution1 in relA:
            for weight_distribution2 in relB:
                val.append(generate_configs(weight_distribution1, weight_distribution2))


    flatten = [element for row in val for element in row]

    return flatten

def construct_fingerprint(knet):
    start = tuple(sorted(knet))
    visited = {start}
    queue = deque([start])

    canonical_min = start

    while queue:
        current = queue.popleft()  # current is ALWAYS a single 5-class knet!

        # Check: len(current) is guaranteed to be 5 here
        if current < canonical_min:
            canonical_min = current

        # Generate single 5-class neighbor knets
        for neighbor in apply_transforms(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return canonical_min

def basis_and_complement(m):
    # takes as input some m = (n00, n10, n01, n11), yeilds 24 equviliant transforms
    # I got these transforms via AI 
    basis_transform = [(0,1,2,3), (0,2,1,3), (0,3,2,1), (0,2,3,1), (0,1,3,2), (0,3,1,2)] # 6 change of basis we can have (eg symmetric differences)
    complement_transform = [(0,1,2,3), (1,0,3,2), (2,3,0,1), (3,2,1,0)]
    Mat = []
    for basis in basis_transform:
        for complement in complement_transform:
            mpp = tuple(m[basis[c]] for c in complement)
            Mat.append(mpp)

    return(list(set(Mat)))

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
    get_overlaps(2,4)
    rel = construct_type_arrays(RELATION_A)
    cfgs = generate_configs(rel[0], rel[1])


    profiles = construct_profiles(PAIRS) # currently at some 870,000~ candidate profiles; 
    # need to somehow collapse these into the 120~ unique profiles via
    # 1. permutation equviliance, 2. complement equviliance, 3. symmetric difference equviliance.

    #searched = basis_and_complement(profiles[0][0]) # profiles[0][0]

    #searchy = construct_fingerprint(profiles[103]) # profiles[24]

    uq = set()


    for i, candidate in enumerate(profiles):
        finger = construct_fingerprint(candidate)
        uq.add(finger)
        #print(i)
        print(len(uq))
        print((i/len(profiles)))
        if len(uq) == 567:
            print('uq=',uq)
            break

    print(uq)
    print(len(uq))


if __name__ == '__main__':
    main()