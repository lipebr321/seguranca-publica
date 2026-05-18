from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)

def main():

    sql = """
    CREATE SCHEMA IF NOT EXISTS dm;

    DROP TABLE IF EXISTS dm.bens_dm;

    CREATE TABLE dm.bens_dm AS

    SELECT
        ano,
        mes,
        fonte,
        municipio,
        tipo_bem,
        subtipo_bem,
        marca_bem,

        COUNT(*) AS total_ocorrencias,
        SUM(quantidade) AS total_bens_subtraidos,

        COUNT(DISTINCT bairro) AS qtd_bairros,
        COUNT(DISTINCT delegacia_circ) AS qtd_delegacias,

        ROUND(
            SUM(quantidade)::numeric / COUNT(*)::numeric,
            2
        ) AS media_bens_por_ocorrencia

    FROM stg.stg_ocorrencias

    WHERE ano IS NOT NULL

    GROUP BY
        ano,
        mes,
        fonte,
        municipio,
        tipo_bem,
        subtipo_bem,
        marca_bem;

    CREATE INDEX idx_bens_ano_mes
        ON dm.bens_dm (ano, mes);

    CREATE INDEX idx_bens_fonte
        ON dm.bens_dm (fonte);

    CREATE INDEX idx_bens_municipio
        ON dm.bens_dm (municipio);

    CREATE INDEX idx_bens_marca
        ON dm.bens_dm (marca_bem);
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Tabela criada: dm.bens_dm")

if __name__ == "__main__":
    main()