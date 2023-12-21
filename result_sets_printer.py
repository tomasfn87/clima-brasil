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

        # Fix titles that are too small
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
            provider: str = "{}{}{}".format(
                left,
                r_list[i].get_provider(),
                before_middle)

            title: str = "{}{}{}".format(
                after_middle,
                r_list[i].get_title(),
                "{}{}".format(
                    " " * (max_header_length - (
                        len(provider)
                        + len(middle)
                        + len(after_middle)
                        + len(r_list[i].get_title())
                        + len(right))),
                    right))

            header: str = f"{provider}{middle}{title}"

            frame: str = "{}{}{}{}{}".format(
                "┌",
                "─" * (len(provider) - 1),
                "┬",
                "─" * (max_header_length - (len(provider) + len(middle)) - 1),
                "┐")

            # Start impression job
            if i == 0:
                # Frame for first Result Set
                print(frame
                    .replace("─", "═").replace("┬", "╤")
                    .replace("┌", "╒").replace("┐", "╕"), end="")
            else:
                # Frame for remaining Result Sets
                print(frame, end="")

            # Display header inside the frame
            print("\n{}\n{}".format(header, frame
                .replace("┬", "┴").replace("┌", "└").replace("┐", "┘")))

            union: str = ": "

            # Maximum line size is defined by provider and title lengths
            max_result_length: int = max_header_length \
                - (padding + len(union)) - 1

            # Display the actual results (key-value pairs)
            for j in range(len(r_list[i].results)):
                key  : str = list(r_list[i].results[j].keys())[0]
                value: str = list(r_list[i].results[j].values())[0]

                print(f"{key.rjust(padding)}{union}", end="")

                # Case when values need more than one line to be displayed
                if len(value) > max_result_length:
                    lines: np.ndarray[Any, np.dtype[np.str_]] = \
                        ut.splitlines_by_length(value, max_result_length)
                    print(lines[0])
                    for k in range(1, len(lines)):
                        print("{}{}".format(
                            " " * (padding + len(union)), lines[k]))
                # Case when values need only one line to be displayed
                else:
                    print(value)

            # Finish impression job
            if i is len(self.result_list) - 1:
                print(f'{"═" * max_header_length}')
