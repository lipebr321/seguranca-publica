import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)


def main():

    query = text("""
        SELECT
            o.ano,
            o.mes,
            t.nome_mes,
            t.trimestre,
            t.semestre,
            t.fim_semana,

            o.fonte,
            o.municipio,
            o.cidade,
            o.bairro,
            o.delegacia_circ,

            o.rubrica,
            o.conduta,
            o.tipo_local,

            p.periodo,

            COUNT(*) AS total_ocorrencias,
            SUM(o.quantidade) AS total_bens_subtraidos,
            COUNT(DISTINCT o.tabela_origem) AS qtd_fontes_origem,
            COUNT(DISTINCT o.delegacia_circ) AS qtd_delegacias,
            COUNT(DISTINCT o.bairro) AS qtd_bairros,

            AVG(o.latitude) AS latitude_media,
            AVG(o.longitude) AS longitude_media

        FROM stg.stg_ocorrencias o

        LEFT JOIN stg.stg_tempo t
            ON o.data_ocorrencia = t.data

        LEFT JOIN stg.stg_periodo p
            ON o.hora_ocorrencia = p.hora_ocorrencia

        WHERE o.ano IS NOT NULL

        GROUP BY
            o.ano,
            o.mes,
            t.nome_mes,
            t.trimestre,
            t.semestre,
            t.fim_semana,
            o.fonte,
            o.municipio,
            o.cidade,
            o.bairro,
            o.delegacia_circ,
            o.rubrica,
            o.conduta,
            o.tipo_local,
            p.periodo
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    df["ticket_medio_bens_por_ocorrencia"] = (
        df["total_bens_subtraidos"] / df["total_ocorrencias"]
    )

    df["nivel_volume"] = pd.cut(
        df["total_ocorrencias"],
        bins=[0, 10, 50, 100, 500, float("inf")],
        labels=["BAIXO", "MODERADO", "ALTO", "CRITICO", "EXTREMO"]
    )

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS dm;"))

    df.to_sql(
        "ocorrencias_dm",
        engine,
        schema="dm",
        if_exists="replace",
        index=False,
        chunksize=10000,
        method="multi"
    )

    print("Tabela criada: dm.ocorrencias_dm")
    print(f"Linhas: {len(df)}")


if __name__ == "__main__":
    main()