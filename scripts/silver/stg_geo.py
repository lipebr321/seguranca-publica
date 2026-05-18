from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)

def main():

    sql = """
    CREATE SCHEMA IF NOT EXISTS stg;

    DROP TABLE IF EXISTS stg.stg_geo;

    CREATE TABLE stg.stg_geo AS

    SELECT
        ROW_NUMBER() OVER() AS id_geo,

        municipio,
        cidade,
        bairro,
        delegacia,
        delegacia_circ,

        ROUND(latitude::numeric, 3) AS latitude_grid,
        ROUND(longitude::numeric, 3) AS longitude_grid,

        AVG(latitude) AS latitude_media,
        AVG(longitude) AS longitude_media,

        COUNT(*) AS total_ocorrencias,

        COUNT(DISTINCT fonte) AS qtd_fontes,

        COUNT(DISTINCT rubrica) AS qtd_tipos_crime

    FROM stg.stg_ocorrencias

    WHERE latitude IS NOT NULL
      AND longitude IS NOT NULL

    GROUP BY
        municipio,
        cidade,
        bairro,
        delegacia,
        delegacia_circ,
        ROUND(latitude::numeric, 3),
        ROUND(longitude::numeric, 3);

    CREATE INDEX idx_geo_lat_lon
        ON stg.stg_geo (latitude_grid, longitude_grid);

    CREATE INDEX idx_geo_municipio
        ON stg.stg_geo (municipio);

    CREATE INDEX idx_geo_bairro
        ON stg.stg_geo (bairro);
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Tabela criada: stg.stg_geo")

if __name__ == "__main__":
    main()