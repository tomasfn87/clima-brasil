from result_set import ResultSet
from result_sets_printer import ResultSetsPrinter
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from typing import Any, Callable
from zoneinfo import ZoneInfo
import numpy as np
import re
import sys
import time as t
import utils as ut

class CssSel:
    @staticmethod
    def climatempo_1(data_id: str, variant: str = "") -> str:
        result = f".daily-variables-grid__item.-{data_id}"
        result += " .daily-variables-grid__value"

        if not variant:
            return result

        return f"{result}.-{variant}"

class Operation:
    @staticmethod
    def join(separator: str) -> Callable[[list[str]], str]:
        return lambda data: separator.join(data)

class Change:
    @staticmethod
    def append(suffix: str) -> Callable[[str], str]:
        return lambda data: data + suffix

    @staticmethod
    def replace(old: str, new: str) -> Callable[[str], str]:
        return lambda data: data.replace(old, new)

class DataRecoveryInstruction:
    def __init__(self, title: str, css_selector: str):
        self.title: str = title
        self.css_selector: str = css_selector

        self.operations: list[Callable] = []
        self.changes: list[Callable] = []

    def get_title(self) -> str:
        return self.title

    def get_css_selector(self) -> str:
        return self.css_selector

    def get_operations(self) -> list[Callable]:
        return self.operations

    def get_changes(self) -> list[Callable]:
        return self.changes

    def add_operation(self, operation: Callable):
        self.operations.append(operation)

    def add_change(self, change: Callable):
        self.changes.append(change)

def main() -> None:
    inputs: list[str] = sys.argv

    if len(inputs) < 3:
        print("ERRO: é necessário digitar cidade e estado.")
        print_examples()
        return
    elif len(inputs) > 4:
        print("ERRO: digite apenas cidade e estado; coloque aspas simples ou")
        print("  duplas se o nome da cidade possuir mais de uma palavra ou")
        print(r"    utilize a barra invertida (\) para cancelar um espaço ")
        print("      vazio como separador de argumentos.")
        print_examples()
        return

    cidade: str = inputs[1]
    estado: str = inputs[2]

    estados_brasileiros = np.array([
        { "acronym": "AC", "name": "Acre" },
        { "acronym": "AL", "name": "Alagoas" },
        { "acronym": "AP", "name": "Amapá" },
        { "acronym": "AM", "name": "Amazonas" },
        { "acronym": "BA", "name": "Bahia" },
        { "acronym": "CE", "name": "Ceará" },
        { "acronym": "DF", "name": "Distrito Federal" },
        { "acronym": "ES", "name": "Espírito Santo" },
        { "acronym": "GO", "name": "Goiás" },
        { "acronym": "MA", "name": "Maranhão" },
        { "acronym": "MT", "name": "Mato Grosso" },
        { "acronym": "MS", "name": "Mato Grosso do Sul" },
        { "acronym": "MG", "name": "Minas Gerais" },
        { "acronym": "PA", "name": "Pará" },
        { "acronym": "PB", "name": "Paraíba" },
        { "acronym": "PR", "name": "Paraná" },
        { "acronym": "PE", "name": "Pernambuco" },
        { "acronym": "PI", "name": "Piauí" },
        { "acronym": "RJ", "name": "Rio de Janeiro" },
        { "acronym": "RN", "name": "Rio Grande do Norte" },
        { "acronym": "RS", "name": "Rio Grande do Sul" },
        { "acronym": "RO", "name": "Rondônia" },
        { "acronym": "RR", "name": "Roraima" },
        { "acronym": "SC", "name": "Santa Catarina" },
        { "acronym": "SP", "name": "São Paulo" },
        { "acronym": "SE", "name": "Sergipe "},
        { "acronym": "TO", "name": "Tocantins" }
    ], dtype=np.object_)

    if not ut.is_a_valid_fixed_length_acronym(
        s=estado, length=2, acronym_list=estados_brasileiros):

        print("ERRO: o segundo argumento deve ser uma sigla válida ", end="")
        print("de estado brasileiro (UF).")
        subtitle: str = "Siglas válidas:"
        print("\n  {}\n  {}\n\n    {}.".format(
            subtitle, "-" * len(subtitle), ut.semantically_unite(
                ut.list_brazilian_states_acronyms(
                    states_list=estados_brasileiros), "ou")))
        return

    if not ut.is_web_connection_active():
        print("ERRO: sem conexão à Internet.")
        return

    if len(inputs) == 4:
        headless: str = inputs[3]
        if re.match("(?i)^(true|false)$", headless):
            if re.match("(?i)true", headless):
                clima(
                    cidade=cidade, estado=estado, headless=True)
            if re.match("(?i)false", headless):
                clima(
                    cidade=cidade, estado=estado, headless=False)
    else:
        clima(cidade=cidade, estado=estado)

def print_examples() -> None:
    print("\n - Exemplo 1:")
    print("\tpython3 previsao_do_tempo_brasil.py Brasília DF")
    print("\n - Exemplo 2:")
    print("\tpython3 previsao_do_tempo_brasil.py \"são paulo\" sp")
    print("\n - Exemplo 3:")
    print("\t", end="")
    print(r"python3 previsao_do_tempo_brasil.py rio\ de\ janeiro rj")

def clima(
    cidade: str, estado: str, headless: bool=True) -> None:

    resultados_previsao_tempo: ResultSet = previsao_tempo_climatempo(
        cidade=cidade, estado=estado, headless=headless)

    result_printer: ResultSetsPrinter = ResultSetsPrinter(
        margin=2, min_width=72)

    if resultados_previsao_tempo.get_num_of_results():
        result_printer.add_results(resultados_previsao_tempo)

    if result_printer.get_num_of_results():
        result_printer.print_all(tz=ZoneInfo("America/Sao_Paulo"))
    else:
        print("ERRO: as informações estão indisponíveis. ", end="")
        print("Tente novamente mais tarde.")

def previsao_tempo_climatempo(
    cidade: str, estado: str, headless: bool=False) -> ResultSet:

    provider: str = "ClimaTempo"
    title: str = "Previsão do tempo em "
    title += f"{ut.capitalize_all(cidade)}/{estado.upper()}, Brasil"

    results: ResultSet = ResultSet(provider=provider, title=title)

    try:
        browser: wd.Chrome = start_chrome(headless=headless)
        browser.get("https://www.duckduckgo.com")

        t.sleep(1)
        browser.implicitly_wait(2)

        browser.find_element(
            By.CSS_SELECTOR, 'textarea[data-mode="search"]') \
            .send_keys(
                f"climatempo previsao-do-tempo {cidade} {estado} brasil",
                Keys.ENTER)

        t.sleep(1)
        browser.implicitly_wait(2)

        browser.find_element(
            By.CSS_SELECTOR, 'article h2 a[href*="previsao-do-tempo/cidade"]'
        ).click()

        t.sleep(1)
        browser.implicitly_wait(2)

        comparacao = DataRecoveryInstruction(
            title='Comparação',
            css_selector='.today-forecast-card__intro'
        )
        comparacao.add_operation(Operation.join(' '))
        comparacao.add_change(Change.append('.'))

        descricao = DataRecoveryInstruction(
            title='Descrição',
            css_selector='.today-forecast-card__desc'
        )

        temperatura_minima = DataRecoveryInstruction(
            title='Temperatura mínima',
            css_selector=CssSel.climatempo_1('temperature', 'cool')
        )
        temperatura_minima.add_change(Change.append('C'))

        temperatura_maxima = DataRecoveryInstruction(
            title='Temperatura máxima',
            css_selector=CssSel.climatempo_1('temperature', 'warm')
        )
        temperatura_maxima.add_change(Change.append('C'))

        sensacao_termica_minima = DataRecoveryInstruction(
            title='Sensação térmica mínima',
            css_selector=CssSel.climatempo_1('thermal', 'cool')
        )
        sensacao_termica_minima.add_change(Change.append('C'))

        sensacao_termica_maxima = DataRecoveryInstruction(
            title='Sensação térmica máxima',
            css_selector=CssSel.climatempo_1('thermal', 'warm')
        )
        sensacao_termica_maxima.add_change(Change.append('C'))

        pluviosidade = DataRecoveryInstruction(
            title='Pluviosidade',
            css_selector=CssSel.climatempo_1('rain')
        )
        pluviosidade.add_change(Change.replace('.', ','))

        humidade_minima = DataRecoveryInstruction(
            title='Humidade mínima',
            css_selector=CssSel.climatempo_1('humidity', 'cool')
        )

        humidade_maxima = DataRecoveryInstruction(
            title='Humidade máxima',
            css_selector=CssSel.climatempo_1('humidity', 'warm')
        )

        horario_sol = DataRecoveryInstruction(
            title='Horário sol',
            css_selector=CssSel.climatempo_1('sun')
        )

        vento = DataRecoveryInstruction(
            title='Vento',
            css_selector=CssSel.climatempo_1('wind')
        )

        rajada_de_vento = DataRecoveryInstruction(
            title='Rajada de vento',
            css_selector=CssSel.climatempo_1('gust')
        )

        arco_iris = DataRecoveryInstruction(
            title='Arco-íris',
            css_selector=CssSel.climatempo_1('rainbow')
        )
        arco_iris.add_change(Change.replace('probabilid.', 'probabilidade'))

        data_recovery_instructions: list[DataRecoveryInstruction] = []
        data_recovery_instructions.append(comparacao)
        data_recovery_instructions.append(descricao)
        data_recovery_instructions.append(temperatura_minima)
        data_recovery_instructions.append(temperatura_maxima)
        data_recovery_instructions.append(sensacao_termica_minima)
        data_recovery_instructions.append(sensacao_termica_maxima)
        data_recovery_instructions.append(pluviosidade)
        data_recovery_instructions.append(humidade_minima)
        data_recovery_instructions.append(humidade_maxima)
        data_recovery_instructions.append(horario_sol)
        data_recovery_instructions.append(vento)
        data_recovery_instructions.append(rajada_de_vento)
        data_recovery_instructions.append(arco_iris)

        for instruction in data_recovery_instructions:
            data = try_to_recover_data(browser, instruction)
            if data:
                results.add_key_value(instruction.get_title(), data)

    finally:
        browser.quit()

    return results

def start_chrome(headless: bool=False) -> wd.Chrome:
    options: wd.ChromeOptions = wd.ChromeOptions()
    if headless: options.add_argument("--headless")
    user_agent = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64 "
    user_agent += "AppleWebKit/537.36 (KHTML, like Gecko) "
    user_agent += "Chrome/91.0.4472.124 Safari/537.36"
    options.add_argument(user_agent)
    options.add_argument("--disable-extensions")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--incognito")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    prefs: dict[str, int] = {
        "profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    return wd.Chrome(options=options)

def uncalled_lambda_name(uncalled_lambda: Callable[..., Any]):
    return '.'.join(str(uncalled_lambda).split(' ')[1].split('.')[0:2])

def process_operations(
    browser: wd.Chrome,
    instruction: DataRecoveryInstruction) -> str:

    data = ''

    for operation in instruction.get_operations():
        if uncalled_lambda_name(operation) == 'Operation.join':
            data_parts = []

            elements: list[WebElement] = browser.find_elements(
                By.CSS_SELECTOR,
                instruction.get_css_selector())

            for i in elements:
                if i.text.strip():
                    data_parts.append(i.text.strip())

            data = operation(data_parts)

    return data

def recover_data(
    browser: wd.Chrome, instruction: DataRecoveryInstruction) -> str:

    element: WebElement|None = browser.find_element(
        By.CSS_SELECTOR, instruction.get_css_selector())

    if element and element.text.strip():
        return element.text.strip()

    return ''

def try_to_recover_data(
    browser: wd.Chrome,
    data_recovery_instruction: DataRecoveryInstruction) -> str:
    data: str = ''
    instruction = data_recovery_instruction

    try:
        if instruction.get_operations():
            data = process_operations(browser, instruction)
        else:
            data = recover_data(browser, instruction)

        if not data:
            return ''

        for change in instruction.get_changes():
            data = change(data)

    finally:
        return data

if __name__ == "__main__":
    main()
