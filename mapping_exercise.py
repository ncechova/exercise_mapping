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


class FMIndex:
    """
    Input: text, a string ending with $; s, a positive int (the sampling step).
    Stores:
    self.bwt: the BWT of text;
    self.first_occurrence: first_occurrence(self.bwt);
    self.counts: dict[str, list[int]], for every letter X a list of length len(text) + 1 with counts[X][i] = the number of X in self.bwt[:i];
    self.sampled: dict[int, int], part of the suffix array: row → sa[row], kept only where sa[row] is a multiple of s;
    self.s: s.   
    """
    def __init__(self, text, s):
        sa = suffix_array(text)
        self.s = s
        self.bwt = bwt(text, sa)
        self.first_occurrence = first_occurrence(self.bwt)
        self.counts = {x: [0] * (len(text) + 1) for x in set(text)}
        for i, letter in enumerate(self.bwt):
            for x in self.counts:
                self.counts[x][i + 1] = self.counts[x][i]
            self.counts[letter][i + 1] += 1
        self.sampled = {row: sa[row] for row in range(len(sa)) if sa[row] % s == 0}

    def lf(self, row):
        """
        Input: row, an int with 0 ≤ row < len(self.bwt).
        Output: int, the row of the suffix that starts one position earlier in the text: first_occurrence[X] + counts[X][row] with X = self.bwt[row].
        Example: for FMIndex("CAT$", 2), lf(1) → 2 (row 1 is AT$, row 2 is CAT$).
        """
        x = self.bwt[row]
        return self.first_occurrence[x] + self.counts[x][row]

    def count(self, p):
        """
        Input: p, a non-empty string.
        Output: tuple[int, int], the interval (top, bottom) of rows that start with p, found by backward search: start with (0, len(self.bwt)), then for each letter X of p from the last one: top = first_occurrence[X] + counts[X][top], and the same for bottom.
        Example: for FMIndex("CAT$", 2), count("AT") → (1, 2).
        """
        top, bottom = 0, len(self.bwt)
        for x in reversed(p):
            if x not in self.counts:
                return (0, 0)
            top = self.first_occurrence[x] + self.counts[x][top]
            bottom = self.first_occurrence[x] + self.counts[x][bottom]
            if top == bottom:
                return (top, bottom)
        return (top, bottom)

    def locate(self, p):
        """
        Input: p, a non-empty string.
        Output: list[int], the text positions of all occurrences of p (one per row of count(p), in row order).
        Example: for FMIndex("CAT$", 2), locate("AT") → [1] (row 1 → row 2, stored 0, one step).
        """
        top, bottom = self.count(p)
        positions = []
        for row in range(top, bottom):
            steps = 0
            while row not in self.sampled:
                row = self.lf(row)
                steps += 1
            positions.append(self.sampled[row] + steps)
        return positions



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

def task3():
    fm = FMIndex("CAT$", 2)
    print(fm.count("AT"))
    print(fm.locate("AT"))

if __name__ == "__main__":
    task1()
    task2()
    task3()