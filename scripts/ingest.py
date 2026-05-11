import pandas as pd

# --- Carregamento dos dados (ajuste o caminho conforme o arquivo da SSP) ---
df = pd.read_csv("dados_ssp.csv", encoding="latin1", sep=";")

# --- Motor de busca ---
def buscar(df, texto=None, tipo_crime=None, ano=None, regiao=None):
    resultado = df.copy()

    # Busca textual em múltiplas colunas
    if texto:
        texto = texto.lower()
        mask = (
            resultado["municipio"].str.lower().str.contains(texto, na=False) |
            resultado["delegacia"].str.lower().str.contains(texto, na=False) |
            resultado["natureza"].str.lower().str.contains(texto, na=False)
        )
        resultado = resultado[mask]

    # Filtros exatos
    if tipo_crime:
        resultado = resultado[resultado["natureza"] == tipo_crime]
    if ano:
        resultado = resultado[resultado["ano"] == int(ano)]
    if regiao:
        resultado = resultado[resultado["regiao"] == regiao]

    return resultado

# --- Resumo dos resultados ---
def resumo(resultado):
    print(f"Registros encontrados : {len(resultado)}")
    print(f"Total de ocorrências  : {resultado['ocorrencias'].sum():,}")
    print(f"Municípios            : {resultado['municipio'].nunique()}")
    print(f"Tipos de crime        : {resultado['natureza'].nunique()}")
    print()
    print(resultado[["municipio", "delegacia", "natureza", "ano", "ocorrencias"]].to_string(index=False))

# --- Exemplo de uso ---
resultado = buscar(df, texto="são paulo", tipo_crime="Roubo", ano="2023")
resumo(resultado)
