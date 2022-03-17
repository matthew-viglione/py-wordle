from sklearn.metrics import r2_score
from soupsieve import match


def get_words(filename):
    """Return a list of all the words in the file."""
    result = []
    with open(filename) as file:
        for line in file:
            result.append(line.rstrip())
    return result


def flatten(t):
    flat = [item for sublist in t for item in sublist]
    return list(set(flat))


def flatten2(t):
    flat = [item for sublist in t for item in sublist]
    return list(set(flat))


def summarize(list2d):
    for r in list2d:
        print(r)
    l = flatten(list2d)
    print(f" {len(l)} possibilities")
    return list(l)


def summarize2(list2d):
    for r in list2d:
        print(r)
    l = flatten2(list2d)
    print(f" {len(l)} possibilities")
    return list(l)


def final_info(*args):
    res = set(args[0])
    if len(args) > 1:
        for s in args[1:]:
            res &= set(s)

    res = list(res)
    print("\n\nFinal info")
    print(res)
    print(f" {len(res)} possibilities")
    return res


pattern = [[0, 2, 2, 2, 2], [0, 2, 2, 2, 2]]


print("\n\nPass 1 info")
# at least 5 - 0 2 2 2 2 matches
words = get_words("wordlist_solutions.txt")
matches = []
target = 5
for w in words:
    these_matches = []
    for w2 in words:
        if w[1:] == w2[1:]:
            if w2 not in these_matches:
                these_matches.append(w2)
                # words.remove(w2)
    # if len(these_matches) >= target:
    if len(these_matches) >= target and these_matches not in matches:
        matches.append(these_matches)

r1 = summarize2(matches)

print("\n\nPass 2 info")
# at least 2 - 1 2 0 2 2 matches
words = get_words("wordlist_solutions.txt")
matches = []
target = 2
for w in words:
    these_matches = []
    # print(f"Matching {w}")
    for w2 in words:
        if (
            w[0] == w2[2]
            and w[1] == w2[1]
            # and w[2] != w2[2]
            and w[3] == w2[3]
            and w[4] == w2[4]
        ):
            if w2 not in these_matches:
                these_matches.append(w2)
                # words.remove(w2)
    # print(f"Found {len(these_matches)} matches")
    # print(these_matches)
    if len(these_matches) >= target:
        matches.append(these_matches)
r2 = summarize(matches)

print("\n\nPass 3 info")
# at least 2 - 2 2 0 2 2 matches
words = get_words("wordlist_solutions.txt")
matches = []
target = 2
for w in words:
    these_matches = []
    # print(f"Matching {w}")
    for w2 in words:
        if (
            w[0] == w2[0]
            and w[1] == w2[1]
            # and w[2] != w2[2]
            and w[3] == w2[3]
            and w[4] == w2[4]
        ):
            if w2 not in these_matches:
                these_matches.append(w2)
                # words.remove(w2)
    # print(f"Found {len(these_matches)} matches")
    # print(these_matches)
    if len(these_matches) >= target:
        matches.append(these_matches)
r3 = summarize(matches)

print("\n\nPass 4 info")
# at least 2 - 2 2 1 2 0 matches
words = get_words("wordlist_solutions.txt")
matches = []
target = 2
for w in words:
    these_matches = []
    # print(f"Matching {w}")
    for w2 in words:
        if (
            w[0] == w2[0]
            and w[1] == w2[1]
            # and w[2] == w2[4]
            and w[3] == w2[3]
            # and w[4] == w2[4]
        ):
            if w2 not in these_matches:
                these_matches.append(w2)
                # words.remove(w2)
    # print(f"Found {len(these_matches)} matches")
    # print(these_matches)
    if len(these_matches) >= target:
        matches.append(these_matches)
r4 = summarize(matches)

# r2 = ["cater", "cyber", "caper", "cider", "crier", "cheer"]

# if implied correct, w is the solution and w2 is possible

# test = final_info(r1, r2)
test = final_info(r1, r2, r3, r4)
# test = final_info(r2, r3, r4)
# test = final_info(r1, r3, r4)
# test = final_info(r1, r2, r4)
# test = final_info(r1, r2, r3)
