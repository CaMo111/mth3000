import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from collections import deque
from itertools import permutations, product, combinations

# ==========================================
# 1. GENERATE THE WHITELIST
# ==========================================
def get_orbit(base):
    """Generates all valid weight profiles under even complementations."""
    orbit = set()
    orbit.add(tuple(sorted(base)))
    
    for i in range(5):
        for j in range(i+1, 5):
            tmp = list(base)
            tmp[i] = 10 - tmp[i]
            tmp[j] = 10 - tmp[j]
            orbit.add(tuple(sorted(tmp)))
            
    for i in range(5):
        tmp = [10 - x for x in base]
        tmp[i] = 10 - tmp[i]
        orbit.add(tuple(sorted(tmp)))
        
    return orbit

WHITELIST = get_orbit((2,2,4,4,4)) | get_orbit((2,4,4,4,6)) | get_orbit((4,4,4,4,4))

# ==========================================
# 2. GENERATE POINT-TYPE EQUATIONS
# ==========================================
# 0:(0,0), 1:(1,0), 2:(0,1), 3:(1,1)
STATES_BITS = [(0,0), (1,0), (0,1), (1,1)]

# Generate the 256 valid point types (even number of incidences for both relations)
VALID_POINT_TYPES = []
for t in product(range(4), repeat=5):
    sum_r1 = sum(STATES_BITS[idx][0] for idx in t)
    sum_r2 = sum(STATES_BITS[idx][1] for idx in t)
    if sum_r1 % 2 == 0 and sum_r2 % 2 == 0:
        VALID_POINT_TYPES.append(t)

def has_integer_solution(overlap_state):
    """
    Sets up the point-type integer linear program for a given overlap.
    Returns True if a valid integer distribution of point types exists.
    """
    A = []
    b = []
    
    # For every pair of parallel classes (i, j)
    for i in range(5):
        for j in range(i+1, 5):
            # For every pair of line types in those classes
            for c_i in range(4):
                for c_j in range(4):
                    # Count how many of each point type fall into this intersection
                    row = [1 if t[i] == c_i and t[j] == c_j else 0 for t in VALID_POINT_TYPES]
                    A.append(row)
                    
                    # The number of intersection points MUST equal the product of the line counts
                    rhs = overlap_state[i][c_i] * overlap_state[j][c_j]
                    b.append(rhs)
                    
    A = np.array(A)
    b = np.array(b)
    
    # We want A * x = b, where x >= 0 and x is strictly integer
    constraints = LinearConstraint(A, b, b)
    bounds = Bounds(0, np.inf)
    integrality = np.ones(len(VALID_POINT_TYPES)) # All 256 variables must be integers
    c = np.zeros(len(VALID_POINT_TYPES))          # Objective is irrelevant, we only seek feasibility
    
    res = milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds)
    
    # 0 = optimal solution found (feasible)
    return res.success

# ==========================================
# 3. OVERLAP GENERATION & BFS FILTERING
# ==========================================
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

def get_all_subspace_weights(state):
    w1 = tuple(sorted(b[1] + b[3] for b in state))
    w2 = tuple(sorted(b[2] + b[3] for b in state))
    w_xor = tuple(sorted(b[1] + b[2] for b in state))
    return w1, w2, w_xor

SEEN_STATES = set()

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
        
        if is_valid:
            w1, w2, w_xor = get_all_subspace_weights(state)
            if w1 not in WHITELIST or w2 not in WHITELIST or w_xor not in WHITELIST:
                is_valid = False
        
        neighbors = []
        neighbors.append(tuple(sorted((b[0], b[2], b[1], b[3]) for b in state)))
        neighbors.append(tuple(sorted((b[0], b[3], b[2], b[1]) for b in state)))
        
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
        (relations.A, relations.A), (relations.A, relations.B),
        (relations.A, relations.C), (relations.B, relations.B),
        (relations.B, relations.C), (relations.C, relations.C),
    ]
    
    canonical_orbits = set()
    
    # Step 1: Find the 120 macroscopic overlaps
    for relo1, relo2 in pairs:
        for value in set(permutations(relo2)):
            M = [construct_intersections(w1, w2) for w1, w2 in zip(relo1, value)]
            for val in product(*M):
                if tuple(sorted(val)) not in SEEN_STATES:
                    canonical_min = explore_orbit(val)
                    if canonical_min is not None:
                        canonical_orbits.add(canonical_min)
                        
    print(f"Total raw overlaps found: {len(canonical_orbits)}")
    
    # Step 2: Solve the point-type equations for each overlap
    print("\nSolving point-type integer equations...")
    surviving_cases = []
    
    for i, state in enumerate(sorted(canonical_orbits), 1):
        if has_integer_solution(state):
            surviving_cases.append(state)
            
    print(f"Surviving cases after ILP filtering: {len(surviving_cases)}\n")
    
    for idx, case in enumerate(surviving_cases, 1):
        print(f"Surviving Case {idx}: {case}")

if __name__ == "__main__":
    main()