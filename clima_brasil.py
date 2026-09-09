from result_set import ResultSet
from result_sets_printer import ResultSetsPrinter
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from typing import Any, Dict, List

import numpy as np
import re
import sys
import time as t
import utils as ut
from zoneinfo import ZoneInfo

def main() -> None:
    inputs: List[str] = sys.argv
    if len(inputs) < 3:
        print("ERRO: é necessário digitar cidade e estado.")
        print_examples()
        return
    elif len(inputs) > 4:
        print("ERRO: digite apenas cidade e estado; coloque aspas simples ou")
        print("  duplas  se o nome da cidade possuir mais de uma palavra ou")
        print(r"    utilize  a barra invertida (\) para cancelar um espaço ")
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
        { "acronym": "TO", "name": "Tocantins" }], dtype=np.object_)

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

    browser: wd.Chrome = start_chrome(headless)
    browser.get("https://www.duckduckgo.com")

    browser.find_element(By.CSS_SELECTOR, 'textarea[data-mode="search"]') \
        .send_keys(
            f"climatempo previsao-do-tempo {cidade} {estado} brasil",
            Keys.ENTER)

    browser.find_element(
        By.CSS_SELECTOR, 'article h2 a[href*="previsao-do-tempo/cidade"]'
    ).click()

    t.sleep(1)
    browser.implicitly_wait(1)

    provider: str = "ClimaTempo"

    title: str = "Previsão do tempo em "
    title += f"{ut.capitalize_all(cidade)}/{estado.upper()}, Brasil"

    results: ResultSet = ResultSet(provider=provider, title=title)

    try:
        comparacao_elements: List[WebElement]|None = browser.find_elements(
            By.CSS_SELECTOR, '.today-forecast-card__intro')
        comparacao_texts: List[str] = []

        if len(comparacao_elements) > 0:
            for i in comparacao_elements:
                comparacao_texts.append(i.text)
            results.add_key_value(
                'Comparação',
                (" ".join(comparacao_texts) + '.'))

        descricao_text: str = try_to_grab_element_text(
            browser,
            '.today-forecast-card__desc')
        if descricao_text:
            results.add_key_value('Descrição', descricao_text)

        temperaturas: List[Dict[str, str]] = [
            {
                'title': 'Temperatura mínima',
                'css': '.daily-variables-grid__item.-temperature .daily-variables-grid__value.-cool',
            },
            {
                'title': 'Temperatura máxima',
                'css': '.daily-variables-grid__item.-temperature .daily-variables-grid__value.-warm',
            },
            {
                'title': 'Sensação térmica mínima',
                'css': '.daily-variables-grid__item.-thermal .daily-variables-grid__value.-cool',
            },
            {
                'title': 'Sensação térmica máxima',
                'css': '.daily-variables-grid__item.-thermal .daily-variables-grid__value.-warm',
            },
        ]

        for i in temperaturas:
            data = try_to_grab_element_text_and_fix_temperature(browser, i['css'], 'C')
            if data:
                results.add_key_value(i['title'], data)

        demais_dados: List[Dict[str, str]] = [
            {
                'title': 'Pluviosidade',
                'css': '.daily-variables-grid__item.-rain .daily-variables-grid__value',
            },
            {
                'title': 'Humidade mínima',
                'css': '.daily-variables-grid__item.-humidity .daily-variables-grid__value.-cool',
            },
            {
                'title': 'Humidade máxima',
                'css': '.daily-variables-grid__item.-humidity .daily-variables-grid__value.-warm',
            },
            {
                'title': 'Horário sol',
                'css': '.daily-variables-grid__item.-sun .daily-variables-grid__value',
            },
            {
                'title': 'Vento',
                'css': '.daily-variables-grid__item.-wind .daily-variables-grid__value',
            },
            {
                'title': 'Rajada de vento',
                'css': '.daily-variables-grid__item.-gust .daily-variables-grid__value',
            },
            {
                'title': 'Arco íris',
                'css': '.daily-variables-grid__item.-rainbow .daily-variables-grid__value',
            },
        ]

        for i in demais_dados:
            data = try_to_grab_element_text(browser, i['css'])
            if data:
                results.add_key_value(i['title'], data)

    except:
        return ResultSet()
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

def try_to_grab_element_text(browser: wd.Chrome, css_selector: str) -> str:
    element: WebElement|None = \
        browser.find_element(By.CSS_SELECTOR, css_selector)

    if element:
        return element.text

    return ''

def try_to_grab_element_text_and_fix_temperature(
    browser: wd.Chrome, css_selector: str, fix: str) -> str:

    text = try_to_grab_element_text(browser, css_selector)

    if text:
        return text + fix

    return ''

if __name__ == "__main__":
    main()
