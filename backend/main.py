from fastapi import FastAPI
from elasticsearch import Elasticsearch

app = FastAPI()

es = Elasticsearch("http://elasticsearch:9200")

@app.get("/")
def home():
    return {"status": "API funcionando"}

@app.get("/buscar")
def buscar(q: str):
    body = {
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["titulo", "descricao"]
            }
        }
    }

    result = es.search(index="seguranca", body=body)

    hits = []

    for h in result["hits"]["hits"]:
        hits.append({
            "score": h["_score"],
            "dados": h["_source"]
        })

    return hits
