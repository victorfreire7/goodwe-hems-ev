"""Extrai da base de tarifas homologadas da ANEEL a tarifa branca residencial (B1)
da Enel SP na vigencia mais recente.

Entrada: tarifas-homologadas-distribuidoras-energia-eletrica.csv (raiz do projeto)
Saida:   tarifa_enel_sp_branca.csv (raiz do projeto) e um resumo no terminal

Uso: python scripts/extrair_tarifa_enel_sp.py
"""
import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "tarifas-homologadas-distribuidoras-energia-eletrica.csv"
SAIDA = RAIZ / "tarifa_enel_sp_branca.csv"
CNPJ_ENEL_SP = "61695227000193"


def numero(texto):
    """Converte valores com virgula decimal ('1,85' ou ',00') em float."""
    return float(texto.replace(",", ".") or 0)


with open(ENTRADA, encoding="utf-8-sig", newline="") as arquivo:
    linhas = [
        linha
        for linha in csv.DictReader(arquivo, delimiter=";")
        if linha["NumCNPJDistribuidora"] == CNPJ_ENEL_SP
        and linha["DscModalidadeTarifaria"] == "Branca"
        and linha["DscSubGrupo"] == "B1"
        and linha["DscClasse"] == "Residencial"
        and linha["DscBaseTarifaria"] == "Tarifa de Aplicação"
    ]

if not linhas:
    raise SystemExit("Nenhuma linha encontrada. Confira o CNPJ e os filtros.")

vigencia = max(linha["DatInicioVigencia"] for linha in linhas)
recentes = [linha for linha in linhas if linha["DatInicioVigencia"] == vigencia]

print(f"Linhas Enel SP, Branca, B1, Residencial: {len(linhas)}")
print(f"Sigla do agente no arquivo: {sorted({l['SigAgente'] for l in recentes})}")
print(f"Vigencia mais recente: {vigencia} a {recentes[0]['DatFimVigencia']}")
print(f"Resolucao: {recentes[0]['DscREH']}")
print()

colunas = [
    "SigAgente", "DatInicioVigencia", "DatFimVigencia", "DscSubClasse",
    "DscDetalhe", "NomPostoTarifario", "unidade", "TUSD", "TE",
    "TUSD_mais_TE", "TUSD_mais_TE_R$_por_kWh",
]
with open(SAIDA, "w", encoding="utf-8", newline="") as saida:
    escritor = csv.writer(saida, delimiter=";")
    escritor.writerow(colunas)
    for linha in recentes:
        tusd = numero(linha["VlrTUSD"])
        te = numero(linha["VlrTE"])
        unidade = linha["DscUnidadeTerciaria"]
        total = tusd + te
        por_kwh = f"{total / 1000:.4f}" if "MWh" in unidade else ""
        escritor.writerow([
            linha["SigAgente"], linha["DatInicioVigencia"], linha["DatFimVigencia"],
            linha["DscSubClasse"], linha["DscDetalhe"], linha["NomPostoTarifario"],
            unidade, tusd, te, f"{total:.2f}", por_kwh,
        ])
        print(
            f"{linha['NomPostoTarifario']:<14} {linha['DscSubClasse']:<14} "
            f"{linha['DscDetalhe']:<14} {unidade:<6} TUSD={tusd:>9.2f} "
            f"TE={te:>9.2f} total={total:>9.2f} ({por_kwh} R$/kWh)"
        )

print(f"\nArquivo gerado: {SAIDA}")
