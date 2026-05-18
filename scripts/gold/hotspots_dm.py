from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)

def main():

    sql = """
    CREATE SCHEMA IF NOT EXISTS dm;

    DROP TABLE IF EXISTS dm.hotspots_dm;

    CREATE TABLE dm.hotspots_dm AS

    SELECT
        ano,
        mes,
        fonte,
        municipio,
        cidade,
        bairro,
        delegacia_circ,
        tipo_local,

        ROUND(AVG(latitude)::numeric, 6) AS latitude_media,
        ROUND(AVG(longitude)::numeric, 6) AS longitude_media,

        COUNT(*) AS total_ocorrencias,
        SUM(quantidade) AS total_bens_subtraidos,

        CASE
            WHEN COUNT(*) <= 10 THEN 'BAIXO'
            WHEN COUNT(*) <= 50 THEN 'MODERADO'
            WHEN COUNT(*) <= 100 THEN 'ALTO'
            WHEN COUNT(*) <= 500 THEN 'CRITICO'
            ELSE 'EXTREMO'
        END AS nivel_risco

    FROM stg.stg_ocorrencias

    WHERE ano IS NOT NULL

    GROUP BY
        ano,
        mes,
        fonte,
        municipio,
        cidade,
        bairro,
        delegacia_circ,
        tipo_local;

    CREATE INDEX idx_hotspots_ano_mes
        ON dm.hotspots_dm (ano, mes);

    CREATE INDEX idx_hotspots_municipio
        ON dm.hotspots_dm (municipio);

    CREATE INDEX idx_hotspots_bairro
        ON dm.hotspots_dm (bairro);

    CREATE INDEX idx_hotspots_risco
        ON dm.hotspots_dm (nivel_risco);
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Tabela criada: dm.hotspots_dm")

if __name__ == "__main__":
    main()