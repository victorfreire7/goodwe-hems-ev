"""Prepara o perfil de radiacao solar de Sao Paulo com os dados horarios do INMET.

Entrada: arquivos da estacao A701 (Sao Paulo - Mirante de Santana) em
         dados/brutos/inmet/. Aceita os .CSV ou os .zip anuais baixados em
         https://portal.inmet.gov.br/dadoshistoricos
Saidas (em dados/processados/):
  perfil_solar_sp.csv        irradiancia media de cada hora, em kW/m2, no horario local (UTC-3)
  dias_sp_classificados.csv  irradiacao diaria em kWh/m2 e classe de cada dia

Uso: python scripts/preparar_geracao_inmet.py
"""
import csv
import io
import re
import unicodedata
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "dados" / "brutos" / "inmet"
SAIDA = RAIZ / "dados" / "processados"
ESTACAO = "A701"
UTC_PARA_LOCAL = timedelta(hours=-3)  # UTC-3; o Brasil nao usa horario de verao desde 2019
HORA_SOL_INICIO = 6  # horas do dia (local) em que ha sol; fora delas a radiacao e zero
HORA_SOL_FIM = 18
HORAS_SOL_MINIMAS = 11  # de 12 horas de sol, o minimo com medicao para o dia ser valido
LIMITE_ENSOLARADO = 0.75  # fracao da irradiacao diaria do percentil 90 dos dias validos
LIMITE_PARCIAL = 0.35
DIAS_DE_HISTORICO = 7


def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().upper()


def numero(texto):
    texto = texto.strip().replace(",", ".")
    try:
        valor = float(texto)
    except ValueError:
        return None
    return None if valor <= -9990 else valor


def interpretar_data(texto):
    for formato in ("%Y/%m/%d", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto.strip(), formato)
        except ValueError:
            continue
    return None


def listar_arquivos():
    """Gera (nome, linhas) para cada arquivo da estacao."""
    for caminho in sorted(ENTRADA.rglob("*")):
        sufixo = caminho.suffix.lower()
        if sufixo == ".zip":
            with zipfile.ZipFile(caminho) as pacote:
                for nome in pacote.namelist():
                    if ESTACAO in nome.upper() and nome.upper().endswith(".CSV"):
                        texto = io.TextIOWrapper(pacote.open(nome), encoding="latin-1").read()
                        yield nome, texto.splitlines()
        elif sufixo == ".csv" and ESTACAO in caminho.name.upper():
            yield caminho.name, caminho.read_text(encoding="latin-1").splitlines()


def ler_radiacao(nome, linhas):
    """Devolve {horario_local: irradiancia media da hora em kW/m2} de um arquivo."""
    for posicao, linha in enumerate(linhas):
        texto = normalizar(linha)
        if texto.lstrip('"').startswith("DATA") and "RADIACAO" in texto:
            break
    else:
        raise SystemExit(f"{nome}: cabecalho com coluna de radiacao nao encontrado.")

    colunas = next(csv.reader([linhas[posicao]], delimiter=";"))
    indice = next(i for i, c in enumerate(colunas) if "RADIACAO" in normalizar(c))
    em_kj = "KJ" in normalizar(colunas[indice])

    valores = {}
    for campos in csv.reader(linhas[posicao + 1:], delimiter=";"):
        if len(campos) <= indice:
            continue
        data = interpretar_data(campos[0])
        digitos = re.sub(r"\D", "", campos[1])
        valor = numero(campos[indice])
        if data is None or not digitos or valor is None:
            continue
        digitos = digitos.zfill(4)[:4]
        utc = data + timedelta(hours=int(digitos[:2]), minutes=int(digitos[2:]))
        # kJ/m2 acumulados em 1 hora: dividir por 3600 da kW/m2 medio da hora
        irradiancia = max(valor, 0.0) / (3600 if em_kj else 1000)
        valores[utc + UTC_PARA_LOCAL] = irradiancia
    return valores


def main():
    horario = {}
    arquivos = 0
    for nome, linhas in listar_arquivos():
        horario.update(ler_radiacao(nome, linhas))
        arquivos += 1
    if not horario:
        raise SystemExit(f"Nenhum arquivo da estacao {ESTACAO} encontrado em {ENTRADA}.")

    pico = max(horario.values())
    print(f"Arquivos lidos: {arquivos}")
    print(f"Registros horarios: {len(horario)} ({min(horario):%Y-%m-%d} a {max(horario):%Y-%m-%d})")
    print(f"Maior irradiancia horaria: {pico:.3f} kW/m2")
    if pico > 1.5:
        print("ATENCAO: valor acima de 1,5 kW/m2; confira a unidade da coluna de radiacao.")

    # A noite o INMET nao registra radiacao: a hora sem medicao fora do periodo de sol vale zero.
    por_dia = {}
    for momento, valor in horario.items():
        if HORA_SOL_INICIO <= momento.hour < HORA_SOL_FIM:
            soma, horas = por_dia.get(momento.date(), (0.0, 0))
            por_dia[momento.date()] = (soma + valor, horas + 1)
    validos = {d: v for d, v in por_dia.items() if v[1] >= HORAS_SOL_MINIMAS}
    if not validos:
        raise SystemExit("Nenhum dia com horas validas suficientes.")

    somas = sorted(soma for soma, _ in validos.values())
    referencia = somas[int(0.9 * (len(somas) - 1))]

    def classe(soma):
        razao = soma / referencia
        if razao >= LIMITE_ENSOLARADO:
            return "ensolarado"
        if razao >= LIMITE_PARCIAL:
            return "parcialmente nublado"
        return "chuvoso"

    SAIDA.mkdir(parents=True, exist_ok=True)
    with open(SAIDA / "perfil_solar_sp.csv", "w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, delimiter=";")
        escritor.writerow(["timestamp_local", "irradiancia_kw_m2"])
        for momento in sorted(horario):
            escritor.writerow([f"{momento:%Y-%m-%dT%H:%M:%S}-03:00", f"{horario[momento]:.5f}"])

    with open(SAIDA / "dias_sp_classificados.csv", "w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, delimiter=";")
        escritor.writerow(["data", "irradiacao_kwh_m2", "horas_validas", "razao_p90", "classe"])
        for dia in sorted(validos):
            soma, horas = validos[dia]
            escritor.writerow([dia.isoformat(), f"{soma:.3f}", horas, f"{soma / referencia:.2f}", classe(soma)])

    candidatos = {}
    for dia in sorted(validos, reverse=True):
        anteriores = [dia - timedelta(days=i) for i in range(1, DIAS_DE_HISTORICO + 1)]
        if all(a in validos for a in anteriores):
            candidatos.setdefault(classe(validos[dia][0]), []).append(dia)

    print(f"\nDias validos: {len(validos)} (referencia p90: {referencia:.2f} kWh/m2 por dia)")
    contagem = {}
    for soma, _ in validos.values():
        contagem[classe(soma)] = contagem.get(classe(soma), 0) + 1
    for nome_classe, quantidade in sorted(contagem.items()):
        print(f"  {nome_classe}: {quantidade} dias")
    print(f"\nDias mais recentes com {DIAS_DE_HISTORICO} dias validos antes (historico para a previsao):")
    for nome_classe, dias in sorted(candidatos.items()):
        lista = ", ".join(d.isoformat() for d in dias[:5])
        print(f"  {nome_classe}: {lista}")
    print(f"\nArquivos gerados em {SAIDA}")


if __name__ == "__main__":
    main()
