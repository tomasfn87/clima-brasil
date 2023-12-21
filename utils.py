import numpy as np
import re
import requests as req
from typing import Any, Dict, List

def capitalize_all(text: str) -> str:
    if " " not in text:
        return text.capitalize()
    exclude: np.ndarray[Any, np.dtype[np.str_]] = \
        np.array(["de", "da", "do", "dos", "das"], dtype="S")
    words: np.ndarray[Any, np.dtype[np.str_]] = np.char.split([text])[0]
    for w in words:
        w = w.lower()
    capitalized_words: np.ndarray[Any, np.dtype[np.str_]] = \
        np.array([], dtype="S")
    for w in words:
        if w in exclude or w[0:2] == "d'":
            capitalized_words = np.append(capitalized_words, w)
        else:
            capitalized_words = np.append(capitalized_words, w.capitalize())
    result: np.ndarray[Any, np.dtype[np.str_]] = \
        np.char.add(" ", capitalized_words)
    return "".join(result).strip()

def is_a_valid_fixed_length_acronym(
    s: str, length: int, acronym_list: List[Dict[str, str]]) -> bool:

    if len(s.strip()) != length:
        return False
    return any(i["acronym"] == s.strip().upper() for i in acronym_list)

def is_web_connection_active() -> bool:
    try:
        response: req.Response = req.get(
            url="https://www.google.com", timeout=5)
        response.raise_for_status()
        return True
    except req.RequestException:
        return False

def limit_empty_spaces(text: str) -> str:
    return re.sub(r"\s{2,}", " ", text, 0)

def list_brazilian_states_acronyms(
    states_list: List[Dict[str, str]]) -> np.ndarray[Any, np.dtype[np.str_]]:

    return np.array([ f'{state["acronym"]} ({state["name"]})'
            for state in states_list ], dtype=np.str_)

def remove_empty_elements(
    arr: List[str]) -> np.ndarray[Any, np.dtype[np.str_]]:

    clean_arr: np.ndarray[Any, np.dtype[np.str_]] = \
        np.array([x for x in arr if x != ""], dtype=np.str_)
    return clean_arr

def remove_starting_empty_spaces(text: str) -> str:
    return re.sub(r"^\s+", "", text, 0)

def semantically_unite(item_list: np.ndarray[Any, np.dtype[np.str_]],
    last_union: str="and", general_union: str=",") -> str:

    result: str = ""
    if len(item_list) == 1:
        result = item_list[0].strip()
    else:
        for i in range(0, len(item_list)):
            result += str(item_list[i])
            if i == len(item_list) - 1:
                break
            if i == len(item_list) - 2:
                result += f" {last_union} "
            else:
                result += f"{general_union} "
    return result

def splitlines_by_length(
    text: str, length: int) -> np.ndarray[Any, np.dtype[np.str_]]:

    words: np.ndarray[Any, np.dtype[np.str_]] = np.char.split([text])[0]
    lines: np.ndarray[Any, np.dtype[np.str_]] = np.array([], dtype="S")
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + bool(current_line):
            if len(current_line) + len(word) + bool(current_line) <= length:
                current_line += word + " "
            else:
                lines = np.append(lines, current_line.strip())
                current_line = word + " "
        else:
            current_line += word + " "

    if current_line:
        lines = np.append(lines, current_line.strip())

    return lines
