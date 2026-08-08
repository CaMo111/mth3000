from collections import deque
from itertools import permutations, product, combinations

# Global tracking to prevent redundant BFS explorations
SEEN_STATES = set()

# 1. GENERATE THE WHITELIST
def get_orbit(base):
    """Generates all valid profiles under even complementations."""
    orbit = set()
    # 0 complements
    orbit.add(tuple(sorted(base)))
    
    # 2 complements
    for i in range(5):
        for j in range(i+1, 5):
            tmp = list(base)
            tmp[i] = 10 - tmp[i]
            tmp[j] = 10 - tmp[j]
            orbit.add(tuple(sorted(tmp)))
            
    # 4 complements
    for i in range(5):
        tmp = [10 - x for x in base]
        tmp[i] = 10 - tmp[i]  # Revert one to get exactly 4 complements
        orbit.add(tuple(sorted(tmp)))
        
    return orbit

# The exact 15 valid profiles allowed by the theorems
WHITELIST = get_orbit((2,2,4,4,4)) | get_orbit((2,4,4,4,6)) | get_orbit((4,4,4,4,4))
print(WHITELIST)

class Relation:
    def __init__(self):
        self.A = (2, 2, 4, 4, 4)
        self.B = (2, 4, 4, 4, 6)
        self.C = (4, 4, 4, 4, 4)

def construct_intersections(w1, w2):
    A_min = max(0, w1 + w2 - 10)
    A_max = min(w1, w2)
    return [
        (10 - (w1 + w2 - A), w1 - A, w2 - A, A)
        for A in range(A_min, A_max + 1)
    ]

def get_relation_weights(state):
    w1 = tuple(sorted(b[1] + b[3] for b in state))
    w2 = tuple(sorted(b[2] + b[3] for b in state))
    return w1, w2

def explore_orbit(start_state):
    start_state = tuple(sorted(start_state))
    
    if start_state in SEEN_STATES:
        return None
        
    orbit = {start_state}
    queue = deque([start_state])
    
    orbit_min = start_state
    is_valid = True
    
    while queue:
        state = queue.popleft()
        
        # 2. ENFORCE THE WHITELIST
        # Because Action 3 replaces R2 with R1 XOR R2, this check guarantees 
        # that R1, R2, AND their symmetric difference are all valid types.
        if is_valid:
            w1, w2 = get_relation_weights(state)
            if w1 not in WHITELIST or w2 not in WHITELIST:
                is_valid = False 
        
        neighbors = []
        
        # Action 2: Exchange relation 1 and relation 2
        n2 = tuple(sorted((b[0], b[2], b[1], b[3]) for b in state))
        neighbors.append(n2)
        
        # Action 3: Replace r2 by symmetric difference of r1 and r2 
        n3 = tuple(sorted((b[0], b[3], b[2], b[1]) for b in state))
        neighbors.append(n3)
        
        # Action 4: Complement r1 on an even number of parallel classes
        for i, j in combinations(range(5), 2):
            new_state = list(state)
            new_state[i] = (new_state[i][1], new_state[i][0], new_state[i][3], new_state[i][2])
            new_state[j] = (new_state[j][1], new_state[j][0], new_state[j][3], new_state[j][2])
            neighbors.append(tuple(sorted(new_state)))
            
        for nxt in neighbors:
            if nxt not in orbit:
                orbit.add(nxt)
                queue.append(nxt)
                if nxt < orbit_min:
                    orbit_min = nxt
                    
    SEEN_STATES.update(orbit)
    return orbit_min if is_valid else None

def main():
    relations = Relation()
    pairs = [
        (relations.A, relations.A),
        (relations.A, relations.B),
        (relations.A, relations.C),
        (relations.B, relations.B),
        (relations.B, relations.C),
        (relations.C, relations.C),
    ]
    
    canonical_orbits = set()
    total_raw = 0
    
    for relo1, relo2 in pairs:
        for value in set(permutations(relo2)):
            M = [construct_intersections(w1, w2) for w1, w2 in zip(relo1, value)]
            
            for val in product(*M):
                total_raw += 1
                if tuple(sorted(val)) not in SEEN_STATES:
                    canonical_min = explore_orbit(val)
                    if canonical_min is not None:
                        canonical_orbits.add(canonical_min)
                        


    # print(canonical_orbits)
    for item in canonical_orbits:
        print(item, '\n')

    print(f"Total raw pairs generated: {total_raw}")
    print(f"Total internal configurations explored: {len(SEEN_STATES)}")
    print(f"Valid Canonical Minimums (After group closure & filtering): {len(canonical_orbits)}\n")

if __name__ == "__main__":
    main()