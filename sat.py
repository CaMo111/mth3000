import itertools
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType

class DualRelation5NetSATSolver:
    def __init__(self, n=10):
        self.n = n
        self.num_squares = 3  # 5-net corresponds to 3 MOLS (Rows, Cols + 3 Latin Squares)
        self.var_map = {}
        self.reverse_map = {}
        self.next_var = 1
        self.solver = Solver(name='cadical195')

    def get_var(self, s, r, c, v):
        """Maps (square s, row r, col c, value v) to a unique SAT variable."""
        key = (s, r, c, v)
        if key not in self.var_map:
            self.var_map[key] = self.next_var
            self.reverse_map[self.next_var] = key
            self.next_var += 1
        return self.var_map[key]

    def new_aux_var(self):
        """Allocates an auxiliary variable for CNF conversion."""
        v = self.next_var
        self.next_var += 1
        return v

    def encode_5net_base(self):
        """Encodes 3 MOLS of order 10 (Cell, Row, Col uniqueness + Pairwise Orthogonality)."""
        # 1. Cell, Row, and Column constraints for each of the 3 Latin Squares
        for s in range(self.num_squares):
            for r in range(self.n):
                for c in range(self.n):
                    # Each cell gets exactly 1 symbol
                    lits = [self.get_var(s, r, c, v) for v in range(self.n)]
                    cnf = CardEnc.equals(lits=lits, bound=1, top_id=self.next_var - 1, encoding=EncType.seqcounter)
                    self.next_var = cnf.top_id + 1
                    for cl in cnf.clauses: self.solver.add_clause(cl)

            for r in range(self.n):
                for v in range(self.n):
                    # Each row gets symbol v exactly once
                    lits = [self.get_var(s, r, c, v) for c in range(self.n)]
                    cnf = CardEnc.equals(lits=lits, bound=1, top_id=self.next_var - 1, encoding=EncType.seqcounter)
                    self.next_var = cnf.top_id + 1
                    for cl in cnf.clauses: self.solver.add_clause(cl)

            for c in range(self.n):
                for v in range(self.n):
                    # Each column gets symbol v exactly once
                    lits = [self.get_var(s, r, c, v) for r in range(self.n)]
                    cnf = CardEnc.equals(lits=lits, bound=1, top_id=self.next_var - 1, encoding=EncType.seqcounter)
                    self.next_var = cnf.top_id + 1
                    for cl in cnf.clauses: self.solver.add_clause(cl)

        # 2. Pairwise Orthogonality between all pairs of Latin Squares (LS1-LS2, LS1-LS3, LS2-LS3)
        for s1, s2 in itertools.combinations(range(self.num_squares), 2):
            for v1 in range(self.n):
                for v2 in range(self.n):
                    pair_lits = []
                    for r in range(self.n):
                        for c in range(self.n):
                            x1 = self.get_var(s1, r, c, v1)
                            x2 = self.get_var(s2, r, c, v2)
                            y = self.new_aux_var()
                            pair_lits.append(y)
                            self.solver.add_clause([-y, x1])
                            self.solver.add_clause([-y, x2])
                            self.solver.add_clause([-x1, -x2, y])

                    # Every ordered pair (v1, v2) appears in exactly 1 cell
                    cnf = CardEnc.equals(lits=pair_lits, bound=1, top_id=self.next_var - 1, encoding=EncType.seqcounter)
                    self.next_var = cnf.top_id + 1
                    for cl in cnf.clauses: self.solver.add_clause(cl)

    def add_dual_relation_constraints(self, rel1_lines, rel2_lines):
        """
        Enforces that every point (cell r,c) is incident to an EVEN number of lines 
        in Relation 1 AND an EVEN number of lines in Relation 2.
        
        rel1_lines and rel2_lines are dicts specifying active relational line indices:
        { 'rows': set(), 'cols': set(), 'sq0': set(), 'sq1': set(), 'sq2': set() }
        """
        for rel_index, rel_lines in enumerate([rel1_lines, rel2_lines]):
            for r in range(self.n):
                for c in range(self.n):
                    # Static contribution from Row and Column parallel classes
                    fixed_count = (1 if r in rel_lines['rows'] else 0) + (1 if c in rel_lines['cols'] else 0)
                    
                    # Dynamic literals from the 3 Latin Squares
                    active_lits = []
                    for s in range(3):
                        sq_key = f'sq{s}'
                        for v in rel_lines[sq_key]:
                            active_lits.append(self.get_var(s, r, c, v))
                    
                    # Enforce sum(active_lits) + fixed_count = 0 (mod 2)
                    self._add_parity_clause(active_lits, target_parity=(fixed_count % 2))

    def _add_parity_clause(self, lits, target_parity):
        """Encodes that an even (or odd) number of literals in 'lits' are true."""
        # Simple parity chain using auxiliary XOR variables
        if not lits:
            return
        
        # Enforce parity sum over active literals
        # (For small length lists of active literals per cell, generate CNF parity directly)
        for p in itertools.product([False, True], repeat=len(lits)):
            # If assignment parity doesn't match target_parity, block it
            if (sum(p) % 2) != target_parity:
                clause = [-lits[i] if p[i] else lits[i] for i in range(len(lits))]
                self.solver.add_clause(clause)

    def add_symmetry_breaking(self):
        """Fixes standard form for Square 0 to prune redundant isomorphic branches."""
        for c in range(self.n):
            self.solver.add_clause([self.get_var(0, 0, c, c)])
        for r in range(1, self.n):
            self.solver.add_clause([self.get_var(0, r, 0, r)])

    def solve_overlap_case(self, rel1_spec, rel2_spec):
        print("Encoding 5-Net base constraints...")
        self.encode_5net_base()
        self.add_symmetry_breaking()
        
        print("Adding Dual Relation parity constraints...")
        self.add_dual_relation_constraints(rel1_spec, rel2_spec)
        
        print("Running CaDiCaL SAT Solver...")
        if self.solver.solve():
            print("\n>>> SOLUTION FOUND! 5-net satisfies both relations. <<<")
            model = set(self.solver.get_model())
            # Output MOLS squares
            for s in range(3):
                print(f"\n--- Latin Square {s + 1} ---")
                for r in range(self.n):
                    row_vals = [v for c in range(self.n) for v in range(self.n) if self.get_var(s, r, c, v) in model]
                    print(" ".join(f"{x:2d}" for x in row_vals))
            return True
        else:
            print("\n>>> UNSATISFIABLE: No 5-net exists for this overlap template. <<<")
            return False

# Example: Running Case with Relation A (2^2 4^3) and Relation C (4^5)
if __name__ == "__main__":
    solver = DualRelation5NetSATSolver(n=10)
    
    # Define active relational lines for Relation 1 (Type 2^2 4^3)
    # Weights per class: Rows=2, Cols=2, SQ0=4, SQ1=4, SQ2=4
    rel1 = {
        'rows': {0, 1},
        'cols': {0, 1},
        'sq0': {0, 1, 2, 3},
        'sq1': {0, 1, 2, 3},
        'sq2': {0, 1, 2, 3}
    }

    # Define active relational lines for Relation 2 (Type 4^5)
    # Weights per class: Rows=4, Cols=4, SQ0=4, SQ1=4, SQ2=4
    rel2 = {
        'rows': {0, 1, 2, 3},
        'cols': {0, 1, 2, 3},
        'sq0': {2, 3, 4, 5},
        'sq1': {2, 3, 4, 5},
        'sq2': {2, 3, 4, 5}
    }

    solver.solve_overlap_case(rel1, rel2)