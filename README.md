# Pipeline ELT e-commerce : Airflow, dbt, DuckDB

Pipeline de données de bout en bout : ingestion d'une API, transformation en
couches avec tests de qualité, génération d'un rapport, le tout orchestré
et testé automatiquement.

> Les données viennent de Mockaroo (jeu synthétique, aléatoire à chaque appel).
> La valeur du projet est le pipeline et ses contrôles qualité, pas les insights métier.

## Architecture

```
Mockaroo API
    │  (Python, include/ingest_orders.py)
    ▼
raw.orders          1000 lignes, tout en texte, snapshot remplacé à chaque run
    │  (dbt : typage, nettoyage, dédoublonnage)
    ▼
refined.orders      typé, ~950 lignes, total_amount calculé
    │  (dbt : retrait des données personnelles)
    ▼
reported.sales      sans nom ni email client
    │  (Python, reporting/build_report.py)
    ▼
reports/report.html KPIs, top produits, ventes par jour
```

Airflow orchestre trois tâches en série : `ingest_orders` → `dbt_build` → `build_report`.
Les tâches sont en série car DuckDB n'accepte qu'un seul processus en écriture.

## Stack

| Rôle | Outil |
|---|---|
| Orchestration | Apache Airflow 3.3.2 (CeleryExecutor, Docker Compose) |
| Transformation et tests de données | dbt-core 1.12 + dbt-duckdb |
| Stockage | DuckDB 1.5.6 |
| Tests de code | pytest |
| CI | GitHub Actions |

## Structure

```
airflow/            DAG (dags/), code d'ingestion (include/), Dockerfile, compose
dbt/                models/ (refined, reported), macros/, tests/ (SQL)
reporting/          génération du rapport HTML
tests/              tests pytest (ingestion, rapport, structure du DAG)
scripts/            outils de développement (inspection de la base)
```

## Qualité des données : ce que le pipeline a révélé

Les tests dbt ont détecté trois problèmes réels dans les données brutes :

1. **Dates au format `M/D/YYYY`** (`10/1/2026`), non ISO : un simple `cast` donnait NULL
   sur 100 % des lignes. Corrigé avec `try_strptime`.
2. **`discount` est un montant**, pas une fraction ni un pourcentage. L'hypothèse
   initiale `(1 - discount)` produisait 925 totaux négatifs sur 1000.
   Formule retenue : `quantity * unit_price - discount + shipping_cost`.
3. **Doublons d'`order_id`** : environ 4 à 5 % par run (Mockaroo tire des ids au hasard).
   Dédoublonnés dans `refined` avec `qualify row_number()`.

## Tests

| Type | Emplacement | Ce qui est vérifié |
|---|---|---|
| Données (dbt) | `dbt/models/*/schema.yml`, `dbt/tests/` | `not_null`, `unique`, montants positifs, à chaque run |
| Code (pytest) | `tests/test_ingest.py`, `test_report.py` | validation du CSV, chargement, rapport, appel API simulé |
| Structure du DAG | `tests/test_dag.py` | 3 tâches, bon ordre (exécuté en CI avec Airflow) |

## Lancer le projet

Prérequis : Docker Desktop, Python 3.13.

```bash
# 1. Configurer les secrets
cp airflow/.env.example airflow/.env
#    renseigner MOCKAROO_API_KEY et FERNET_KEY
#    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Initialiser la base (schéma raw)
python scripts/init_db.py

# 3. Démarrer Airflow
cd airflow
docker compose build
docker compose up airflow-init
docker compose up -d
```

Interface : http://localhost:8081 (identifiants par défaut `airflow` / `airflow`, À ADAPTER).
Active le DAG `ecommerce_etl` puis déclenche-le. Le rapport apparaît dans `reports/report.html`.

Tests locaux : `pip install pytest pandas duckdb requests` puis `pytest -q`
(`test_dag.py` est ignoré sans Airflow, il tourne en CI).

## Choix et limites assumés

- **Snapshot complet à chaque run** (`CREATE OR REPLACE`) : Mockaroo génère des
  données différentes à chaque appel, les ids ne sont pas stables, donc pas de modèle
  incrémental.
- **DuckDB** : base embarquée, un seul écrivain. Adapté à un projet local,
  pas à la production multi-utilisateurs.
- **Deux environnements Python dans l'image** : dbt est dans un venv séparé pour éviter
  les conflits de dépendances avec Airflow. DuckDB est figé à la même version partout
  (1.5.6), car les versions peuvent changer le format du fichier.
- **Sécurité** : image de base officielle `apache/airflow`, scannée avec Docker Scout
  (vulnérabilités critiques signalées dans l'image de base). Usage local uniquement,
  non exposé sur Internet.
- **CI sans déploiement** : la CI vérifie le code, le DAG, le build dbt sur une mini base
  et le build de l'image. Il n'y a pas de livraison continue vers un serveur.

## Pistes d'amélioration

- Rapport avec graphiques, `dbt docs` pour le lineage.
- Marts agrégés dans dbt plutôt que dans le script de rapport.
- Passage à un entrepôt multi-utilisateurs (Postgres, MotherDuck) pour la concurrence.