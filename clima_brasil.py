from result_set import ResultSet
from result_sets_printer import ResultSetsPrinter
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from typing import Dict, List

import numpy as np
import re
import sys
import time as t
import utils as ut
from zoneinfo import ZoneInfo

class Operation:
    def join(separator):
        return lambda data: separator.join(data)

class Change:
    def append(suffix):
        return lambda data: data + suffix

    def replace(old, new):
        return lambda data: data.replace(old, new)

def main() -> None:
    inputs: List[str] = sys.argv
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

        data_recovery_instructions: List[Dict] = [
            {
                'title': 'Comparação',
                'css_selector': '.today-forecast-card__intro',
                'operations': [
                    Operation.join(' '),
                ],
                'changes': [
                    Change.append('.'),
                ],
            },
            {
                'title': 'Descrição',
                'css_selector': '.today-forecast-card__desc',
            },
            {
                'title': 'Temperatura mínima',
                'css_selector': climatempo_common_css_selector(
                    'temperature', 'cool'),
                'changes': [
                    Change.append('C'),
                ],
            },
            {
                'title': 'Temperatura máxima',
                'css_selector': climatempo_common_css_selector(
                    'temperature', 'warm'),
                'changes': [
                    Change.append('C'),
                ],
            },
            {
                'title': 'Sensação térmica mínima',
                'css_selector': climatempo_common_css_selector(
                    'thermal', 'cool'),
                'changes': [
                    Change.append('C'),
                ],
            },
            {
                'title': 'Sensação térmica máxima',
                'css_selector': climatempo_common_css_selector(
                    'thermal', 'warm'),
                'changes': [
                    Change.append('C'),
                ],
            },
            {
                'title': 'Pluviosidade',
                'css_selector': climatempo_common_css_selector(
                    'rain'),
                'changes': [
                    Change.replace('.', ','),
                ],
            },
            {
                'title': 'Humidade mínima',
                'css_selector': climatempo_common_css_selector(
                    'humidity', 'cool'),
            },
            {
                'title': 'Humidade máxima',
                'css_selector': climatempo_common_css_selector(
                    'humidity', 'warm'),
            },
            {
                'title': 'Horário sol',
                'css_selector': climatempo_common_css_selector(
                    'sun'),
            },
            {
                'title': 'Vento',
                'css_selector': climatempo_common_css_selector(
                    'wind'),
            },
            {
                'title': 'Rajada de vento',
                'css_selector': climatempo_common_css_selector(
                    'gust'),
            },
            {
                'title': 'Arco íris',
                'css_selector': climatempo_common_css_selector(
                    'rainbow'),
                'changes': [
                    Change.replace('probabilid.', 'probabilidade'),
                ],
            },
        ]

        for i in data_recovery_instructions:
            data = try_to_recover_data(browser, i)
            if data:
                results.add_key_value(i['title'], data)

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
    prefs: Dict[str, int] = {
        "profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    return wd.Chrome(options=options)

def climatempo_common_css_selector(data_id:str, variant:str=''):
    common_source_1: str = '.daily-variables-grid__item.-'
    common_source_2: str = ' .daily-variables-grid__value'
    variant_prefix: str = '.-'

    base_css_selector: str = common_source_1 + data_id + common_source_2

    if not variant:
        return base_css_selector

    return base_css_selector + variant_prefix + variant

def class_method_name(class_method):
    result = '.'.join(str(class_method) \
        .replace('<function ', '') \
        .split('.')[0:2])

    return result

def try_to_recover_data(
    browser: wd.Chrome, data_recovery_instruction: Dict) -> str:

    data = ''

    try:
        if 'operations' in data_recovery_instruction:
            for operation in data_recovery_instruction['operations']:
                if class_method_name(operation) == 'Operation.join':
                    data_parts = []

                    elements: List[WebElement]|None = browser.find_elements(
                        By.CSS_SELECTOR,
                        data_recovery_instruction['css_selector'])

                    for i in elements:
                        if i.text.strip():
                            data_parts.append(i.text.strip())

                    data = operation(data_parts)
        else:
            element: WebElement|None = \
                browser.find_element(
                    By.CSS_SELECTOR,
                    data_recovery_instruction['css_selector'])
            if element and element.text.strip():
                data = element.text.strip()

        if not data:
            return ''

        for change in data_recovery_instruction.get('changes', []):
            data = change(data)

    finally:
        return data

if __name__ == "__main__":
    main()
