import requests
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    )
}

# arquivos JS encontrados no HTML
JS_FILES = [
    "https://www.ssp.sp.gov.br/runtime.a5dc32c1ca8e6772.js",
    "https://www.ssp.sp.gov.br/polyfills.d4c011a4c11ebf6b.js",
    "https://www.ssp.sp.gov.br/scripts.dcc45d84c84ddb6d.js",
    "https://www.ssp.sp.gov.br/main.a9e2763a4f505b0d.js"
]

jsons_encontrados = set()

for js_url in JS_FILES:

    print(f"\nLendo: {js_url}")

    try:

        response = requests.get(
            js_url,
            headers=HEADERS,
            timeout=30
        )

        conteudo = response.text

        encontrados = re.findall(
            r'[\w\-_]+\.json',
            conteudo
        )

        for item in encontrados:
            jsons_encontrados.add(item)

    except Exception as e:
        print("Erro:", e)

print("\nJSONs encontrados:\n")

for item in sorted(jsons_encontrados):
    print(item)