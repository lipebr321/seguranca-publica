import pandas as pd
from pathlib import Path
from datetime import datetime

ORIGEM = Path("data/raw/xlsx")
DESTINO = Path("data/parquet")
LOG_DIR = Path("data/logs")

DESTINO.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_path = LOG_DIR / "conversao_parquet.log"

def limpar_colunas(df):
    df.columns = [
        str(col)
        .strip()
        .upper()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "_")
        for col in df.columns
    ]
    return df

def converter_tudo_para_texto(df):
    for col in df.columns:
        df[col] = df[col].astype("string")
    return df.fillna("")

with open(log_path, "a", encoding="utf-8") as log:

    log.write(f"\n\n===== EXECUÇÃO {datetime.now()} =====\n")

    for arquivo in sorted(ORIGEM.glob("*.xlsx")):

        nome_saida = arquivo.stem + ".parquet"
        caminho_saida = DESTINO / nome_saida

        print("\n==============================")
        print(f"Arquivo: {arquivo.name}")

        if caminho_saida.exists():
            print(f"Já convertido, pulando: {caminho_saida}")
            log.write(f"PULADO: {arquivo.name}\n")
            continue

        try:
            print("Lendo XLSX...")

            df = pd.read_excel(
                arquivo,
                engine="openpyxl",
                dtype=object
            )

            df = limpar_colunas(df)
            df = converter_tudo_para_texto(df)

            print(f"Linhas: {len(df)}")
            print(f"Colunas: {len(df.columns)}")

            df.to_parquet(
                caminho_saida,
                engine="pyarrow",
                compression="snappy",
                index=False
            )

            print(f"Parquet salvo: {caminho_saida}")
            log.write(f"OK: {arquivo.name} -> {nome_saida}\n")

        except Exception as e:
            print(f"Erro em {arquivo.name}")
            print(e)
            log.write(f"ERRO: {arquivo.name} -> {e}\n")

print("\n===================================")
print("CONVERSÃO FINALIZADA")
print(f"Log salvo em: {log_path}")