import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)


def limpar(valor):

    if pd.isna(valor):
        return "IGNORADO"

    valor = str(valor).strip().upper()

    if valor == "":
        return "IGNORADO"

    return valor


def main():

    query = text("""
        SELECT
            fonte,
            tipo_bem,
            subtipo_bem,
            marca_bem,
            quantidade
        FROM stg.stg_ocorrencias
        WHERE tipo_bem IS NOT NULL
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    df["fonte"] = df["fonte"].apply(limpar)
    df["tipo_bem"] = df["tipo_bem"].apply(limpar)
    df["subtipo_bem"] = df["subtipo_bem"].apply(limpar)
    df["marca_bem"] = df["marca_bem"].apply(limpar)

    agg = (
        df.groupby(
            [
                "fonte",
                "tipo_bem",
                "subtipo_bem",
                "marca_bem"
            ],
            dropna=False
        )
        .agg(
            total_ocorrencias=("tipo_bem", "count"),
            total_quantidade=("quantidade", "sum")
        )
        .reset_index()
    )

    agg["id_bem"] = (
        "BEM_"
        + (agg.index + 1).astype(str)
    )

    agg = agg[
        [
            "id_bem",
            "fonte",
            "tipo_bem",
            "subtipo_bem",
            "marca_bem",
            "total_ocorrencias",
            "total_quantidade"
        ]
    ]

    agg = agg.sort_values(
        by="total_ocorrencias",
        ascending=False
    )

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE SCHEMA IF NOT EXISTS stg;
        """))

    agg.to_sql(
        "stg_bens",
        engine,
        schema="stg",
        if_exists="replace",
        index=False,
        chunksize=10000,
        method="multi"
    )

    print("\nTabela criada: stg.stg_bens")
    print(f"Linhas: {len(agg)}")


if __name__ == "__main__":
    main()