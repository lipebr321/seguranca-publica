import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"
engine = create_engine(DATABASE_URL)

def main():
    query = text("""
        SELECT
            fonte,
            ano,
            mes,
            municipio,
            cidade,
            bairro,
            delegacia_circ,
            tipo_local,
            ROUND(AVG(latitude)::numeric, 6) AS latitude_media,
            ROUND(AVG(longitude)::numeric, 6) AS longitude_media,
            COUNT(*) AS total_ocorrencias,
            SUM(quantidade) AS total_bens_subtraidos
        FROM stg.stg_ocorrencias
        WHERE ano IS NOT NULL
        GROUP BY
            fonte,
            ano,
            mes,
            municipio,
            cidade,
            bairro,
            delegacia_circ,
            tipo_local
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    df["nivel_risco"] = pd.cut(
        df["total_ocorrencias"],
        bins=[0, 10, 50, 100, 500, float("inf")],
        labels=["BAIXO", "MODERADO", "ALTO", "CRITICO", "EXTREMO"]
    )

    df.to_sql(
        "stg_hotspots",
        engine,
        schema="stg",
        if_exists="replace",
        index=False,
        chunksize=10000,
        method="multi"
    )

    print("Tabela criada: stg.stg_hotspots")
    print(f"Linhas: {len(df)}")

if __name__ == "__main__":
    main()