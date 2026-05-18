from sqlalchemy import create_engine
import pandas as pd

# conexão postgres
engine = create_engine(
    "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"
)

# lista tabelas
query = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
"""

tabelas = pd.read_sql(query, engine)

for tabela in tabelas["table_name"]:

    print("\n" + "=" * 80)
    print(f"TABELA: {tabela}")

    # colunas
    col_query = f"""
    SELECT
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_name = '{tabela}'
    ORDER BY ordinal_position;
    """

    colunas = pd.read_sql(col_query, engine)

    print("\nCOLUNAS:")
    print(colunas)

    # amostra
    sample_query = f"""
    SELECT *
    FROM {tabela}
    LIMIT 5;
    """

    amostra = pd.read_sql(sample_query, engine)

    print("\nAMOSTRA:")
    print(amostra)
