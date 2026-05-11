import re
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, inspect

PARQUET_DIR = Path("data/parquet")

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)

def nome_tabela(nome):
    nome = nome.lower()
    nome = re.sub(r"[^a-z0-9_]", "_", nome)
    return nome

inspector = inspect(engine)
tabelas_existentes = set(inspector.get_table_names())

print(f"Tabelas existentes no PostgreSQL: {len(tabelas_existentes)}")

for arquivo in sorted(PARQUET_DIR.glob("*.parquet")):

    tabela = nome_tabela(arquivo.stem)

    print("\n==============================")
    print(f"Arquivo: {arquivo.name}")
    print(f"Tabela: {tabela}")

    if tabela in tabelas_existentes:
        print("Já existe no PostgreSQL. Pulando.")
        continue

    try:
        df = pd.read_parquet(arquivo)

        print(f"Linhas: {len(df)}")
        print(f"Colunas: {len(df.columns)}")

        df.to_sql(
            tabela,
            engine,
            if_exists="fail",
            index=False,
            chunksize=10000,
            method="multi"
        )

        print("Carregado no PostgreSQL.")

    except Exception as e:
        print(f"Erro ao carregar {arquivo.name}")
        print(e)

print("\nCarga finalizada.")