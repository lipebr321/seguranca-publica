# Segurança Pública SP — Data Lake SSP-SP

Projeto de engenharia de dados para coleta, processamento, armazenamento e disponibilização de dados públicos da Secretaria de Segurança Pública do Estado de São Paulo (SSP-SP).

---

# Objetivo

O projeto tem como objetivo:

* Automatizar a coleta de bases públicas da SSP-SP;
* Transformar arquivos XLSX em formato otimizado Parquet;
* Armazenar dados em PostgreSQL;
* Criar um Data Lake local;
* Permitir futuras análises, dashboards e APIs de consulta;
* Estruturar um pipeline de dados reutilizável.

---

# Fontes de Dados

Os dados são obtidos diretamente do portal oficial da SSP-SP:

[https://www.ssp.sp.gov.br/estatistica/consultas](https://www.ssp.sp.gov.br/estatistica/consultas)

Arquivos encontrados automaticamente:

* Dados criminais
* Dados de produtividade
* Morte decorrente de intervenção policial
* Celulares subtraídos
* Veículos subtraídos
* Objetos subtraídos

---

# Arquitetura do Projeto

```text
SSP-SP
   ↓
Download automático
   ↓
Arquivos XLSX
   ↓
Conversão para Parquet
   ↓
Data Lake local
   ↓
PostgreSQL
   ↓
API / Dashboards / ElasticSearch
```

---

# Estrutura do Projeto

```text
seguranca-publica/
│
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   └── index.html
│
├── scripts/
│   ├── download_ssp.py
│   ├── explorar_ssp.py
│   ├── convert_xlsx_to_parquet.py
│   ├── load_parquet_to_postgres.py
│   ├── ingest.py
│   └── download_ssp_selenium.py
│
├── data/
│   ├── raw/
│   │   ├── json/
│   │   └── xlsx/
│   │
│   └── parquet/
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Tecnologias Utilizadas

## Linguagem

* Python 3

## Processamento de Dados

* Pandas
* PyArrow
* OpenPyXL

## Banco de Dados

* PostgreSQL

## Containers

* Docker
* Docker Compose

## Busca e Indexação

* ElasticSearch

## Backend

* FastAPI
* Uvicorn

## Frontend

* Nginx

---

# Configuração do Ambiente

## 1. Clonar projeto

```bash
git clone git@github.com:lipebr321/seguranca-publica.git

cd seguranca-publica
```

---

## 2. Criar ambiente virtual

```bash
python3 -m venv venv
```

Ativar:

```bash
source venv/bin/activate
```

---

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

# Download dos Dados

O script abaixo:

* acessa os JSONs públicos da SSP-SP;
* identifica os XLSX disponíveis;
* baixa apenas arquivos novos;
* evita downloads duplicados.

## Executar

```bash
python scripts/download_ssp.py
```

Arquivos salvos em:

```text
data/raw/xlsx/
```

---

# Conversão XLSX → Parquet

O projeto converte automaticamente:

* arquivos XLSX;
* tratamento de colunas inconsistentes;
* correção de tipos;
* normalização de dados.

O pipeline também:

* ignora arquivos já convertidos;
* continua execução mesmo com erros;
* registra falhas por arquivo.

## Executar

```bash
python scripts/convert_xlsx_to_parquet.py
```

Arquivos gerados:

```text
data/parquet/
```

---

# PostgreSQL

## Subir containers

```bash
docker compose up -d
```

## Verificar containers

```bash
docker ps
```

---

# Carregar dados no PostgreSQL

## Executar

```bash
python scripts/load_parquet_to_postgres.py
```

O processo:

* detecta tabelas já carregadas;
* evita duplicidade;
* carrega apenas tabelas faltantes.

---

# Consultar PostgreSQL

Entrar no banco:

```bash
docker exec -it postgres_ssp psql -U ssp_user -d ssp
```

Listar tabelas:

```sql
\dt
```

Contar registros:

```sql
SELECT COUNT(*) FROM celularessubtraidos_2024;
```

---

# Docker Compose

O projeto utiliza:

* PostgreSQL
* ElasticSearch
* Backend FastAPI
* Frontend Nginx

## Subir ambiente

```bash
docker compose up -d
```

## Derrubar ambiente

```bash
docker compose down
```

---

# GitHub

Projeto versionado em:

[https://github.com/lipebr321/seguranca-publica](https://github.com/lipebr321/seguranca-publica)

---

# Próximos Passos

## Engenharia de Dados

* Particionamento de Parquet;
* Data Lake em S3/MinIO;
* Airflow;
* Delta Lake;
* DuckDB.

## Analytics

* Dashboards;
* Power BI;
* Metabase;
* Kibana.

## Machine Learning

* Predição criminal;
* Hotspots;
* Séries temporais;
* Clusterização.

## APIs

* Busca textual;
* Filtros por cidade;
* Filtros por tipo de crime;
* APIs REST.

---

# Licença

Projeto acadêmico e educacional utilizando dados públicos da SSP-SP.

---

# Autor

Luis Felipe Pereira - Carlos Brito

GitHub:

[https://github.com/lipebr321](https://github.com/lipebr321)
