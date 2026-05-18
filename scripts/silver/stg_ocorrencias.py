import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://ssp_user:ssp_pass@localhost:5432/ssp"

engine = create_engine(DATABASE_URL)


def normalizar_texto(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if valor == "":
        return None

    return valor.upper()


def listar_tabelas_origem():
    query = text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND (
            table_name LIKE 'celularessubtraidos_%'
            OR table_name LIKE 'veiculossubtraidos_%'
            OR table_name LIKE 'objetossubtraidos_%'
        )
        ORDER BY table_name;
    """)

    with engine.connect() as conn:
        return pd.read_sql(query, conn)["table_name"].tolist()


def preparar_dataframe(df, tabela):
    colunas = df.columns.tolist()

    # Ignora arquivos que são metodologia/dicionário
    if len(colunas) <= 2 and "metodologia" in str(colunas[0]).lower():
        print(f"Ignorando tabela de metodologia: {tabela}")
        return pd.DataFrame()

    if tabela.startswith("celularessubtraidos"):
        fonte = "CELULAR"
        tipo_bem_col = "DESCR_TIPO_OBJETO"
        subtipo_bem_col = "DESCR_SUBTIPO_OBJETO"
        marca_bem_col = "MARCA_OBJETO"
        quantidade_col = "QUANTIDADE_OBJETO"

    elif tabela.startswith("objetossubtraidos"):
        fonte = "OBJETO"
        tipo_bem_col = "DESCR_TIPO_OBJETO"
        subtipo_bem_col = "DESCR_SUBTIPO_OBJETO"
        marca_bem_col = "MARCA_OBJETO"
        quantidade_col = "QUANTIDADE_OBJETO"

    elif tabela.startswith("veiculossubtraidos"):
        fonte = "VEICULO"
        tipo_bem_col = "DESCR_TIPO_VEICULO"
        subtipo_bem_col = "DESCR_OCORRENCIA_VEICULO"
        marca_bem_col = "DESCR_MARCA_VEICULO"
        quantidade_col = None

    else:
        return pd.DataFrame()

    def pegar(col):
        if col and col in df.columns:
            return df[col]
        return pd.Series([None] * len(df), index=df.index)

    saida = pd.DataFrame(index=df.index)

    # Corrigido: cria fonte como coluna com mesmo tamanho do dataframe
    saida["fonte"] = pd.Series([fonte] * len(df), index=df.index)
    saida["tabela_origem"] = pd.Series([tabela] * len(df), index=df.index)

    saida["ano"] = pegar("ANO")
    saida["mes"] = pegar("MES")

    saida["data_ocorrencia"] = pegar("DATA_OCORRENCIA_BO")

    if "HORA_OCORRENCIA" in df.columns:
        saida["hora_ocorrencia"] = pegar("HORA_OCORRENCIA")
    else:
        saida["hora_ocorrencia"] = pegar("HORA_OCORRENCIA_BO")

    if "NOME_MUNICIPIO_CIRC" in df.columns:
        saida["municipio"] = pegar("NOME_MUNICIPIO_CIRC")
    else:
        saida["municipio"] = pegar("NOME_MUNICIPIO")

    saida["cidade"] = pegar("CIDADE")
    saida["bairro"] = pegar("BAIRRO")
    saida["delegacia"] = pegar("NOME_DELEGACIA")
    saida["delegacia_circ"] = pegar("NOME_DELEGACIA_CIRC")

    saida["rubrica"] = pegar("RUBRICA")
    saida["conduta"] = pegar("DESCR_CONDUTA")
    saida["tipo_local"] = pegar("DESCR_TIPOLOCAL")
    saida["subtipo_local"] = pegar("DESCR_SUBTIPOLOCAL")

    saida["latitude"] = pegar("LATITUDE")
    saida["longitude"] = pegar("LONGITUDE")

    saida["tipo_bem"] = pegar(tipo_bem_col)
    saida["subtipo_bem"] = pegar(subtipo_bem_col)
    saida["marca_bem"] = pegar(marca_bem_col)

    if quantidade_col:
        saida["quantidade"] = pegar(quantidade_col)
    else:
        saida["quantidade"] = pd.Series(["1"] * len(df), index=df.index)

    # Limpeza textual somente em colunas textuais
    colunas_texto = [
        "fonte",
        "tabela_origem",
        "hora_ocorrencia",
        "municipio",
        "cidade",
        "bairro",
        "delegacia",
        "delegacia_circ",
        "rubrica",
        "conduta",
        "tipo_local",
        "subtipo_local",
        "tipo_bem",
        "subtipo_bem",
        "marca_bem"
    ]

    for col in colunas_texto:
        if col in saida.columns:
            saida[col] = saida[col].apply(normalizar_texto)

    # Tipagem numérica
    saida["ano"] = pd.to_numeric(saida["ano"], errors="coerce").astype("Int64")
    saida["mes"] = pd.to_numeric(saida["mes"], errors="coerce").astype("Int64")

    saida["quantidade"] = (
        pd.to_numeric(saida["quantidade"], errors="coerce")
        .fillna(1)
        .astype(int)
    )

    # Data
    saida["data_ocorrencia"] = pd.to_datetime(
        saida["data_ocorrencia"],
        errors="coerce"
    ).dt.date

    # Latitude e longitude
    saida["latitude"] = (
        saida["latitude"]
        .astype("string")
        .str.replace(",", ".", regex=False)
    )

    saida["longitude"] = (
        saida["longitude"]
        .astype("string")
        .str.replace(",", ".", regex=False)
    )

    saida["latitude"] = pd.to_numeric(saida["latitude"], errors="coerce")
    saida["longitude"] = pd.to_numeric(saida["longitude"], errors="coerce")

    # Remove registros inválidos
    saida = saida[saida["ano"].notna()]

    return saida


def main():
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS stg;"))
        conn.execute(text("DROP TABLE IF EXISTS stg.stg_ocorrencias;"))

    tabelas = listar_tabelas_origem()

    print(f"Tabelas encontradas: {len(tabelas)}")

    primeira_carga = True

    for tabela in tabelas:
        print("\n==============================")
        print(f"Lendo: {tabela}")

        with engine.connect() as conn:
            df = pd.read_sql(
                text(f'SELECT * FROM public."{tabela}"'),
                conn
            )

        stg = preparar_dataframe(df, tabela)

        if stg.empty:
            print("Sem dados válidos para carregar.")
            continue

        print(f"Carregando {len(stg)} linhas em stg.stg_ocorrencias")

        stg.to_sql(
            "stg_ocorrencias",
            engine,
            schema="stg",
            if_exists="replace" if primeira_carga else "append",
            index=False,
            chunksize=10000,
            method="multi"
        )

        primeira_carga = False

    print("\nSTG finalizada: stg.stg_ocorrencias")


if __name__ == "__main__":
    main()