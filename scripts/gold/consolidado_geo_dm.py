from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"
)

def main():

    sql = """
    CREATE SCHEMA IF NOT EXISTS dm;

    DROP TABLE IF EXISTS dm.consolidado_geo_dm;

    CREATE TABLE dm.consolidado_geo_dm AS

    SELECT
        ano,
        mes,
        municipio,
        cidade,
        bairro,

        latitude_grid,
        longitude_grid,

        'VEICULOS' AS indicador,

        total_ocorrencias,

        total_veiculos_subtraidos AS total_bens_subtraidos,

        total_roubos_veiculos AS total_roubos,

        total_furtos_veiculos AS total_furtos

    FROM dm.veiculos_geo_dm

    UNION ALL

    SELECT
        ano,
        mes,
        municipio,
        cidade,
        bairro,

        latitude_grid,
        longitude_grid,

        'CELULARES' AS indicador,

        total_ocorrencias,

        total_celulares_subtraidos AS total_bens_subtraidos,

        total_roubos_celulares AS total_roubos,

        total_furtos_celulares AS total_furtos

    FROM dm.celulares_geo_dm

    UNION ALL

    SELECT
        ano,
        mes,
        municipio,
        cidade,
        bairro,

        latitude_grid,
        longitude_grid,

        'VIOLENCIA_MULHER' AS indicador,

        total_ocorrencias,

        0 AS total_bens_subtraidos,

        0 AS total_roubos,

        0 AS total_furtos

    FROM dm.violencia_mulher_geo_dm;

    CREATE INDEX idx_consolidado_geo
        ON dm.consolidado_geo_dm (
            latitude_grid,
            longitude_grid
        );

    CREATE INDEX idx_consolidado_indicador
        ON dm.consolidado_geo_dm (
            indicador
        );

    CREATE INDEX idx_consolidado_municipio
        ON dm.consolidado_geo_dm (
            municipio
        );
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Tabela criada: dm.consolidado_geo_dm")

if __name__ == "__main__":
    main()