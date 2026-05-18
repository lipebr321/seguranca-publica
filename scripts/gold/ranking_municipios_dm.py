from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)

def main():

    sql = """
    CREATE SCHEMA IF NOT EXISTS dm;

    DROP TABLE IF EXISTS dm.ranking_municipios_dm;

    CREATE TABLE dm.ranking_municipios_dm AS

    SELECT
        ano,
        mes,
        municipio,
        fonte,

        COUNT(*) AS total_ocorrencias,
        SUM(quantidade) AS total_bens_subtraidos,
        COUNT(DISTINCT bairro) AS qtd_bairros_afetados,
        COUNT(DISTINCT delegacia_circ) AS qtd_delegacias,

        RANK() OVER (
            PARTITION BY ano, mes, fonte
            ORDER BY COUNT(*) DESC
        ) AS ranking_municipio_mes

    FROM stg.stg_ocorrencias

    WHERE ano IS NOT NULL
      AND municipio IS NOT NULL

    GROUP BY
        ano,
        mes,
        municipio,
        fonte;

    CREATE INDEX idx_ranking_municipios_ano_mes
        ON dm.ranking_municipios_dm (ano, mes);

    CREATE INDEX idx_ranking_municipios_municipio
        ON dm.ranking_municipios_dm (municipio);

    CREATE INDEX idx_ranking_municipios_fonte
        ON dm.ranking_municipios_dm (fonte);
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Tabela criada: dm.ranking_municipios_dm")

if __name__ == "__main__":
    main()