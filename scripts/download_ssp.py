import requests
import json
import argparse
from pathlib import Path
from urllib.parse import urljoin
from time import sleep

BASE_URL = "https://www.ssp.sp.gov.br/"

JSONS = [
    "baseDadosCelVeiEObjSub.json",
    "spDados160_516.json"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.ssp.sp.gov.br/estatistica/consultas"
}

parser = argparse.ArgumentParser()
parser.add_argument(
    "--force",
    action="store_true",
    help="Baixa novamente mesmo se o arquivo já existir"
)
args = parser.parse_args()

Path("data/raw/json").mkdir(parents=True, exist_ok=True)
Path("data/raw/xlsx").mkdir(parents=True, exist_ok=True)

session = requests.Session()

def baixar_json(json_name):
    url = urljoin(BASE_URL, f"assets/estatistica/transparencia/{json_name}")
    destino = Path("data/raw/json") / json_name

    if destino.exists() and not args.force:
        print(f"JSON já existe, pulando: {destino}")
        with open(destino, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"\nBaixando JSON: {json_name}")

    response = session.get(url, headers=HEADERS, timeout=60)
    print(f"Status JSON: {response.status_code}")

    if response.status_code != 200:
        print(f"Erro ao baixar JSON: {json_name}")
        return None

    conteudo = response.content.decode("utf-8-sig")
    dados = json.loads(conteudo)

    with open(destino, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f"JSON salvo: {destino}")

    return dados

def baixar_xlsx(url, destino):
    destino = Path(destino)

    if destino.exists() and not args.force:
        print(f"XLSX já existe, pulando: {destino}")
        return

    print(f"Baixando XLSX: {destino.name}")

    response = session.get(url, headers=HEADERS, timeout=120)
    print(f"Status XLSX: {response.status_code}")

    if response.status_code == 200:
        with open(destino, "wb") as f:
            f.write(response.content)

        print(f"Salvo: {destino}")
    else:
        print(f"Erro HTTP: {response.status_code}")

for json_name in JSONS:

    print("\n==============================")

    dados = baixar_json(json_name)

    if not dados:
        continue

    for categoria in dados.get("data", []):

        nome_categoria = categoria.get("nome", "Sem categoria")
        print(f"\nCategoria: {nome_categoria}")

        for item in categoria.get("lista", []):

            periodo = item.get("periodo", "")
            arquivo = item.get("arquivo", "")

            if not arquivo:
                continue

            arquivo_url = urljoin(BASE_URL, arquivo)
            nome_arquivo = arquivo.split("/")[-1]
            destino = Path("data/raw/xlsx") / nome_arquivo

            print(f"Período: {periodo}")

            baixar_xlsx(
                arquivo_url,
                destino
            )

            sleep(1)

print("\nDOWNLOAD FINALIZADO")