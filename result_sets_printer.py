from result_set import ResultSet
from typing import Any, List

import datetime as dt
import numpy as np
import utils as ut

class ResultSetsPrinter:
    def __init__(self: Any, margin: int, min_width: int) -> None:
        if margin < 1:
            self.margin = 2
        else:
            self.margin = margin

        if min_width < 3:
            self.min_width = 79
        else:
            self.min_width = min_width

        self.num_of_results: int = 0
        self.result_list: List[ResultSet] = []

    def add_results(self: Any, results: ResultSet) -> bool:
        if results.get_num_of_results():
            self.result_list.append(results)
            self.num_of_results += results.get_num_of_results()
        return bool(results.get_num_of_results())

    def get_min_width(self: Any) -> int:
        return self.min_width

    def get_num_of_results(self: Any) -> int:
        return self.num_of_results

    def get_base_header_length(self: Any) -> int:
        max_header_length: int = 0
        for i in self.result_list:
            header_length = len(i.get_provider()) + len(i.get_title())
            if header_length > max_header_length:
                max_header_length = header_length
        return max_header_length

    def print_all(self: Any) -> None:
        print(f" ->  {str(dt.datetime.now())[0:19]}")

        r_list = self.result_list

        padding: int = 0
        for r in r_list:
            if r.get_max_key_length() > padding:
                padding = r.get_max_key_length()
        padding += self.margin

        left         : str = "│   "
        before_middle: str = "  "
        middle       : str = "│"
        after_middle : str = "  "
        right        : str = "   │"

        if not len(middle) == 1:
            middle = middle[0] if middle else " "

        max_header_length: int = self.get_base_header_length() \
            + len(left) \
            + len(before_middle) \
            + len(middle) \
            + len(after_middle) \
            + len(right)

        for r in r_list:
            header_length = len(left) \
                + len(before_middle) \
                + len(middle) \
                + len(after_middle) \
                + len(right) \
                + len(r.get_provider()) \
                + len(r.get_title())

            if header_length < self.get_min_width():
                r.set_title("{}{}".format(
                    r.get_title(),
                    " " * (self.get_min_width() - header_length)))

        if self.get_min_width() > max_header_length:
            max_header_length = self.get_min_width()

        for i in range(len(r_list)):
            provider_1: str = left
            provider_2: str = r_list[i].get_provider()
            provider_3: str = before_middle

            title_1: str = after_middle
            title_2: str = r_list[i].get_title()
            title_3: str = "{}{}".format(
                " " * (max_header_length - (
                    len(provider_1)
                    + len(provider_2)
                    + len(provider_3)
                    + len(middle)
                    + len(title_1)
                    + len(title_2)
                    + len(right))),
                right)

            frame: str = "{}{}{}{}{}".format(
                "┌",
                "─" * (
                    len(provider_1)
                    + len(provider_2)
                    + len(provider_3) - 1),
                "┬",
                "─" * (max_header_length - (
                    len(provider_1)
                    + len(provider_2)
                    + len(provider_3)
                    + len(middle)) - 1),
                "┐")

            if i == 0:
                print(frame
                    .replace("─", "═").replace("┬", "╤")
                    .replace("┌", "╒").replace("┐", "╕"), end="")
            else:
                print(frame, end="")

            print(f"\n{provider_1}", end="")
            ut.print_yellow(provider_2, end="")
            print("{}{}{}".format(
                provider_3, middle, title_1), end="")
            ut.print_lyellow(title_2, end="")
            print(title_3)

            print(frame
                .replace("┬", "┴").replace("┌", "└").replace("┐", "┘"))

            union: str = ": "

            max_result_length: int = max_header_length \
                - (padding + len(union)) - 1

            for j in range(len(r_list[i].results)):
                key  : str = list(r_list[i].results[j].keys())[0]
                value: str = list(r_list[i].results[j].values())[0]

                if j % 2 != 0:
                     ut.print_green(f"{key.rjust(padding)}", end="")
                else:
                     ut.print_cyan(f"{key.rjust(padding)}", end="")
                print(union, end="")

                if len(value) > max_result_length:
                    lines: np.ndarray[Any, np.dtype[np.str_]] = \
                        ut.splitlines_by_length(value, max_result_length)
                    if j % 2 != 0:
                        ut.print_lgreen(lines[0])
                    else:
                        ut.print_lcyan(lines[0])
                    for k in range(1, len(lines)):
                        if j % 2 != 0:
                            ut.print_lgreen("{}{}".format(
                                " " * (padding + len(union)), lines[k]))
                        else:
                            ut.print_lcyan("{}{}".format(
                                " " * (padding + len(union)), lines[k]))
                else:
                    if j % 2 != 0:
                        ut.print_lgreen(value)
                    else:
                        ut.print_lcyan(value)

            if i is len(self.result_list) - 1:
                print(f'{"═" * max_header_length}')
