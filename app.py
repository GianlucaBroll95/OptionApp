"""
A tkinter app
"""
import os
import sys

import future.moves.tkinter as tk
from future.moves.tkinter import ttk
from future.moves.tkinter.messagebox import showerror
from option_class import Option
from utils.param_parser import param_parser


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class OptionApp(ttk.Frame):
    _FIELDS = ["price", "strike", "maturity", "volatility",  "risk_free_rate", "dividend_yield"]
    options = {'padx': 5, 'pady': 5}
    col, row = 0, 0

    def __init__(self, container):
        super().__init__(container)
        self._set_entry()

        self.calculate_button = ttk.Button(self, text="Calculate Price")
        self.calculate_button.grid(columnspan=3, row=self.row + 1, sticky="ew")
        self.calculate_button["command"] = self._get_option_price

        self.greek_button = ttk.Button(self, text="Calculate Greeks")
        self.greek_button.grid(columnspan=3, row=self.row + 2, sticky="ew")
        self.greek_button["command"] = self._get_option_greeks

        self.grid(padx=10, pady=10, sticky=tk.NSEW)

    def _set_entry(self):
        for entry in self._FIELDS:
            setattr(self, entry + "_label",
                    ttk.Label(self, text=entry.title().replace("_", " ") + ":", width=25).grid(columnspan=2,
                                                                                               row=OptionApp.row,
                                                                                               sticky="e",
                                                                                               **self.options))
            setattr(self, entry, tk.StringVar())
            setattr(self, entry + "_entry",
                    ttk.Entry(self, textvariable=getattr(self, entry), width=20).grid(column=self.col + 2, row=self.row,
                                                                                      **self.options))
            OptionApp.row += 1

    def _get_option_price(self):
        param = {entry: getattr(self, entry).get() for entry in self._FIELDS}
        font = ('Helvetica', 9, 'bold')
        try:
            option = Option(**param_parser(param))
            call, put = option.black_scholes_price()
            self.header = ttk.Label(self, text="Call Option", font=font).grid(column=1, row=9)
            self.header = ttk.Label(self, text="Put Option", font=font).grid(column=2, row=9)
            self.index = ttk.Label(self, text="Price (B&S):", width=14, font=font).grid(column=0, row=10, sticky="w")
            self.call = ttk.Label(self, text=f"${call:.2f}").grid(column=1, row=10)
            self.put = ttk.Label(self, text=f"${put:.2f}").grid(column=2, row=10)
        except ValueError as error:
            showerror(title='Error', message=error)
        except TypeError as error:
            showerror(title='Error', message=error)

    def _get_option_greeks(self):
        param = {entry: getattr(self, entry).get() for entry in self._FIELDS}
        greeks = "Delta", "Gamma", "Theta", "Vega", "Rho"
        font = ('Helvetica', 9, 'bold')
        OptionApp.row += 5
        try:
            option = Option(**param_parser(param))
            greeks_values = option.greeks()
            for greek, greek_value in zip(greeks, greeks_values):
                setattr(self, greek + "_name",
                        ttk.Label(self, text=greek + ":", font=font).grid(column=0, row=OptionApp.row, sticky="w"))
                setattr(self, greek + "_c_value",
                        ttk.Label(self, text=greek_value[0]).grid(column=1, row=OptionApp.row))
                setattr(self, greek + "_p_value",
                        ttk.Label(self, text=greek_value[1]).grid(column=2, row=OptionApp.row))
                OptionApp.row += 1
            OptionApp.row -= 10
        except ValueError as error:
            showerror(title='Error', message=error)
        except TypeError as error:
            showerror(title='Error', message=error)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Option Calculator")
        self.iconbitmap(default=resource_path("fintech.ico"))
        self.geometry("320x425")
        self.label = tk.Label(self, text="Option Price Calculator", font=('Helvetica', 12, 'bold'))
        self.label.grid()
        self.resizable(False, False)


app = App()
OptionApp(app)
app.mainloop()
