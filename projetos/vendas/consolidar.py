"""Demonstração de portfólio. Python 3.10+, sem dependências externas."""
import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

CAMPOS = ["id_venda", "data", "produto", "quantidade", "preco_unitario"]

def gravar(path, campos, linhas):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos, delimiter=";")
        writer.writeheader()
        writer.writerows(linhas)

def executar(entrada, saida):
    arquivos = sorted(entrada.glob("*.csv"))
    if not arquivos:
        raise ValueError("Nenhum CSV encontrado na pasta de entrada.")
    if entrada.resolve() == saida.resolve():
        raise ValueError("Use pastas diferentes para entrada e saída.")
    saida.mkdir(parents=True, exist_ok=True)
    vendas, rejeitados, duplicados = {}, [], []
    lidas = 0
    for arquivo in arquivos:
        with arquivo.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            if reader.fieldnames != CAMPOS:
                raise ValueError(f"Cabeçalho inesperado: {arquivo.name}")
            for numero, raw in enumerate(reader, 2):
                lidas += 1
                origem = dict(arquivo=arquivo.name, linha=numero)
                try:
                    row = {k: (raw[k] or "").strip() for k in CAMPOS}
                    if not row["id_venda"] or not row["produto"]:
                        raise ValueError("ID ou produto vazio")
                    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
                        try:
                            data = datetime.strptime(row["data"], formato).date()
                            break
                        except ValueError:
                            pass
                    else:
                        raise ValueError("Data inválida")
                    qtd = int(row["quantidade"])
                    preco = Decimal(row["preco_unitario"].replace(",", "."))
                    if qtd <= 0 or not preco.is_finite() or preco < 0:
                        raise ValueError("Quantidade ou preço inválido")
                    if preco != preco.quantize(Decimal("0.01")):
                        raise ValueError("Preço com mais de duas casas decimais")
                    normal = dict(id_venda=row["id_venda"], data=data.isoformat(),
                                  produto=row["produto"].title(), quantidade=qtd,
                                  preco_unitario=f"{preco:.2f}", total=f"{qtd * preco:.2f}")
                    chave = normal["id_venda"]
                    if chave in vendas:
                        if vendas[chave] != normal:
                            raise ValueError("ID repetido com dados divergentes; primeira ocorrência mantida")
                        duplicados.append({**origem, **raw})
                    else:
                        vendas[chave] = normal
                except (ValueError, InvalidOperation) as error:
                    rejeitados.append({**origem, **{k: raw.get(k) for k in CAMPOS}, "motivo": str(error)})
    linhas = sorted(vendas.values(), key=lambda x: (x["data"], x["id_venda"]))
    mensal, produtos = defaultdict(lambda: [0, 0, Decimal(0)]), defaultdict(lambda: [0, 0, Decimal(0)])
    for row in linhas:
        for grupo, chave in ((mensal, row["data"][:7]), (produtos, row["produto"])):
            grupo[chave][0] += 1
            grupo[chave][1] += row["quantidade"]
            grupo[chave][2] += Decimal(row["total"])
    gravar(saida / "vendas_consolidadas.csv", CAMPOS + ["total"], linhas)
    for nome, grupo, chave in (("resumo_mensal", mensal, "mes"), ("resumo_produtos", produtos, "produto")):
        gravar(saida / f"{nome}.csv", [chave, "vendas", "unidades", "faturamento"],
               [{chave: k, "vendas": v[0], "unidades": v[1], "faturamento": f"{v[2]:.2f}"} for k, v in sorted(grupo.items())])
    gravar(saida / "rejeitados.csv", ["arquivo", "linha"] + CAMPOS + ["motivo"], rejeitados)
    gravar(saida / "duplicados.csv", ["arquivo", "linha"] + CAMPOS, duplicados)
    auditoria = dict(arquivos=len(arquivos), linhas_lidas=lidas, vendas_validas=len(linhas),
                     duplicados=len(duplicados), rejeitados=len(rejeitados),
                     faturamento=f"{sum((Decimal(r['total']) for r in linhas), Decimal(0)):.2f}")
    assert lidas == len(linhas) + len(duplicados) + len(rejeitados)
    (saida / "auditoria.json").write_text(json.dumps(auditoria, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(auditoria, ensure_ascii=False, indent=2))
    return auditoria

if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=base / "entrada")
    parser.add_argument("--saida", type=Path, default=base / "saida")
    args = parser.parse_args()
    executar(args.entrada, args.saida)
