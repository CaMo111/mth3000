# SageMath built-in for vector bounds
# from sage.combinat.integer_vector import IntegerVectors

# Example: w1 = 4, w2 = 6, total_lines = 10
w1 = 4
w2 = 6
# We want vectors [A, B, C, D] summing to 10 where (A+B)=4 and (A+C)=6

# Instead of raw bounds, Sage lets you generate constraints directly:
# A ranges from max(0, w1 + w2 - 10) to min(w1, w2)
A_min = max(0, w1 + w2 - 10)
A_max = min(w1, w2)


valid_tuples_class = [
    (10 - (w1 + w2 - A), w1 - A, w2 - A, A)
    for A in range(A_min, A_max + 1)
]

print(valid_tuples_class)