from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)

def main():

    sql = """
    CREATE SCHEMA IF NOT EXISTS dm;

    DROP TABLE IF EXISTS dm.veiculos_geo_dm;

    CREATE TABLE dm.veiculos_geo_dm AS

    SELECT
        ano,
        mes,
        municipio,
        cidade,
        bairro,

        ROUND(latitude::numeric, 3) AS latitude_grid,
        ROUND(longitude::numeric, 3) AS longitude_grid,

        COUNT(*) AS total_ocorrencias,

        SUM(quantidade) AS total_veiculos_subtraidos,

        SUM(
            CASE
                WHEN rubrica ILIKE '%ROUBO%' THEN quantidade
                ELSE 0
            END
        ) AS total_roubos_veiculos,

        SUM(
            CASE
                WHEN rubrica ILIKE '%FURTO%' THEN quantidade
                ELSE 0
            END
        ) AS total_furtos_veiculos,

        COUNT(DISTINCT delegacia_circ) AS qtd_delegacias,

        MIN(data_ocorrencia) AS primeira_ocorrencia,
        MAX(data_ocorrencia) AS ultima_ocorrencia

    FROM stg.stg_ocorrencias

    WHERE fonte = 'VEICULO'
      AND ano IS NOT NULL
      AND latitude IS NOT NULL
      AND longitude IS NOT NULL

    GROUP BY
        ano,
        mes,
        municipio,
        cidade,
        bairro,
        ROUND(latitude::numeric, 3),
        ROUND(longitude::numeric, 3);

    CREATE INDEX idx_veiculos_geo_ano_mes
        ON dm.veiculos_geo_dm (ano, mes);

    CREATE INDEX idx_veiculos_geo_municipio
        ON dm.veiculos_geo_dm (municipio);

    CREATE INDEX idx_veiculos_geo_lat_lon
        ON dm.veiculos_geo_dm (latitude_grid, longitude_grid);
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Tabela criada: dm.veiculos_geo_dm")

if __name__ == "__main__":
    main()