from result_set import ResultSet
from result_sets_printer import ResultSetsPrinter
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from typing import Any, Dict, List

import json
import numpy as np
import os
import re
import sys
import time as t
import utils as ut

def main() -> None:
    inputs: List[str] = sys.argv
    if len(inputs) < 3:
        print("ERRO: é necessário digitar cidade e estado.")
        print_examples()
        return
    elif len(inputs) > 4:
        print("ERRO: digite apenas cidade e estado; coloque aspas simples ou")
        print("  duplas  se o nome da cidade possuir mais de uma palavra ou")
        print("    utilize  a barra invertida (\) para cancelar um espaço ")
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
    cidade: str, estado: str, headless: bool=False) -> None:

    resultados_condicao_tempo: ResultSet = condicao_tempo_accuweather(
        cidade=cidade, estado=estado, headless=headless)

    resultados_previsao_tempo: ResultSet = previsao_tempo_climatempo(
        cidade=cidade, estado=estado, headless=headless)

    result_printer: ResultSetsPrinter = ResultSetsPrinter(
        margin=2, min_width=72)

    if resultados_condicao_tempo.get_num_of_results():
        result_printer.add_results(resultados_condicao_tempo)

    if resultados_previsao_tempo.get_num_of_results():
        result_printer.add_results(resultados_previsao_tempo)

    if result_printer.get_num_of_results():
        result_printer.print_all()
    else:
        print("ERRO: as informações estão indisponíveis. ", end="")
        print("Tente novamente mais tarde.")

def condicao_tempo_accuweather(
    cidade: str, estado: str, headless: bool=False) -> ResultSet:

    browser: wd.Chrome = start_chrome(headless)
    browser.get("https://www.duckduckgo.com")

    try:
        browser.find_element(
            By.CSS_SELECTOR, "input[type=text]").send_keys(
                f"accuweather pt br brazil weather {cidade} {estado}",
                    Keys.ENTER)

        url: str|None = browser.find_element(
            By.CSS_SELECTOR, "#r1-0 h2 a").get_attribute("href")

        browser.get(format_accuweather_url(url))
        t.sleep(1)
        browser.implicitly_wait(1)

        provider: str = "AccuWeather"
        title: str = "Condições meteorológicas em "
        title += f"{ut.capitalize_all(cidade)}/{estado.upper()}, Brasil"
        results: ResultSet = ResultSet(provider=provider, title=title)

        tempoAtualTitulo: str = browser.find_element(
            By.CSS_SELECTOR, ".current-weather-card h1").text

        tempoAtualValor: str = browser.find_element(
            By.CSS_SELECTOR,
                ".current-weather-card div.current-weather-info div.temp").text

        tempoAtualSensacaoValor: str = browser.find_element(
            By.CSS_SELECTOR, ".current-weather-card div.phrase").text

        tempoAtualExtraRealFeelData: np.ndarray[Any, np.dtype[np.str_]] = \
            np.char.splitlines([browser.find_element(
                By.CSS_SELECTOR,
                ".current-weather-card div.current-weather-extra").text])[0]

        detalhes: np.ndarray[Any, np.dtype[np.str_]] = np.char.splitlines(
            [browser.find_element(
                By.CSS_SELECTOR,
                ".current-weather-card .current-weather-details").text])[0]

        tempoAtualRealFeelTitulo: str = np.char.split(
            [tempoAtualExtraRealFeelData[0]])[0][0]

        tempoAtualRealFeelValor: str = np.char.split(
            [tempoAtualExtraRealFeelData[0]])[0][1]

        tempoAtualRealFeelShadeTitulo: str = ""
        tempoAtualRealFeelShadeValor: str = ""

        if len(tempoAtualExtraRealFeelData) == 2:
            rFShade: np.ndarray[Any, np.dtype[np.str_]] = \
                np.char.split([tempoAtualExtraRealFeelData[1]])[0]
            tempoAtualRealFeelShadeTitulo = f"{rFShade[0]} {rFShade[1]}"
            tempoAtualExtraRealFeelShadeValor = rFShade[2]

        results.add_key_value(
            tempoAtualTitulo,
            f"{tempoAtualValor} ({tempoAtualSensacaoValor})")

        results.add_key_value(
            tempoAtualRealFeelTitulo,
            f"{tempoAtualRealFeelValor}C")

        if tempoAtualRealFeelShadeTitulo \
            and tempoAtualRealFeelShadeValor:
            results.add_key_value(
                tempoAtualRealFeelShadeTitulo,
                f"{tempoAtualExtraRealFeelShadeValor}C")

        for i in range(len(detalhes)):
            if i % 2 == 0:
                results.add_key_value(f"{detalhes[i]}",
                    f'{detalhes[i+1].replace("° C", "°C")}')
    except:
        return ResultSet()
    finally:
        browser.quit()

    return results

def previsao_tempo_climatempo(
    cidade: str, estado: str, headless: bool=False) -> ResultSet:

    browser: wd.Chrome = start_chrome(headless)
    browser.get("https://www.duckduckgo.com")

    browser.find_element(
        By.CSS_SELECTOR, "input[type=text]").send_keys(
            f"climatempo {cidade} {estado} brasil", Keys.ENTER)

    browser.find_element(
        By.CSS_SELECTOR, "#r1-0 h2 a").click()

    t.sleep(1)
    browser.implicitly_wait(1)

    data = np.array([], dtype="S")

    provider: str = "ClimaTempo"
    title: str = "Previsão do tempo em "
    title += f"{ut.capitalize_all(cidade)}/{estado.upper()}, Brasil"
    results: ResultSet = ResultSet(provider=provider, title=title)

    tempMin: str = ""
    tempMax: str = ""
    previsao: str = ""
    nascerPorDoSol: str = ""

    try:
        data = np.char.splitlines([browser.find_element(
            By.CSS_SELECTOR,
            'div[class="card -no-top -no-bottom"]').text])[0]

        browser.quit()

        comparacao: str = data[0]
        previsao = data[1]
        tempMin = data[7]
        tempMax = data[8]
        precipitacao: str = data[10]
        umidadeMin: str = data[14]
        umidadeMax: str = data[15]
        nascerPorDoSol = ""

        for i in range(0, len(data)):
            if data[i] == "Sol":
                nascerPorDoSol = data[i+1].replace("h", "")

        results.add_key_value("Temperatura mínima", f"{tempMin}C")
        results.add_key_value("Temperatura máxima", f"{tempMax}C")
        results.add_key_value("Comparação", comparacao)
        results.add_key_value("Previsão", previsao)
        results.add_key_value("Precipitação", precipitacao)
        results.add_key_value("Humidade mínima", umidadeMin)
        results.add_key_value("Humidade máxima", umidadeMax)

        if nascerPorDoSol:
            results.add_key_value("Nascer/pôr do sol",
                nascerPorDoSol.replace(" ", " / "))

        return results
    except:
        pass

    try:
        data = ut.remove_empty_elements(np.char.splitlines(
            [browser.find_element(
                By.CSS_SELECTOR,
                "#first-block-of-days section").text])[0])
    except:
        return ResultSet()
    finally:
        browser.quit()

    tempMin = data[2]
    tempMax = data[3]
    pluviosidade: str = data[4]
    previsao = data[5]
    umidade: str = ""
    lua: str = ""
    nascerPorDoSol = ""

    for i in range(0, len(data)):
        if data[i] == "UMIDADE DO AR" and len(data) >= i+2:
            umidade = data[i+1]
        if data[i] == "SOL" and len(data) >= i+2:
            nascerPorDoSol = data[i+1]
        if data[i] == "LUA" and len(data) >= i+2:
            lua = data[i+1]

    results.add_key_value("Temperatura mínima", f"{tempMin}C")
    results.add_key_value("Temperatura máxima", f"{tempMax}C")
    results.add_key_value("Previsão", previsao)
    results.add_key_value("Pluviosidade", pluviosidade)
    if umidade:
        results.add_key_value("Umidade", umidade)
    if nascerPorDoSol:
        results.add_key_value(
            "Nascer/pôr do sol", nascerPorDoSol.replace("-", "/"))
    if lua:
        results.add_key_value("Lua", lua)

    return results

def start_chrome(headless: bool=False) -> wd.Chrome:
    options: wd.ChromeOptions = wd.ChromeOptions()
    headless and options.add_argument("--headless")
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

def format_accuweather_url(url: str|None) -> str:
    if url is None:
        return ""
    return url.replace("en", "pt").replace(
        "weather-forecast", "current-weather")

if __name__ == "__main__":
    main()
