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

def bwt(text, sa):
    """
    Input: text, a string ending with $; sa, its suffix array.
    Output: str, the BWT: the letter before each suffix, in row order, text[sa[row] - 1].
    Example: bwt("CAT$", [3, 1, 0, 2]) → "TC$A".
    """
    bwt = ""
    for i in sa:
        bwt += text[i-1]
    return bwt

def first_occurrence(letters):
    """
    Input: letters, a string (here, always a BWT).
    Output: dict[str, int], for each letter X of letters, the row where X starts in F = the number of letters in letters that are smaller than X.
    Example: first_occurrence("TC$A") → {"$": 0, "A": 1, "C": 2, "T": 3}.
    """ 
    first_oc = {}
    for i,l in enumerate(sorted(letters)):
        if l not in first_oc:
            first_oc[l]=i
    return first_oc

def inverse_bwt(bwt):
    """    
    Input: bwt, the BWT (L) of some text ending with $.
    Output: str, that text.
    """
    first = first_occurrence(bwt)

    counts = {}
    ranks = []
    for char in bwt:
        counts[char] = counts.get(char, 0) + 1
        ranks.append(counts[char])

    row = 0
    collected = []
    for _ in range(len(bwt) - 1):
        X = bwt[row]
        k = ranks[row]
        collected.append(X)
        row = first[X] + k - 1
        
    return "".join(reversed(collected)) + "$"
        



def task1():
    print(brute_force("AAAA", "AA"))
    print(suffix_array("ACGT$"))
    a,b = (find_block("ATGGTG",suffix_array("ATGGTG"),"TG"))
    print(sorted(suffix_array("ATGGTG")[a:b]))
    print(brute_force("ATGGTG","TG"))
    return

def task2():
    bt = bwt("CAT$", [3, 1, 0, 2])
    print(first_occurrence(bt))
    print(inverse_bwt(bt))


if __name__ == "__main__":
    # task1()
    task2()