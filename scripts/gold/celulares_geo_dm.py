from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp")

def main():
    sql = """
    CREATE SCHEMA IF NOT EXISTS dm;

    DROP TABLE IF EXISTS dm.celulares_geo_dm;

    CREATE TABLE dm.celulares_geo_dm AS
    SELECT
        o.ano,
        o.mes,
        o.municipio,
        o.cidade,
        o.bairro,
        o.delegacia_circ,
        ROUND(o.latitude::numeric, 3) AS latitude_grid,
        ROUND(o.longitude::numeric, 3) AS longitude_grid,

        COUNT(*) AS total_ocorrencias,
        SUM(o.quantidade) AS total_celulares_subtraidos,

        SUM(CASE WHEN o.rubrica ILIKE '%ROUBO%' THEN o.quantidade ELSE 0 END) AS total_roubos_celulares,
        SUM(CASE WHEN o.rubrica ILIKE '%FURTO%' THEN o.quantidade ELSE 0 END) AS total_furtos_celulares,

        COUNT(DISTINCT o.marca_bem) AS qtd_marcas,
        MIN(o.data_ocorrencia) AS primeira_ocorrencia,
        MAX(o.data_ocorrencia) AS ultima_ocorrencia
    FROM stg.stg_ocorrencias o
    WHERE o.fonte = 'CELULAR'
      AND o.ano IS NOT NULL
      AND o.latitude IS NOT NULL
      AND o.longitude IS NOT NULL
    GROUP BY
        o.ano, o.mes, o.municipio, o.cidade, o.bairro, o.delegacia_circ,
        ROUND(o.latitude::numeric, 3),
        ROUND(o.longitude::numeric, 3);

    CREATE INDEX idx_celulares_geo
        ON dm.celulares_geo_dm (latitude_grid, longitude_grid);

    CREATE INDEX idx_celulares_municipio
        ON dm.celulares_geo_dm (municipio);
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Tabela criada: dm.celulares_geo_dm")

if __name__ == "__main__":
    main()