from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp")

def main():
    sql = """
    CREATE SCHEMA IF NOT EXISTS dm;

    DROP TABLE IF EXISTS dm.violencia_mulher_geo_dm;

    CREATE TABLE dm.violencia_mulher_geo_dm AS
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
        COUNT(DISTINCT o.rubrica) AS qtd_tipos_crime,
        MIN(o.data_ocorrencia) AS primeira_ocorrencia,
        MAX(o.data_ocorrencia) AS ultima_ocorrencia
    FROM stg.stg_ocorrencias o
    WHERE o.ano IS NOT NULL
      AND o.latitude IS NOT NULL
      AND o.longitude IS NOT NULL
      AND (
            o.rubrica ILIKE '%MULHER%'
         OR o.rubrica ILIKE '%VIOLENCIA DOMESTICA%'
         OR o.rubrica ILIKE '%VIOLÊNCIA DOMÉSTICA%'
         OR o.rubrica ILIKE '%FEMINICIDIO%'
         OR o.rubrica ILIKE '%FEMINICÍDIO%'
         OR o.conduta ILIKE '%MULHER%'
      )
    GROUP BY
        o.ano, o.mes, o.municipio, o.cidade, o.bairro, o.delegacia_circ,
        ROUND(o.latitude::numeric, 3),
        ROUND(o.longitude::numeric, 3);

    CREATE INDEX idx_violencia_mulher_geo
        ON dm.violencia_mulher_geo_dm (latitude_grid, longitude_grid);

    CREATE INDEX idx_violencia_mulher_municipio
        ON dm.violencia_mulher_geo_dm (municipio);
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Tabela criada: dm.violencia_mulher_geo_dm")

if __name__ == "__main__":
    main()