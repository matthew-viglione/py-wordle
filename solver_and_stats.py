"""Do some fun analytics on the wordle word sets"""

import string
import matplotlib.pyplot as plt

from colorama import init

init()


class Colors:
    """Colors class:reset all colors with colors.reset; two
    sub classes fg for foreground
    and bg for background; use as colors.subclass.colorname.
    i.e. colors.fg.red or colors.bg.greenalso, the generic bold, disable,
    underline, reverse, strike through,
    and invisible work with the main class i.e. colors.bold"""

    reset = "\033[0m"
    bold = "\033[01m"
    disable = "\033[02m"
    underline = "\033[04m"
    reverse = "\033[07m"
    strikethrough = "\033[09m"
    invisible = "\033[08m"

    class fg:
        """Valid foreround colors."""

        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        ORANGE = "\033[33m"
        BLUE = "\033[34m"
        PURPLE = "\033[35m"
        CYAN = "\033[36m"
        LIGHTGREY = "\033[37m"
        DARKGREY = "\033[90m"
        LIGHTRED = "\033[91m"
        LIGHTGREEN = "\033[92m"
        YELLOW = "\033[93m"
        LIGHTBLUE = "\033[94m"
        PINK = "\033[95m"
        LIGHTCYAN = "\033[96m"

        @classmethod
        def all(cls):
            """Return a list containing all color name and color code pairs."""
            return [(name, value) for name, value in vars(cls).items() if name.isupper()]

        def color_test(self):
            """Print all colors to terminal.

            e.g.: Colors.fg().color_test()
            """
            for c, v in self.all():
                print(f"{v}{c}\033[0m")

    class bg:
        """Valid background colors."""

        BLACK = "\033[40m"
        RED = "\033[41m"
        GREEN = "\033[42m"
        ORANGE = "\033[43m"
        BLUE = "\033[44m"
        PURPLE = "\033[45m"
        CYAN = "\033[46m"
        LIGHTGREY = "\033[47m"

        @classmethod
        def all(cls):
            """Return a list containing all color name and color code pairs."""
            return [(name, value) for name, value in vars(cls).items() if name.isupper()]

        def color_test(self):
            """Print all colors to terminal.

            e.g.: Colors.bg().color_test()
            """
            for c, v in self.all():
                print(f"{v}{c}\033[0m")


valid_guesses = "wordlist_guesses.txt"
valid_solutions = "wordlist_solutions.txt"
file_list = [valid_guesses, valid_solutions]


def get_size_of_wordlist(filename):
    """Reuturn the number of lines in the file."""
    return sum(1 for _ in open(filename))


def get_letter_counts(filename):
    """Return a dictionary with letter -> count pairs from a wordlist."""
    counts = dict.fromkeys(string.ascii_lowercase, 0)
    with open(filename) as file:
        for line in file:
            for char in line.rstrip():
                counts[char] += 1
    return counts


def get_letter_counts_by_position(filename):
    """Return a dictionary with letter -> count pairs from a wordlist."""
    counts = []
    for i in range(0, 5):
        counts.append(dict.fromkeys(string.ascii_lowercase, 0))
    with open(filename) as file:
        for line in file:
            for i, char in enumerate(line.rstrip()):
                counts[i][char] += 1
    return counts


def generate_bar_graph(d, data_name=""):
    """Plot a bar graph from a dict with keys on X axis and values on Y axis."""
    plt.title(f"Letter frequency for '{data_name}'")
    plt.xlabel("Letter")
    plt.ylabel("Frequency (Percent and count)")
    plt.ylim([0, max(d.values()) * 1.3])
    plt.bar(range(len(d)), list(d.values()), align="center")
    plt.xticks(range(len(d)), list(d.keys()))

    for i, v in enumerate(d.values()):
        percent = str(round(v / sum(d.values()) * 100, 2))
        label = " " + percent + "% (" + str(v) + ")"
        plt.text(i + 0.075, v + 10, label, ha="center", size="x-small", rotation=90)
    fig_name = data_name.replace(" ", "_").lower() + ".png"
    # plt.savefig(fig_name)
    # plt.cla()
    plt.show()


def generate_bar_graph_by_position(filename):
    count_list = get_letter_counts_by_position(filename)
    for i, counts in enumerate(count_list):
        generate_bar_graph(counts, f"position {i+1} in {filename}")


def get_min_key(d):
    """Return the key from the dict with the min value."""
    return min(d, key=d.get)


def get_max_key(d):
    """Return the key from the dict with the max value."""
    return max(d, key=d.get)


def sort_dict(d, reverse=True):
    """Return the dictionary sorted by value."""
    return {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=reverse)}


def normalize_dict(d):
    """Turn the dictionary values into percentages"""
    total = sum(d.values())
    for k in d:
        d[k] = d[k] / total
    return d


def get_repeated_letter_words(filename, num_repeats=1):
    """Return list of words with repeated letters from supplied list file."""
    word_list = []
    with open(filename) as file:
        for word in file:
            counts = dict.fromkeys(string.ascii_lowercase, 0)
            word = word.rstrip()
            for char in word:
                counts[char] += 1

            for v in counts.values():
                if v > num_repeats:
                    word_list.append(word)
                    break
    return word_list


def report_words_with_repeat_letters(filenames):
    """Return some statistics on how often words have repeated letters"""
    n = 50
    print("-" * n)
    print("Repeat statistics")
    print("-" * n)
    for f in filenames:
        wordlist_size = get_size_of_wordlist(f)
        print(f"{f} has {wordlist_size} entries")
        for i in range(0, 4):
            wordlist = get_repeated_letter_words(f, i)
            p = round(len(wordlist) / wordlist_size * 100, 2)
            print(f"Words with at least {i} repeated letters:\t{len(wordlist)}\t({p}%)")
            # print(wordlist)
        print("-" * n)


def report_letter_frequency(filenames):
    """Generate graphs with letter frequency data."""
    for f in filenames:
        counts = get_letter_counts(f)
        sorted_counts = sort_dict(counts, reverse=True)
        generate_bar_graph(sorted_counts, f)


def report_word_difficulty(filename):
    """Return a dictionary of all possible words, with a difficulty score.

    A lower score means the letters occur less frequently, making the
    word harder to guess.
    """
    letter_counts = get_letter_counts(valid_solutions)
    letter_scores = normalize_dict(letter_counts)
    score_dict = {}
    with open(filename) as file:
        for word in file:
            word = word.rstrip()
            score = 0
            for char in word:
                score += letter_scores[char]
            score_dict[word] = score
    return score_dict


## Repeat stats
# report_words_with_repeat_letters(file_list)

## Frequency stats
# report_letter_frequency(file_list)


## Word difficulty rank stats
# scores = report_word_difficulty(valid_solutions)
# print(f"Scores generated for {len(scores)} words")
# easiest_word = get_max_key(scores)
# hardest_word = get_min_key(scores)
# print(f"Easiest word (highest score): {easiest_word} ({round(scores[easiest_word],3)})")
# print(f"Hardest word (lowest score):  {hardest_word} ({round(scores[hardest_word],3)})")

# generate_bar_graph_by_position(valid_solutions)
# generate_bar_graph_by_position(valid_guesses)

"""
* number of times letter appears in any word (but only once if it is multiple)
* lowest frequency score word (hardest to guess)
* highest frequency word (easiest to guess)
* score for how hard a given word is to guess

* how does knowing the guess and solution set effect performance?
"""


def get_words(filename):
    """Return a list of all the words."""
    result = []
    with open(filename) as file:
        for line in file:
            result.append(line.rstrip())
    return result


def contains(wordlist, letter):
    """Return a list of words that contain the correct letter."""
    result = []
    for word in wordlist:
        if letter in word:
            result.append(word)
    return result


def does_not_contain(wordlist, letter):
    """Return the words in wordlist that don't contain the specified
    letter. This corresponds to a grey guess in Wordle.
    """
    result = []
    for word in wordlist:
        if letter not in word:
            result.append(word)
    return result


def does_not_contain_at_position(wordlist, letter, position):
    """Return the words in wordlist that don't contain the specified
    letter at the specified position. This corresponds to a repeated
    letter that was marked grey but does exist elsewhere in the word.
    """
    result = []
    for word in wordlist:
        if letter != word[position - 1]:
            result.append(word)
    return result


def contains_at_position(wordlist, letter, position):
    """Return the words that have the letter at the specified position.
    This corresponds to a green guess in Wordle.
    """
    result = []
    for word in wordlist:
        if word[position - 1] == letter:
            result.append(word)
    return result


def contains_not_at_position(wordlist, letter, position):
    """Return the words that have the letter, but not at the specified
    position. These correspond to yellow guesses in wordle.
    """
    result = []
    wordlist = contains(wordlist, letter)
    for word in wordlist:
        if word[position - 1] != letter:
            result.append(word)
    return result


def report_occurences_by_word(words):
    """Report how many words contain each letter."""
    counts = dict.fromkeys(string.ascii_lowercase, 0)
    for w in words:
        for c in counts:
            if c in w:
                counts[c] += 1
    return sort_dict(counts, reverse=True)


def simple_bar_graph(d, num_words):
    """A quick and dirty bar chart."""
    plt.ylim([0, max(d.values()) * 1.3])
    plt.bar(range(len(d)), list(d.values()), align="center")
    plt.xticks(range(len(d)), list(d.keys()))

    for i, v in enumerate(d.values()):
        percent = str(round(v / num_words * 100, 2))
        label = " " + percent + "% (" + str(v) + ")"
        plt.text(i + 0.075, v + 1, label, ha="center", size="x-small", rotation=90)

    plt.show()


def get_letter_scores(wordlist):
    """Return a normalized percent count of each letter. The result is
    what percent of the words in the wordlist contain at least one of
    the letter.
    """
    counts = dict.fromkeys(string.ascii_lowercase, 0)
    for w in wordlist:
        for c in counts:
            if c in w:
                counts[c] += 1

    for c in counts:
        counts[c] = counts[c] / len(wordlist)
    return counts


def get_letter_scores_by_position(wordlist):
    """Return a normalized percent count of each letter. The result is
    what percent of the words in the wordlist contain at least one of
    the letter, separated into positions.

    e.g. : a [0.061, 0.131, 0.133, 0.070, 0.028] means the char 'a'
    occurs in the first position 6.1% of the time, in the second
    position 13.1% of the time, etc.
    """
    # scores = dict.fromkeys(string.ascii_lowercase, [0, 0, 0, 0, 0])
    scores = dict.fromkeys(string.ascii_lowercase)
    for char in scores:
        scores[char] = [0, 0, 0, 0, 0]
    for word in wordlist:
        for i, char in enumerate(word):
            scores[char][i] += 1
    for char in scores:
        for i, score in enumerate(scores[char]):
            scores[char][i] = score / len(wordlist)
    return scores


def position_level_score(wordlist):
    """Calculate a score for each word, using scores that are aware of
    positions.
    """
    char_frequency = get_letter_scores_by_position(wordlist)
    result = {}
    for word in wordlist:
        this_score = 0
        for i, c in enumerate(word):
            this_score += char_frequency[c][i]
        result[word] = this_score
    return sort_dict(result, reverse=True)


def word_level_score(wordlist):
    """Give a score to each word. Each letter adds the % chance it has
    of occuring in a word to the score for the whole word.
    """
    scores = get_letter_scores(wordlist)
    result = {}
    for w in wordlist:
        this_score = 0
        for char in scores:
            if char in w:
                this_score += scores[char]
        result[w] = this_score
    return sort_dict(result, reverse=True)


def count_at_position(wordlist):
    counts = []
    for i in range(0, 5):
        counts.append(dict.fromkeys(string.ascii_lowercase, 0))
    for line in wordlist:
        for i, char in enumerate(line.rstrip()):
            counts[i][char] += 1
    return counts


def print_scores(score_dict, num=15000):
    """Print out all the scores with highest score first."""
    print(f"Count: {len(score_dict)}")
    for i, (k, v) in enumerate(score_dict.items()):
        if i < num:
            print(k, v)


def solve(
    wordlist, word, max_guesses=6, p=True, start_word=None, method=word_level_score
):
    """Simulate a game played"""
    if p:
        print(f"-- Trying to guess '{word}' with method '{method.__name__}'")
    for num in range(1, max_guesses + 1):
        if num == 1 and start_word is not None:
            guess_word = start_word
        else:
            guess_word = next(iter(method(wordlist)))
        result = ""
        for i, char in enumerate(guess_word):
            if char == word[i]:
                result += f"{Colors.fg.GREEN}{char}{Colors.reset}"
                wordlist = contains_at_position(wordlist, char, i + 1)
            elif char in word:
                result += f"{Colors.fg.YELLOW}{char}{Colors.reset}"
                wordlist = contains_not_at_position(wordlist, char, i + 1)
            else:
                result += char
                wordlist = does_not_contain(wordlist, char)
        if p:
            print(f"Guess {num}: {result}")
        if word == guess_word:
            if p:
                print(f"Solved! Took {num} guesses.")
            return num, result
    if p:
        print(f"Did not solve. Go to: {result} Correct word: {word}")
    return None, word


def solve_with_stats(wordlist, method=word_level_score):
    """Collect stats on solver."""

    filename = f"start_word_stats_{method.__name__}.csv"
    words = get_words(wordlist)

    with open(filename, "a") as fileout:
        fileout.write("start,average,max,failed\n")

    for ww in words:
        score_list = []
        all_results = {}
        failed = 0
        failed_list = []
        for w in words:
            sw = ww
            score, result = solve(words, w, max_guesses=26, p=False, start_word=sw)
            all_results[result] = score
            if score is None or score > 6:
                failed += 1
                failed_list.append(result)
            score_list.append(score)

        avg = sum(score_list) / len(score_list)
        print(f"Start word: {sw}")
        print(f"Average: {avg}")
        print(f"Max: {max(score_list)}")
        print(f"Failed: {failed}")

        with open(filename, "a") as fileout:
            fileout.write(f"{sw},{avg},{max(score_list)},{failed}\n")


if __name__ == "__main__":
    words = get_words(valid_solutions)
    # solve(words, "pause", method=word_level_score, start_word="sulci")
    # solve(words, "pause", method=position_level_score)

    words = does_not_contain(words, "o")
    words = does_not_contain(words, "r")
    words = contains_not_at_position(words, "a", 3)
    words = does_not_contain(words, "t")
    words = does_not_contain(words, "e")

    words = does_not_contain(words, "s")
    words = contains_not_at_position(words, "u", 2)
    words = contains_not_at_position(words, "l", 3)
    words = contains_not_at_position(words, "c", 4)
    words = does_not_contain(words, "i")

    print("\nWord level suggestions:")
    print_scores(word_level_score(words), num=30)
    print("\nLetter level suggestions:")
    print_scores(position_level_score(words), num=30)
