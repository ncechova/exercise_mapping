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

def reverse_complement(dna_sequence):
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    reversed_sequence = dna_sequence[::-1]
    return ''.join(complement[base] for base in reversed_sequence)

def hamming(a, b):
    """
    Input: two strings of the same length.
    Output: int, the number of positions where they differ.
    Example: hamming("ACGT", "AGGA") → 2.
    """
    if len(a) != len(b):
        raise ValueError("Strings must be of the same length")
    return sum(1 for x, y in zip(a, b) if x != y)

def seeds(read,n):
    """
    Input: read, a string; n, the number of seeds.
    Output: list[tuple[int, str]], n consecutive, nearly equal pieces that cover the whole read, 
            each with its offset in the read: piece i starts at i * len(read) // n.
    """   
    pieces = []
    for i in range(n):
        start = i * len(read) // n
        end = (i + 1) * len(read) // n
        pieces.append((start, read[start:end]))
    return pieces

def map_read(read, fm, ref, d=2, n_seeds=None):
    """
    Input:  read; fm, an FMIndex of ref + "$"; ref, the reference string; d, the maximum number 
            of mismatches; n_seeds, the number of seeds (None means d + 1).
    Output: tuple[list[tuple[str, int, int]], int]: the sorted list of hits (strand, position, mismatches), 
            strand "+" for the read and "-" for its reverse complement, position 0-based in ref (for "-": the 
            leftmost position where the reverse complement matches); and the number of candidates: the distinct 
            starts inside the reference that you verified with hamming, summed over both strands.
    """
    if n_seeds is None:
        n_seeds = d + 1
    hits = []
    n_candidates = 0
    for strand, seq in (("+", read), ("-", reverse_complement(read))):
        candidates = set()
        for offset, seed in seeds(seq, n_seeds):
            for p in fm.locate(seed):
                start = p - offset
                if 0 <= start <= len(ref) - len(seq):   # the read must not stick out of the reference
                    candidates.add(start)
        n_candidates += len(candidates)
        for start in candidates:
            mismatches = hamming(seq, ref[start:start + len(seq)])
            if mismatches <= d:
                hits.append((strand, start, mismatches))
    return sorted(hits), n_candidates

def brute_map(read, ref, d=2):
    """
    Input: read, ref and d as in map_read (no index).
    Output: the sorted list of hits, as in map_read, found the slow way: try every start on both strands.
    """
    hits = []
    for strand, seq in (("+", read), ("-", reverse_complement(read))):
        for start in range(len(ref) - len(seq) + 1):
            mismatches = hamming(seq, ref[start:start + len(seq)])
            if mismatches <= d:
                hits.append((strand, start, mismatches))
    return sorted(hits)


def task1():
    print("--- TASK 1 ---")
    print(brute_force("AAAA", "AA"))
    print(suffix_array("ACGT$"))
    a,b = (find_block("ATGGTG",suffix_array("ATGGTG"),"TG"))
    print(sorted(suffix_array("ATGGTG")[a:b]))
    print(brute_force("ATGGTG","TG"))
    return

def task2():
    print("--- TASK 2 ---")
    bt = bwt("CAT$", [3, 1, 0, 2])
    print(first_occurrence(bt))
    print(inverse_bwt(bt))

def task3():
    print("--- TASK 3 ---")
    fm = FMIndex("CAT$", 2)
    print(fm.count("AT"))
    print(fm.locate("AT"))

def task4():
    print("--- TASK 4 ---")
    print(reverse_complement("AACG"))
    print(hamming("ACGT", "AGGA"))
    print(seeds("ACGTACGTAC", 3))
    fm = FMIndex("ACGTACGT$", 2)
    print(map_read("ACGTA", fm, "ACGTACGT"))
    print(brute_map("ACGTA", "ACGTACGT"))

if __name__ == "__main__":
    task1()
    task2()
    task3()
    task4()