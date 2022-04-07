"""A simple Python implementation of the famous Wordle game."""
import random
import string
import PySimpleGUI as sg


def get_words(filename):
    """Return a list of all the words in the file."""
    result = []
    with open(filename) as file:
        for line in file:
            result.append(line.rstrip())
    return result


def sort_dict(d, reverse=True):
    """Return the dictionary sorted by value."""
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=reverse))


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


def reduce_solutions(wordscore, wordlist):
    """Reduce the possible solutions based on the provided wordscore."""
    char_count = {i[0]: 0 for i in wordscore}
    for char, _ in wordscore:
        char_count[char] += 1
    for i, (char, val) in enumerate(wordscore):
        if val == 2:
            wordlist = contains_at_position(wordlist, char, i + 1)
        elif val == 1:
            wordlist = contains_not_at_position(wordlist, char, i + 1)
        elif val == 0:
            if char_count[char] > 1:
                wordlist = does_not_contain_at_position(wordlist, char, i + 1)
            else:
                wordlist = does_not_contain(wordlist, char)
    return wordlist


class Colors:
    """A class containing the original Wordle colors for easy use."""

    green = "#6aaa64"
    darkendGreen = "#538d4e"
    yellow = "#c9b458"
    darkendYellow = "#b59f3b"
    lightGray = "#d8d8d8"
    gray = "#86888a"
    darkGray = "#939598"
    white = "#fff"
    black = "#212121"
    background = black

    def colormap(self, n):
        """Return the color code for numbers 0, 1, and 2. These are the
        background colors of guesses.
        """
        return [self.darkGray, self.yellow, self.green][n]


class WordleGame:
    """A class representing a Wordle game."""

    guess_file = "wordlist_guesses.txt"
    solution_file = "wordlist_solutions.txt"
    valid_guesses = get_words(guess_file)
    possible_solutions = get_words(solution_file)
    guesses_made = []
    solution = ""
    solution_index = None
    enable_solver = False
    game_over = False
    solved = False

    def __init__(self, guesses_made=None, enable_solver=True, solution=None):
        """Set up guess list and pick a solution."""
        if solution is None:
            self.solution, self.solution_index = self.pick_solution()
        else:
            self.solution = solution
            self.solution_index = self.possible_solutions.index(solution)
        if guesses_made:
            self.guesses_made = guesses_made
        else:
            self.guesses_made = []
        if enable_solver:
            self.enable_solver = True
        # print(f"Solution is #{self.solution_index}:'{self.solution}'")

    def pick_solution(self, n=None):
        """Return the solution word, or a random solution if no index
        was specified.
        """
        valid_solutions = get_words(self.solution_file)
        if n is None:
            n = random.randint(0, len(valid_solutions))
        return valid_solutions[n], n

    def is_valid_guess(self, word):
        """Return True if the word is a valid guess, else False."""
        if word in self.valid_guesses:
            return True
        return False

    def is_solution(self, word):
        """Return True if word is the solution, else return False."""
        if word == self.solution:
            return True
        return False

    def game_is_over(self):
        """Return True if user has used all 6 guesses or the game was
        previously determined to be over, else return False.
        """
        if len(self.guesses_made) >= 6 or self.game_over:
            return True
        return False

    def set_game_over(self):
        """Set the game over flag."""
        self.game_over = True

    def evaluate_guess(self, guess):
        """Return a list representing how the guess matches the
        solution. Each character in the guess gets a value:

        0 - grey   - letter is not in the solution at any position
        1 - yellow - letter is in the solution at a different position
        2 - green  - letter is in the solution at the correct position
        """
        result = [[i, 0] for i in guess]
        count = {i: self.solution.count(i) for i in self.solution}
        for i, letter in enumerate(guess):
            if letter == self.solution[i]:
                result[i][1] = 2
                count[letter] -= 1
        for i, letter in enumerate(guess):
            if letter in self.solution and count[letter] > 0 and result[i][1] != 2:
                result[i][1] = 1
                count[letter] -= 1
        self.guesses_made.append(result)
        if self.enable_solver:
            self.possible_solutions = reduce_solutions(result, self.possible_solutions)
        if len(self.guesses_made) >= 6:
            self.game_over = True
        if guess == self.solution:
            self.game_over = True
            self.solved = True
        return result

    def suggest_word(self, wordlist=None, method=word_level_score):
        """Return the next word suggested by the chosen method."""
        if wordlist is None:
            wordlist = self.possible_solutions
        return next(iter(method(wordlist)))

    def solve(self, method=word_level_score, first_guess="later"):
        """Solve the game using the provided method. Returns the guess
        list and scores, and whether or not the puzzle was solved.

        Providing a pre-computed first guess that partitions the
        solution space well can greatly speed up solving. For example,
        using the basic word level score function without a pre-selected
        first guess takes 13.53 seconds to solve all possible puzzles.
        Adding the first guess 'later' (which will always be the same
        word, depending on the algorithm) sped the time up to 2.15
        seconds, a 6.3x speedup.
        """
        while not self.game_is_over():
            if first_guess is not None and len(self.guesses_made) == 0:
                self.evaluate_guess(first_guess)
                first_guess = None
            else:
                self.evaluate_guess(self.suggest_word(method=method))
        return self.guesses_made, self.solved


class WordleUI:
    """A PySimplGUI UI for a Wordle game."""

    sg.theme("DarkBlack1")
    window = None
    layout = [
        [
            sg.Text("Guess a word"),
            sg.Input(
                key="-IN-",
                size=(10, 1),
                background_color=Colors.lightGray,
                enable_events=True,
            ),
            sg.Button("Clear", key="-CLEAR-"),
            sg.Button("Submit", disabled=False, bind_return_key=True),
        ],
        [
            sg.Button("Suggest word", key="-SUGGEST-"),
            sg.Button("Solve", key="-SOLVE-"),
            sg.Button("Reset"),
        ],
        [
            sg.Multiline(
                size=(7, 6),
                font=("Consolas", 50),
                justification="c",
                disabled=True,
                write_only=True,
                no_scrollbar=True,
                background_color=Colors.background,
                key="-ML-",
            )
        ],
    ]

    def __init__(self):
        self.window = sg.Window(
            "Wordle", self.layout, element_justification="c"
        ).Finalize()
        self.window["-ML-"].update("")

    def draw_letter(self, l, color=Colors.darkGray):
        """Draw a letter to the multiline element with the specified
        background color.
        """
        if l == "\n":
            self.window["-ML-"].update(
                "\n", background_color_for_value=Colors.background, append=True
            )
        else:
            self.window["-ML-"].update(
                l.upper(),
                text_color_for_value=Colors.white,
                background_color_for_value=color,
                append=True,
            )

    def draw_word(self, word):
        """Draw a full word to the multiline element."""
        self.draw_letter(" ", Colors.background)
        for i in word:
            self.draw_letter(i[0], Colors().colormap(i[1]))
        self.draw_letter(" \n", Colors.background)

    def validate_user_input(self, text_element_key):
        """Limit user input to this field to 5 characters and remove any
        invalid characters on the fly.
        """
        element = self.window[text_element_key]
        val = element.get()
        if not val:
            return
        if not val[-1].isalpha():
            element.update(val[:-1])
        if len(val) > 5:
            element.update(val[:-1])

    def handle_submit(self, guess, game_handle):
        """Make sure the guess is the right length and is a valid word, then
        submit it to the game controller.
        """
        if len(guess) < 5:
            sg.popup("Too few letters!")
        elif len(guess) > 5:
            sg.popup("Too many letters!")
        elif not game_handle.is_valid_guess(guess):
            sg.popup("Not a valid word!")
        else:
            if not game_handle.game_is_over():
                result = game_handle.evaluate_guess(guess)
                self.draw_word(result)
            if game_handle.is_solution(guess):
                sg.popup("You got it!")
            elif game_handle.game_is_over():
                sg.popup("Try again!")
        self.window["-IN-"].update("")

    def run(self):
        """Start the Wordle UI."""
        wordle = WordleGame(enable_solver=True)
        self.window["-ML-"].update("")
        while True:
            event, values = self.window.read()
            if event is None:
                break
            if event == "Reset":
                wordle = WordleGame(enable_solver=True)
                self.window["-ML-"].update("")
            if event == "-IN-":
                self.validate_user_input("-IN-")
            if event == "Submit":
                self.handle_submit(values["-IN-"].lower(), wordle)
            if event == "-CLEAR-":
                self.window["-IN-"].update("")
            if event == "-SUGGEST-":
                self.window["-IN-"](wordle.suggest_word())
            if event == "-SOLVE-":
                if not wordle.game_is_over():
                    self.window["-ML-"].update("")
                    for word in wordle.solve()[0]:
                        self.draw_word(word)

        self.window.close()

    def view_game(self, guess_list):
        """A simple Window to visualize a game."""
        self.window["-IN-"].update("")
        for word in guess_list:
            self.draw_word(word)
        self.window.read()
        self.run()


def run_solver_benchmarks():
    """Solve all possible puzzles and print some statistics."""

    from timeit import default_timer as timer

    all_solutions = get_words("wordlist_solutions.txt")
    blacklist = []
    unsolved = []
    num_guesses = []
    start = timer()
    for w in all_solutions:
        try:
            game = WordleGame(enable_solver=True, solution=w)
            # print(game.solve())
            result, solved = game.solve()
            if not solved:
                unsolved.append(w)
            else:
                num_guesses.append(len(result))
        except ZeroDivisionError:
            print("Zero division! ", w)
            blacklist.append(w)
    end = timer()
    print(f"Blacklist {len(blacklist)}: {blacklist}")
    print(f"Unsolved {len(unsolved)}: {unsolved}")
    print(f"Average score: {sum(num_guesses)/len(num_guesses)}")
    print(f"Elapsed time: {end - start}")


def make_score(word, score):
    """Return a wordscore list from two strings that can be used by the
    solver's reduce function.

    e.g. word='later' and score='21011' would give
        [['l', 2], ['a', 1], ['t', 0], ['e', 1], ['r', 1]]
    """
    return [[l, int(s)] for l, s in zip(word, score)]


def manual_solver(guesses):
    """Use this to solve Wordle games in progress."""

    def print_scores(score_dict, num=15000):
        """Print out all the scores with highest score first."""
        print(f"Count: {len(score_dict)}")
        for i, (k, v) in enumerate(score_dict.items()):
            if i < num:
                print(k, v)

    words = get_words("wordlist_solutions.txt")
    for guess in guesses:
        words = reduce_solutions(make_score(guess[0], guess[1]), words)
    print("Word level suggestions:")
    print_scores(word_level_score(words), num=5)


if __name__ == "__main__":
    # WordleUI().run()
    # run_solver_benchmarks()

    guess_list = [
        [
            ("orate", "01201"),
            ("sulci", "00000"),
        ]
    ]

    for i, g in enumerate(guess_list):
        print(f"----------------Puzzle {i+1}----------------")
        manual_solver(g)
