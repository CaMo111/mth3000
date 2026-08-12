def is_valid_chunk(chunk):
    n00, n10, n01, n11 = chunk
    w1 = n10 + n11
    w2 = n01 + n11
    return w1 > 0 and w2 > 0   # neither relation is empty in this class

def is_valid(pv):
    chunks = [pv[i:i+4] for i in range(0, 20, 4)]
    return all(is_valid_chunk(c) for c in chunks)

if __name__ == '__main__':
    print(is_valid((4, 0, 6, 0, 5, 1, 3, 1, 6, 2, 0, 2, 4, 2, 2, 2, 5, 1, 1, 3)))