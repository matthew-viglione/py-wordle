"""A simple Python implementation of the famous Wordle game."""
import random
import PySimpleGUI as sg


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
    guesses_made = []
    solution = ""
    solution_index = None

    def __init__(self):
        """Set up guess list and pick a solution."""
        self.solution, self.solution_index = self.pick_solution()
        self.guesses_made = []
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

    def game_over(self):
        """Return True if user has used all 6 guesses, else False."""
        if len(self.guesses_made) >= 6:
            return True
        return False

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
        return result


sg.theme("DarkBlack1")
layout = [
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
window = sg.Window("Wordle", layout, element_justification="c").Finalize()
textbox_element = window["-IN-"]
display_element = window["-ML-"]


def draw_letter(l, color=Colors.darkGray):
    """Draw a letter to the multiline element with the specified
    background color.
    """
    if l == "\n":
        display_element.update(
            "\n", background_color_for_value=Colors.background, append=True
        )
    else:
        display_element.update(
            l.upper(),
            text_color_for_value=Colors.white,
            background_color_for_value=color,
            append=True,
        )


def draw_word(word):
    """Draw a full word to the multiline element."""
    draw_letter(" ", Colors.background)
    for i in word:
        if len(i) < 2:
            draw_letter(i[0])
        else:
            draw_letter(i[0], Colors().colormap(i[1]))
    draw_letter(" \n", Colors.background)


def validate_user_input(text_element_key):
    """Limit user input to this field to 5 characters and remove any
    invalid characters on the fly.
    """
    val = values[text_element_key]
    element = window[text_element_key]
    if not val:
        return
    if not val[-1].isalpha():
        element.update(val[:-1])
    if len(val) > 5:
        element.update(val[:-1])


def handle_submit(guess, game_handle):
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
        draw_word(game_handle.evaluate_guess(guess))
        if game_handle.is_solution(guess):
            sg.popup("You got it!")
        elif game_handle.game_over():
            sg.popup("Try again!")


wordle = WordleGame()
while True:
    event, values = window.read()
    if event is None:
        break
    if event == "Reset":
        wordle = WordleGame()
        display_element("")
    if event == "-IN-":
        validate_user_input("-IN-")
    if event == "Submit":
        handle_submit(values["-IN-"].lower(), wordle)
        textbox_element("")
window.close()
