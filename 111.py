from collections import Counter, deque # for checking permutations
from itertools import permutations, product, combinations # for constructing all permutations and getting cartisian product for Mk matrix  

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
    return list(set(permutations(t)))

def get_overlaps(c1, c2):
    Mk_possible = []
    min_overlap = max(0, c1 + c2 - 10)
    max_overlap = min(c1, c2)
    for overlap in range(min_overlap, max_overlap+1):
        n11 = overlap 
        n10 = c1 - n11
        n01 = c2 - n11 
        n00 = 10 - (n11+n10+n01)
        
        # --- NEW: ENFORCE EVENNESS ---
        # A valid relation requires that each point is on an even number of lines.
        # This eliminates the 96 cases that have no integer solutions.
        if (n00 % 2 == 0 and n10 % 2 == 0 and n01 % 2 == 0 and n11 % 2 == 0) or (n00 % 2 == 1 and n10 % 2 == 1 and n01 % 2 == 1 and n11 % 2 == 1):
            Mk_possible.append((n00, n10, n01, n11))

    return Mk_possible

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
def get_neighbors(knet):
    """
    Takes a single k-net and returns all valid 1-step transformations 
    based on the 4 symmetry rules.
    """
    neighbors = []
    
    # RULE 1: Swap any two parallel classes 
    # (Doing this recursively in BFS generates all 120 permutations)
    for i, j in combinations(range(5), 2):
        temp = list(knet)
        temp[i], temp[j] = temp[j], temp[i]
        neighbors.append(tuple(temp))
        
    # RULE 2: Swap R1 <-> R2 (swaps n10 and n01)
    temp = []
    for tup in knet:
        t = list(tup)
        t[1], t[2] = t[2], t[1]
        temp.append(tuple(t))
    neighbors.append(tuple(temp))
    
    # RULE 3: Symm Diff (swaps n10 and n11)
    temp = []
    for tup in knet:
        t = list(tup)
        t[1], t[3] = t[3], t[1]
        temp.append(tuple(t))
    neighbors.append(tuple(temp))
    
    # RULE 4: Complement r1 on an even number (2) of parallel classes
    # (Complementing 2 at a time recursively generates all even combinations)
    for idx1, idx2 in combinations(range(5), 2):
        temp = list(knet)
        for idx in (idx1, idx2):
            t = list(temp[idx])
            t[0], t[1] = t[1], t[0]  # Swap n00 and n10
            t[2], t[3] = t[3], t[2]  # Swap n01 and n11
            temp[idx] = tuple(t)
        neighbors.append(tuple(temp))
        
    return neighbors

def construct_fingerprint(start_knet):
    """
    Explores all symmetries exhaustively using BFS to find the absolute
    lexicographically minimum fingerprint for this equivalence class.
    """
    visited = set([start_knet])
    queue = deque([start_knet])
    fingerprint = start_knet
    
    while queue:
        current = queue.popleft()
        
        for neighbor in get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                
                # Track the absolute minimum encountered
                if neighbor < fingerprint:
                    fingerprint = neighbor
                    
    # Return both the minimum fingerprint AND the whole orbit 
    # so we can skip checking these again later!
    return fingerprint, visited

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

    profiles = construct_profiles(PAIRS) 

    uq = set()
    global_seen = set() # Cache to remember every configuration we've already explored

    for i, candidate in enumerate(profiles):
        # Convert candidate to a tuple so it can be hashed and checked
        candidate_tuple = tuple(tuple(mk) for mk in candidate)
        
        # If this candidate was already found inside a previous orbit, skip it!
        if candidate_tuple in global_seen:
            continue

        # Unpack the fingerprint and the entire orbit from the BFS
        fingerprint, orbit = construct_fingerprint(candidate_tuple)
        
        uq.add(fingerprint)
        global_seen.update(orbit) # Add the whole orbit to our global cache
        
        # Print progress in a cleaner format
        print(f"Processed {i}/{len(profiles)} ... Found unique class {len(uq)}")
        print('class=',fingerprint)

    print("\n--- FINAL RESULTS ---")
    for val in uq:
        print(val, "\n \n")
    print("Unique canonical fingerprints:", len(uq))
    # print(uq) # Optional: print the actual set if you want to see all 111 shapes

if __name__ == '__main__':
    main()