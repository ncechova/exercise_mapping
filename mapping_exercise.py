def brute_force(text,p):
    """
    Input: text, p, strings.
    Output: list[int], every start position of p in text, in increasing order, overlapping occurrences included.
    Example: brute_force("AAAA", "AA") → [0, 1, 2].
    """
    return [i for i in range(len(text)-len(p)+1) if text[i:i+len(p)] == p]

def suffix_array(text):
    """
    Input: text, a string ending with $.
    Output: list[int], the start positions of the suffixes of text in alphabetical order of the suffixes.
    """
    return sorted(range(len(text)), key=lambda i: text[i:])

def find_block(text, sa, p):
    """
    Input: text; sa, its suffix array; p, a non-empty pattern.
    Output: tuple[int, int], the half-open interval (a, b) of rows whose suffixes start with p. If p does not occur, a == b (an empty block at the row where p would be).
    """
    m = len(p)
    lo, hi = 0, len(sa)
    while lo < hi:
        mid = (lo + hi) // 2
        if text[sa[mid] : sa[mid] + m] < p:
            lo = mid + 1
        else:
            hi = mid
    a = lo
    lo, hi = a, len(sa) 
    while lo < hi:
        mid = (lo + hi) // 2
        if text[sa[mid] : sa[mid] + m] <= p:
            lo = mid + 1
        else:
            hi = mid
    b = lo

    return (a, b)



if __name__ == "__main__":
    print(brute_force("AAAA", "AA"))
    print(suffix_array("ACGT$"))
    a,b = (find_block("ATGGTG",suffix_array("ATGGTG"),"TG"))
    print(sorted(suffix_array("ATGGTG")[a:b]))
    print(brute_force("ATGGTG","TG"))
