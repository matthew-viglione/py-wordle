import PySimpleGUI as sg

from wordle_game import Colors


def print_button_states(m):
    for i in m:
        print(i)


c = Colors()
num_x = 5
num_y = 6

layout = [
    [sg.Button("Clear"), sg.Button("Submit")],
    [
        [
            sg.Button(" " * 4, button_color=c.colormap(0), key=(f"b-{i}-{j}"))
            for i in range(num_x)
        ]
        for j in range(num_y)
    ],
]

window = sg.Window("", element_justification="c").Layout(layout)

colors = [[0 for _ in range(num_x)] for _ in range(num_y)]
while True:
    event, values = window.read()
    if event is None:
        break
    if event == "Clear":
        colors = [[0 for _ in range(num_x)] for _ in range(num_y)]
        for x in range(num_x):
            for y in range(num_y):
                window[f"b-{x}-{y}"].Update(button_color=c.colormap(0))
    elif "b-" in event:
        e = event.split("-")
        x, y = int(e[2]), int(e[1])
        colors[x][y] = (colors[x][y] + 1) % 3
        print(event)
        print_button_states(colors)
        window[event].Update(button_color=c.colormap(colors[x][y] % 3))
