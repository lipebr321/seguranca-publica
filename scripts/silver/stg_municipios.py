import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"
engine = create_engine(DATABASE_URL)

def main():
    query = text("""
        SELECT
            municipio,
            cidade,
            bairro,
            delegacia,
            delegacia_circ,
            latitude,
            longitude,
            COUNT(*) AS total_ocorrencias
        FROM stg.stg_ocorrencias
        WHERE municipio IS NOT NULL
        GROUP BY
            municipio,
            cidade,
            bairro,
            delegacia,
            delegacia_circ,
            latitude,
            longitude
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    df["municipio"] = df["municipio"].str.strip().str.upper()
    df["cidade"] = df["cidade"].str.strip().str.upper()
    df["bairro"] = df["bairro"].str.strip().str.upper()
    df["delegacia"] = df["delegacia"].str.strip().str.upper()
    df["delegacia_circ"] = df["delegacia_circ"].str.strip().str.upper()

    df = df.drop_duplicates()

    df.to_sql(
        "stg_municipios",
        engine,
        schema="stg",
        if_exists="replace",
        index=False,
        chunksize=10000,
        method="multi"
    )

    print("Tabela criada: stg.stg_municipios")
    print(f"Linhas: {len(df)}")

if __name__ == "__main__":
    main()