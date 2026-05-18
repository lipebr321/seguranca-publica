import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)

MESES = {
    1: "JANEIRO",
    2: "FEVEREIRO",
    3: "MARÇO",
    4: "ABRIL",
    5: "MAIO",
    6: "JUNHO",
    7: "JULHO",
    8: "AGOSTO",
    9: "SETEMBRO",
    10: "OUTUBRO",
    11: "NOVEMBRO",
    12: "DEZEMBRO"
}

DIAS = {
    0: "SEGUNDA",
    1: "TERÇA",
    2: "QUARTA",
    3: "QUINTA",
    4: "SEXTA",
    5: "SÁBADO",
    6: "DOMINGO"
}

def criar_dimensao_tempo():

    datas = pd.date_range(
        start="2017-01-01",
        end="2030-12-31",
        freq="D"
    )

    df = pd.DataFrame()

    df["data"] = datas

    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["dia"] = df["data"].dt.day

    df["nome_mes"] = df["mes"].map(MESES)

    df["trimestre"] = df["data"].dt.quarter

    df["semestre"] = df["mes"].apply(
        lambda x: 1 if x <= 6 else 2
    )

    df["dia_semana"] = df["data"].dt.weekday

    df["nome_dia_semana"] = df["dia_semana"].map(DIAS)

    df["fim_semana"] = df["dia_semana"].isin([5, 6])

    df["ano_mes"] = (
        df["ano"].astype(str)
        + "-"
        + df["mes"].astype(str).str.zfill(2)
    )

    return df

def main():

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE SCHEMA IF NOT EXISTS stg;
        """))

    df = criar_dimensao_tempo()

    print(df.head())

    df.to_sql(
        "stg_tempo",
        engine,
        schema="stg",
        if_exists="replace",
        index=False,
        chunksize=10000,
        method="multi"
    )

    print("\nTabela criada: stg.stg_tempo")

if __name__ == "__main__":
    main()