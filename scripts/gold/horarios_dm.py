from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)

def main():

    sql = """
    CREATE SCHEMA IF NOT EXISTS dm;

    DROP TABLE IF EXISTS dm.horarios_dm;

    CREATE TABLE dm.horarios_dm AS

    SELECT
        o.ano,
        o.mes,

        t.nome_mes,
        t.trimestre,
        t.semestre,

        p.hora,
        p.periodo,

        o.fonte,
        o.municipio,

        COUNT(*) AS total_ocorrencias,

        SUM(o.quantidade) AS total_bens_subtraidos,

        COUNT(DISTINCT o.bairro) AS qtd_bairros_afetados,

        COUNT(DISTINCT o.delegacia_circ) AS qtd_delegacias

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
        p.hora,
        p.periodo,
        o.fonte,
        o.municipio;

    CREATE INDEX idx_horarios_ano_mes
        ON dm.horarios_dm (ano, mes);

    CREATE INDEX idx_horarios_periodo
        ON dm.horarios_dm (periodo);

    CREATE INDEX idx_horarios_hora
        ON dm.horarios_dm (hora);

    CREATE INDEX idx_horarios_municipio
        ON dm.horarios_dm (municipio);
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Tabela criada: dm.horarios_dm")

if __name__ == "__main__":
    main()