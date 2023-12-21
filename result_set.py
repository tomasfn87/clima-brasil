import utils as ut
from typing import Any, Dict, List

class ResultSet:
    def __init__(
        self: Any,
        provider: str="Result set provider",
        title: str="Result set title") -> None:

        self.title = ut.remove_starting_empty_spaces(
            ut.limit_empty_spaces(title))
        self.provider = ut.limit_empty_spaces(provider.strip())
        self.num_of_results: int = 0
        self.results: List[Dict[str, str]] = []

    def add_key_value(self: Any, key: str, value: str) -> bool:
        if (not any(list(i.keys())[0] == key for i in self.results) \
            and key.strip() and value.strip()):
            self.results.append({
                ut.limit_empty_spaces(key.strip()):
                ut.limit_empty_spaces(value.strip())})
            self.num_of_results += 1
            return True
        else:
            print("Resultado não foi adicionado ", end="")
            print("(chave: {}, valor: {}).".format(
                ut.limit_empty_spaces(key.strip()),
                ut.limit_empty_spaces(value.strip())))
            return False

    def get_provider(self: Any) -> str:
        return self.provider

    def get_title(self: Any) -> str:
        return self.title

    def set_title(self: Any, new_title: str) -> bool:
        if len(ut.remove_starting_empty_spaces(new_title)):
            self.title = new_title
        return bool(ut.remove_starting_empty_spaces(new_title))

    def get_num_of_results(self: Any) -> int:
        return self.num_of_results

    def get_max_key_length(self: Any) -> int:
        max_key_length: int = 0
        for i in range(len(self.results)):
            key: str = list(self.results[i].keys())[0]
            if len(key) > max_key_length:
                max_key_length = len(key)
        return max_key_length