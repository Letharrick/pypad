import functools
import os
import tkinter as tk
import traceback
from argparse import ArgumentParser
from collections import OrderedDict
from pathlib import Path
import tkinter.font as tk_font
from tkinter import messagebox as tk_messagebox
from tkinter import filedialog as tk_filedialog

class RetainMethods(type):
    @classmethod
    def __prepare__(metacls, name, bases, **kwargs):
        return OrderedDict()

    def __new__(cls, name, bases, namespace, **kwargs):
        result = type.__new__(cls, name, bases, dict(namespace))
        result.__methods__ = namespace

        return result

class AutoMenu(tk.Menu, metaclass=RetainMethods):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for func_name, func in self.__methods__.items():
            if not func_name.startswith('_'):
                command = functools.partial(func, self)
                self.add_command(label=func_name.replace('_', ' ').title(), command=command)

class File(AutoMenu):
    def __init__(self, pypad, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pypad = pypad

    def new(self):
        self.pypad.file = self.pypad.DEFAULT_FILE_PATH

    def open(self):
        f = tk.filedialog.askopenfile(
            filetypes=[('All Files', '.*'), ('Text Files', '.txt')],
            mode='r'
        )

        if f:
            self.pypad.file = f.name
            f.close()

    def save(self):
        if os.path.isfile(self.pypad.file):
            with open(self.pypad.file, 'w') as f:
                f.write(self.pypad.editor.get(1.0, tk.END))
        else:
            self.save_as()

    def save_as(self):
        f = tk.filedialog.asksaveasfile(
            filetypes=[('All Files', '.*'), ('Text Files', '.txt')],
            initialfile=self.pypad.file,
            mode='w'
        )
        
        if f:
            f.write(self.pypad.editor.get(1.0, tk.END))
            f.close()

    def exit(self):
        self.pypad.quit()

class PyPad(tk.Tk):
    DEFAULT_FILE_PATH = './untitled.txt'
    FONT_FAMILY = 'Consolas'
    FONT_SIZE = 12
    WINDOW_DIMENSIONS = (800, 600)

    def __init__(self, filepath=DEFAULT_FILE_PATH):
        super().__init__()

        self.menu_bar = tk.Menu(self)
        self.editor = tk.Text(self)
        self.font = tk.font.Font(family=PyPad.FONT_FAMILY, size=PyPad.FONT_SIZE)
        self.__file = Path(filepath.strip(' ') or PyPad.DEFAULT_FILE_PATH)

    @property
    def file(self):
        return self.__file

    @file.setter
    def file(self, file_path_str):
        file_path = Path(file_path_str)
        
        if file_path:
            self.__file = file_path
            self.editor.delete(1.0, tk.END)
            self.title(f'{file_path} - {self.__class__.__name__}')
            
            if file_path.exists():
                with file_path.open() as f:
                    self.editor.insert(tk.END, f.read())

    def start(self):
        self.__setup_window()
        self.__setup_widgets()
        
        self.mainloop()

    def __exception_callback(self, error_type, error, traceback_):
        tk.messagebox.showerror(title=error.__class__.__name__, message=traceback.format_exc())

    def __setup_window(self):
        self.title(f'{self.__file} - {self.__class__.__name__}')
        self.geometry(f'{self.WINDOW_DIMENSIONS[0]}x{self.WINDOW_DIMENSIONS[1]}')
        self.config(menu=self.menu_bar)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.report_callback_exception = self.__exception_callback

    def __setup_widgets(self):
        self.menu_bar.add_cascade(label='File', menu=File(self, tearoff=False))
        self.editor.grid(column=0, row=1, sticky='NESW')
        self.editor.config(font=self.font)

def main():
    argparser = ArgumentParser(description='Choose the file you\'d like to open with PyPad')
    argparser.add_argument(
        '-f',
        '--file',
        dest='file',
        type=str,
        help='The file to open with PyPad',
        default=PyPad.DEFAULT_FILE_PATH
    )
    
    args = argparser.parse_args()

    pypad = PyPad(args.file)
    pypad.start()

if __name__ == '__main__':
    main()