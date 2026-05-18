from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)

def main():

    sql = """
    CREATE SCHEMA IF NOT EXISTS dm;

    DROP TABLE IF EXISTS dm.ocorrencias_resumo_dm;

    CREATE TABLE dm.ocorrencias_resumo_dm AS

    SELECT
        o.ano,
        o.mes,
        t.nome_mes,

        o.fonte,

        o.municipio,
        o.cidade,

        COUNT(*) AS total_ocorrencias,

        SUM(o.quantidade) AS total_bens_subtraidos,

        COUNT(DISTINCT o.bairro) AS qtd_bairros,

        COUNT(DISTINCT o.delegacia_circ) AS qtd_delegacias,

        ROUND(
            SUM(o.quantidade)::numeric
            /
            COUNT(*)::numeric,
            2
        ) AS ticket_medio_bens

    FROM stg.stg_ocorrencias o

    LEFT JOIN stg.stg_tempo t
        ON o.data_ocorrencia = t.data

    WHERE o.ano IS NOT NULL

    GROUP BY
        o.ano,
        o.mes,
        t.nome_mes,
        o.fonte,
        o.municipio,
        o.cidade;

    CREATE INDEX idx_resumo_ano_mes
        ON dm.ocorrencias_resumo_dm (ano, mes);

    CREATE INDEX idx_resumo_municipio
        ON dm.ocorrencias_resumo_dm (municipio);

    CREATE INDEX idx_resumo_fonte
        ON dm.ocorrencias_resumo_dm (fonte);
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Tabela criada: dm.ocorrencias_resumo_dm")

if __name__ == "__main__":
    main()