import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)


def classificar_periodo(hora):

    if pd.isna(hora):
        return "IGNORADO"

    try:

        hora = str(hora).strip()

        if ":" in hora:
            h = int(hora.split(":")[0])

        else:
            h = int(float(hora))

    except:
        return "IGNORADO"

    if 0 <= h <= 5:
        return "MADRUGADA"

    elif 6 <= h <= 11:
        return "MANHÃ"

    elif 12 <= h <= 17:
        return "TARDE"

    elif 18 <= h <= 23:
        return "NOITE"

    return "IGNORADO"


def main():

    query = text("""
        SELECT DISTINCT
            hora_ocorrencia
        FROM stg.stg_ocorrencias
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    df["periodo"] = df["hora_ocorrencia"].apply(
        classificar_periodo
    )

    df["hora"] = (
        df["hora_ocorrencia"]
        .astype(str)
        .str.extract(r'(\d{1,2})')[0]
    )

    df["hora"] = pd.to_numeric(
        df["hora"],
        errors="coerce"
    )

    df = df[
        [
            "hora_ocorrencia",
            "hora",
            "periodo"
        ]
    ]

    df = df.drop_duplicates()

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE SCHEMA IF NOT EXISTS stg;
        """))

    df.to_sql(
        "stg_periodo",
        engine,
        schema="stg",
        if_exists="replace",
        index=False,
        chunksize=10000,
        method="multi"
    )

    print("\nTabela criada: stg.stg_periodo")
    print(f"Linhas: {len(df)}")


if __name__ == "__main__":
    main()