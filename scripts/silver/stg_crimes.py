import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)


def classificar_categoria(rubrica):

    if rubrica is None:
        return "OUTROS"

    rubrica = str(rubrica).upper()

    if "ROUBO" in rubrica:
        return "ROUBO"

    if "FURTO" in rubrica:
        return "FURTO"

    if "HOMIC" in rubrica:
        return "HOMICIDIO"

    if "ESTUPRO" in rubrica:
        return "VIOLENCIA_SEXUAL"

    if "TRAFICO" in rubrica:
        return "TRAFICO"

    return "OUTROS"


def classificar_macro_categoria(categoria):

    mapa = {
        "ROUBO": "PATRIMONIAL",
        "FURTO": "PATRIMONIAL",
        "HOMICIDIO": "VIOLENTO",
        "VIOLENCIA_SEXUAL": "VIOLENTO",
        "TRAFICO": "NARCOTRAFICO",
        "OUTROS": "OUTROS"
    }

    return mapa.get(categoria, "OUTROS")


def main():

    query = text("""
        SELECT DISTINCT
            rubrica,
            conduta,
            tipo_bem,
            subtipo_bem,
            marca_bem
        FROM stg.stg_ocorrencias
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    df["categoria_crime"] = df["rubrica"].apply(
        classificar_categoria
    )

    df["macro_categoria"] = df["categoria_crime"].apply(
        classificar_macro_categoria
    )

    df["id_crime"] = (
        df["categoria_crime"].astype(str)
        + "_"
        + df.index.astype(str)
    )

    df = df[
        [
            "id_crime",
            "rubrica",
            "conduta",
            "categoria_crime",
            "macro_categoria",
            "tipo_bem",
            "subtipo_bem",
            "marca_bem"
        ]
    ]

    df = df.drop_duplicates()

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE SCHEMA IF NOT EXISTS stg;
        """))

    df.to_sql(
        "stg_crimes",
        engine,
        schema="stg",
        if_exists="replace",
        index=False,
        chunksize=10000,
        method="multi"
    )

    print("\nTabela criada: stg.stg_crimes")
    print(f"Linhas: {len(df)}")


if __name__ == "__main__":
    main()