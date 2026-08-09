from sage.all import PermutationGroup
from itertools import permutations, product
from operator import itemgetter

def get_overlaps(c1, c2):
    if c1%2==1 or c2%2==1:
        print('ERROR')
    Mk_possible = []
    min_overlap = max(0, c1 + c2 - 10)
    max_overlap = min(c1, c2)
    for overlap in range(min_overlap, max_overlap+1):
        n11 = overlap 
        n10 = c1 - n11
        n01 = c2 - n11 
        n00 = 10 - (n11+n10+n01)
        if (n00 % 2 == 0 and n10 % 2 == 0 and n01 % 2 == 0 and n11 % 2 == 0) or (n00 % 2 == 1 and n10 % 2 == 1 and n01 % 2 == 1 and n11 % 2 == 1):
            Mk_possible.append((n00, n10, n01, n11))

    return Mk_possible

def generate_configs(ordering1, ordering2):
    M = []
    for i, (c1, c2) in enumerate(zip(ordering1, ordering2)):
        M.append(get_overlaps(c1,c2))
    
    cartesian_product = product(*M)
    return list(cartesian_product)

def construct_type_arrays(t):
    return list(set(permutations(t)))

def construct_profiles(pairs):
    val = []
    #relA = construct_type_arrays(pair[0])
    for pair in pairs:
        relB = construct_type_arrays(pair[1])
        for weight_distribution2 in relB:
            val.append(generate_configs(pair[0], weight_distribution2))

    flatten = [element for row in val for element in row]
    return flatten

# 1. Define the Permutation Group Generators on 20 points
generators_str = [
    "(1,5)(2,6)(3,7)(4,8)",         # Swap Row 1 and 2
    "(5,9)(6,10)(7,11)(8,12)",      # Swap Row 2 and 3
    "(9,13)(10,14)(11,15)(12,16)",  # Swap Row 3 and 4
    "(13,17)(14,18)(15,19)(16,20)", # Swap Row 4 and 5
    "(2,3)(6,7)(10,11)(14,15)(18,19)", # Exchange R1 and R2
    "(2,4)(6,8)(10,12)(14,16)(18,20)", # Symmetric Difference
    "(1,2)(3,4)(5,6)(7,8)",         # Complement Row 1 and Row 2
    "(1,2)(3,4)(9,10)(11,12)",      # Complement Row 1 and Row 3
    "(1,2)(3,4)(13,14)(15,16)",     # Complement Row 1 and Row 4
    "(1,2)(3,4)(17,18)(19,20)"      # Complement Row 1 and Row 5
]

print("Initializing Permutation Group in SageMath...")
G = PermutationGroup(generators_str)
print(f"Group Order (Symmetries per configuration): {G.order()}")

# 2. Pre-calculate C-optimized orbit mappings
print("Pre-calculating orbit mappings for maximum performance...")
MAPPINGS = []
for g in G:
    ginv = g.inverse()
    # Convert GAP's 1-based indexing to Python's 0-based indexing
    mapping = tuple(ginv(i + 1) - 1 for i in range(20))
    # itemgetter runs entirely in C, bypassing Python loop overhead 
    MAPPINGS.append(itemgetter(*mapping))

def get_canonical_knet(knet):
    """
    Applies all group mappings in pure Python/C and returns the absolute 
    lexicographical minimum.
    """
    # Flatten the 5x4 knet into a single 20-element tuple
    flat = tuple(val for row in knet for val in row)
    
    # Apply all MAPPINGS instantly using the C-optimized getters, then find min
    best_flat = min(getter(flat) for getter in MAPPINGS)
    print(best_flat)

    # Reshape back into a 5-tuple of 4-tuples
    return tuple(
        tuple(best_flat[i : i+4]) 
        for i in range(0, 20, 4)
    )

def main():
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

    print("Building candidate profiles...")
    profiles = construct_profiles(PAIRS)
    
    uq = set()
    total_profiles = len(profiles)

    print(f"Total candidate profiles to canonicalize: {total_profiles}")
    
    for i, candidate in enumerate(profiles):
        canonical = get_canonical_knet(candidate)
        uq.add(canonical)
        

        print(f"Processed: {i} / {total_profiles} | Unique found: {len(uq)}")

    print(f"\nFinal Unique Profiles: {len(uq)}")

if __name__ == '__main__':
    main()