"""A simple Python implementation of the famous Wordle game."""
import random
import PySimpleGUI as sg
from pymongo import MongoClient
from solver_and_stats import (
    contains_at_position,
    contains_not_at_position,
    does_not_contain,
    word_level_score,
    position_level_score,
)

client = MongoClient(port=27017)
db = client.wordle_scores


def get_words(filename):
    """Return a list of all the words in the file."""
    result = []
    with open(filename) as file:
        for line in file:
            result.append(line.rstrip())
    return result


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

    solution_file = "wordlist_solutions.txt"
    guess_file = "wordlist_guesses.txt"
    valid_guesses = get_words(guess_file)
    possible_solutions = get_words(solution_file)
    guesses_made = []
    solution = ""
    solution_index = None
    enable_solver = False
    game_over = False

    def __init__(self, guesses_made=None, enable_solver=True):
        """Set up guess list and pick a solution."""
        self.solution, self.solution_index = self.pick_solution()
        if guesses_made:
            self.guesses_made = guesses_made
        else:
            self.guesses_made = []
        if enable_solver:
            self.enable_solver = True
        print(f"Solution is #{self.solution_index}:'{self.solution}'")

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
            self.possible_solutions = filter_solutions(result, self.possible_solutions)
        return result


def filter_solutions(word, wordlist):
    """Reduce the possible solutions based on the provided word."""
    for i, (char, val) in enumerate(word):
        if val == 2:
            wordlist = contains_at_position(wordlist, char, i + 1)
        elif val == 1:
            wordlist = contains_not_at_position(wordlist, char, i + 1)
        elif val == 0:
            wordlist = does_not_contain(wordlist, char)
    return wordlist


def suggest_word(wordlist, method=word_level_score):
    """Return the next word suggested by the chosen method."""
    return next(iter(method(wordlist)))


class WordleUI:
    """A PySimplGUI UI for a Wordle game."""

    sg.theme("DarkBlack1")
    window = None
    layout = [
        [
            sg.Text("What is your name?"),
            sg.Input(
                key="-NAME-",
                size=(21, 1),
                background_color=Colors.lightGray,
                default_text="Anonymous",
            ),
        ],
        [
            sg.Button(
                "Suggest word",
                key="-SUGGEST-",
            ),
            sg.Button(
                "Clear word",
                key="-CLEAR-",
            ),
        ],
        [
            sg.Text("Guess a word"),
            sg.Input(
                key="-IN-",
                size=(10, 1),
                background_color=Colors.lightGray,
                enable_events=True,
            ),
            sg.Button("Submit", disabled=False, bind_return_key=True),
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
        self.textbox_element = self.window["-IN-"]
        self.display_element = self.window["-ML-"]
        self.display_element("")

    def draw_letter(self, l, color=Colors.darkGray):
        """Draw a letter to the multiline element with the specified
        background color.
        """
        if l == "\n":
            self.display_element.update(
                "\n", background_color_for_value=Colors.background, append=True
            )
        else:
            self.display_element.update(
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
                game_handle.set_game_over()
            elif game_handle.game_is_over():
                sg.popup("Try again!")
        self.textbox_element("")

    def run(self):
        """Start the Wordle UI."""
        wordle = WordleGame(enable_solver=True)
        self.display_element("")
        while True:
            event, values = self.window.read()
            if event is None:
                break
            if event == "Reset":
                wordle = WordleGame(enable_solver=True)
                self.display_element("")
            if event == "-IN-":
                self.validate_user_input("-IN-")
            if event == "Submit":
                self.handle_submit(values["-IN-"].lower(), wordle)
            if event == "-CLEAR-":
                self.window["-IN-"].update("")
            if event == "-SUGGEST-":
                self.window["-IN-"].update(suggest_word(wordle.possible_solutions))
        self.window.close()

    def view_game(self, guess_list):
        """A simple Window to visualize a game."""
        self.textbox_element("")
        for word in guess_list:
            self.draw_word(word)
        self.window.read()
        self.run()


if __name__ == "__main__":
    WordleUI().run()
