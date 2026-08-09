from collections import deque 
from itertools import permutations, product, combinations 

# --- 1. WHITELIST GENERATION ---
def get_orbit(base):
    orbit = set()
    n = len(base)
    # 0 complements
    orbit.add(tuple(sorted(base)))
    
    # 2 complements
    for i in range(n):
        for j in range(i+1, n):
            tmp = list(base)
            tmp[i] = 10 - tmp[i]
            tmp[j] = 10 - tmp[j]
            orbit.add(tuple(sorted(tmp)))
            
    # 4 complements
    for i in range(n):
        tmp = [10 - x for x in base]
        tmp[i] = 10 - tmp[i] 
        orbit.add(tuple(sorted(tmp)))
        
    return orbit

WHITELIST = get_orbit((2,2,4,4,4)) | get_orbit((2,4,4,4,6)) | get_orbit((4,4,4,4,4))


# --- 2. BFS ORBIT EXPLORATION ---
SEEN_STATES = set()

def explore_orbit(start_state):
    canonical_start = tuple(sorted(start_state))
    if canonical_start in SEEN_STATES:
        return None
        
    orbit_seen = {canonical_start}
    queue = deque([canonical_start])
    
    canonical_min = canonical_start
    is_orbit_valid = True
    
    while queue:
        state = queue.popleft()
        
        # Check Whitelist
        w1 = tuple(sorted(b[1] + b[3] for b in state))
        w2 = tuple(sorted(b[2] + b[3] for b in state))
        
        if w1 not in WHITELIST or w2 not in WHITELIST:
            is_orbit_valid = False
            # CRITICAL FIX: DO NOT BREAK OR PRUNE HERE!
            # The entire orbit must be generated and added to SEEN_STATES
            # otherwise the orbit fractures, causing duplicate false-positives later.
        
        neighbors = []
        
        # Action 2: Exchange relation 1 and relation 2
        neighbors.append(tuple((b[0], b[2], b[1], b[3]) for b in state))
        
        # Action 3: Replace R2 by symmetric difference (R1 ^ R2)
        neighbors.append(tuple((b[0], b[3], b[2], b[1]) for b in state))
        
        # Action 4: Complement R1 on an even number of parallel classes
        for i, j in combinations(range(5), 2):
            nxt = list(state)
            nxt[i] = (nxt[i][1], nxt[i][0], nxt[i][3], nxt[i][2])
            nxt[j] = (nxt[j][1], nxt[j][0], nxt[j][3], nxt[j][2])
            neighbors.append(tuple(nxt))
            
        for nxt in neighbors:
            # S5 Permutation Action is perfectly quotiented out by sorting the classes
            can_nxt = tuple(sorted(nxt))
            if can_nxt not in orbit_seen:
                orbit_seen.add(can_nxt)
                queue.append(can_nxt)
                if can_nxt < canonical_min:
                    canonical_min = can_nxt
                    
    # Update global tracking ONLY once the entire orbit is constructed
    SEEN_STATES.update(orbit_seen)
    
    return canonical_min if is_orbit_valid else None


# --- 3. RAW PAIR GENERATION ---
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
    
    canonical_minimums = set()
    total_raw = 0
    
    for relo1, relo2 in pairs:
        for perm_relo2 in set(permutations(relo2)):
            M = [construct_intersections(w1, w2) for w1, w2 in zip(relo1, perm_relo2)]
            
            for val in product(*M):
                total_raw += 1
                
                # CRITICAL FIX: Keep as a tuple of tuples. Do not flatten!
                pv = tuple(tuple(group) for group in val)
                
                if tuple(sorted(pv)) not in SEEN_STATES:
                    result = explore_orbit(pv)
                    if result is not None:
                        canonical_minimums.add(result)
                        
    print(f"Total raw combinations generated: {total_raw}")
    print(f"Total explored internal states: {len(SEEN_STATES)}")
    print(f"Valid Canonical Minimums: {len(canonical_minimums)}\n")
    
    for item in sorted(canonical_minimums):
        print(item)

if __name__ == "__main__":
    main()