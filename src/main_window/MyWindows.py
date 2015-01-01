__author__ = 'Anti'

import Tkinter
import tkColorChooser


sensor_names = ["AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"]
headset_freq = 128


class AbstractWindow(object):
    def __init__(self, title, width, height, color="#eeeeee"):
        self.window_width = width
        self.window_height = height
        self.name = title
        self.title(title)
        self.resizable(0, 0)
        self.configure(background=color)

    def exit(self):
        self.destroy()


class TkWindow(AbstractWindow, Tkinter.Tk):
    def __init__(self, title, width, height, color="#eeeeee"):
        Tkinter.Tk.__init__(self)
        AbstractWindow.__init__(self, title, width, height, color)


class ToplevelWindow(AbstractWindow, Tkinter.Toplevel):
    def __init__(self, title, width, height, color="#eeeeee"):
        Tkinter.Toplevel.__init__(self)
        AbstractWindow.__init__(self, title, width, height, color)


def validate(textbox, function):
    try:
        function(textbox)
        textbox.configure(background="#ffffff")
        return True
    except:
        textbox.configure(background="#ff0000")
        return False


def saveColor(button, textbox):
    previous = textbox.get()
    try:
        color = tkColorChooser.askcolor(previous)[1]
    except:
        color = tkColorChooser.askcolor()[1]
    if color is None:
        color = previous
    textbox.delete(0, Tkinter.END)
    textbox.insert(0, color)
    validateButtonColor(button, textbox)


def validateButtonColor(button, textbox):
    return validate(textbox, lambda x: button.configure(background=textbox.get()))


def newColorButton(frame, name, column=0, row=0):
    button = Tkinter.Button(frame, text=name)
    button.grid(column=column, row=row, padx=5, pady=5)
    textbox = Tkinter.Entry(frame, width=7, validate="focusout", validatecommand=lambda: validateButtonColor(button, textbox))
    textbox.grid(column=column+1, row=row, padx=5, pady=5)
    button.config(command=lambda: saveColor(button, textbox))
    return textbox, button


def newTextBox(frame, text, column=0, row=0, width=5, validatefunction=lambda x: int(x.get())):
    Tkinter.Label(frame, text=text+":").grid(column=column, row=row, padx=5, pady=5)
    textbox = Tkinter.Entry(frame, width=width, validate="focusout", validatecommand=lambda: validate(textbox, validatefunction))
    textbox.grid(column=column+1, row=row, padx=5, pady=5)
    return textbox


def newCheckbox(frame, text, column=0, row=0, columnspan=2, padx=5, pady=5, command=None):
    var = Tkinter.IntVar()
    button = Tkinter.Checkbutton(frame, text=text, variable=var, command=command)
    button.grid(column=column, row=row, padx=padx, pady=pady, columnspan=columnspan)
    return var, button


def updateTextbox(textbox, value):
    previous_state = textbox.config("state")[4]
    textbox.config(state=Tkinter.NORMAL)
    textbox.delete(0, Tkinter.END)
    textbox.insert(0, value)
    textbox.config(state=previous_state)


def updateVar(var, value):
    var.set(value)


def updateDict(dictionary, values, set):
    for pair in values:
        key, value = pair.split(":")
        set(dictionary[key], value)


def saveDict(dictionary, file, end="\n"):
    for key in sorted(dictionary):
        value = str(dictionary[key].get())
        file.write(str(key)+":"+(value if value != "" else "0")+" ")
    file.write(end)


def initButtonFrame(frame, button_names, commands, start_column=0, start_row=0, buttons={}, buttons_in_row=0, columnspan=1):
    for i in range(len(button_names)):
        if buttons_in_row == 0:
            column = start_column + i
            row = start_row
        else:
            column = start_column + i % buttons_in_row
            row = start_row + i//buttons_in_row
        column *= columnspan
        buttons[button_names[i]] = Tkinter.Button(frame, text=button_names[i],command=commands[i])
        buttons[button_names[i]].grid(column=column, row=row, padx=5, pady=5, columnspan=columnspan)
