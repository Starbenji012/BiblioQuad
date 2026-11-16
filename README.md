# BiblioQuad

BiblioQuad est un projet académique qui implémente la même application web de
gestion de bibliothèque dans quatre technologies : PHP, Node.js, Python et
Java. Chaque application possède sa base MySQL dédiée et conserve les mêmes
entités fonctionnelles : livres, emprunteurs et emprunts.

## Applications et technologies

| Application | Technologie | Base MySQL | Port HTTP |
|---|---|---|---:|
| [`bibliotheque-php`](./bibliotheque-php) | PHP natif MVC | `biblio_php` | 8000 |
| [`bibliotheque-node`](./bibliotheque-node) | Node.js + Express MVC | `biblio_node` | 3000 |
| [`bibliotheque-python`](./bibliotheque-python) | Python + Flask MVC | `biblio_python` | 5000 |
| [`bibliotheque-java`](./bibliotheque-java) | Java + Spring Boot MVC | `biblio_java` | 8080 |

Les quatre applications utilisent les tables `livres`, `emprunteurs` et
`emprunts`. La disponibilité est calculée à partir de la quantité et des
emprunts actifs. Les prêts et les retours utilisent une transaction et un
verrou sur le livre.

## Prérequis

- MySQL compatible avec le schéma du projet ;
- PHP et l'extension PDO MySQL ;
- Node.js et npm ;
- Python 3.12 recommandé, avec un environnement virtuel ;
- JDK compatible avec la version déclarée dans
  [`bibliotheque-java/pom.xml`](./bibliotheque-java/pom.xml) et Maven ;
- `aiohttp` et `matplotlib` pour les scripts HTTP et les figures.

Les versions observées lors de la préparation du rapport sont indiquées dans
le tableau de l'article. Elles ne constituent pas une empreinte complète de
la campagne HTTP.

## Bases MySQL

Créer quatre bases séparées, sans réutiliser une base de production :

```sql
CREATE DATABASE biblio_php CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE biblio_node CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE biblio_python CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE biblio_java CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Le schéma requis doit être installé dans chacune des quatre bases. Le fichier
[`scripts/seed.sql`](./scripts/seed.sql) contient uniquement des insertions
idempotentes de démonstration ; l'exécuter séparément dans chaque base après
avoir vérifié les données.

Les applications lisent les paramètres suivants dans l'environnement :

| Variable | Valeur de développement par défaut |
|---|---|
| `DB_HOST` | `127.0.0.1` |
| `DB_PORT` | `3306` |
| `DB_USER` | `root` |
| `DB_PASSWORD` | vide |
| `DB_NAME` | dépend de l'application |

Java utilise en plus `DB_URL` et `PORT`. Python utilise aussi `SECRET_KEY`
pour la configuration Flask. Les valeurs par défaut sont destinées au
développement local ; définir des variables explicites avant tout déploiement.
Ne jamais committer un fichier `.env` ou un mot de passe réel.

## Installation et démarrage

Depuis la racine du projet, démarrer une seule application à la fois avec sa
base correspondante, sauf pour le benchmark HTTP qui nécessite les quatre
applications simultanément.

### PHP

```powershell
php -S 127.0.0.1:8000 -t .\bibliotheque-php
```

### Node.js

```powershell
Set-Location .\bibliotheque-node
npm install
npm start
```

### Python

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\bibliotheque-python\requirements.txt
.\.venv\Scripts\python.exe .\bibliotheque-python\app.py
```

### Java

Configurer `DB_URL`, `DB_USER` et `DB_PASSWORD`, puis :

```powershell
Set-Location .\bibliotheque-java
mvn spring-boot:run
```

Les pages d'accueil sont accessibles respectivement aux adresses
`http://127.0.0.1:8000/`, `http://127.0.0.1:3000/`,
`http://127.0.0.1:5000/` et `http://127.0.0.1:8080/`.

## Benchmarks et résultats

Les scripts et le protocole détaillé sont dans [`benchmarks/`](./benchmarks).
Les quatre benchmarks SQL mesurent insertion, recherche, lecture, modification
et suppression, après cinq échauffements et avec trente mesures. Ils écrivent
temporairement dans la base et ne doivent être lancés qu'après vérification de
la configuration.

Le benchmark HTTP ne modifie ni application ni base de données. Après avoir
démarré les quatre applications, l'exécuter depuis la racine :

```powershell
.\.venv\Scripts\python.exe .\benchmarks\benchmark_http.py
```

Il produit :

- [`benchmarks/resultats_http_bruts.csv`](./benchmarks/resultats_http_bruts.csv) ;
- [`benchmarks/resultats_http_synthese.csv`](./benchmarks/resultats_http_synthese.csv).

Les figures peuvent être régénérées à partir du CSV synthétique :

```powershell
.\.venv\Scripts\python.exe .\benchmarks\generer_figures_http.py
```

Les deux images sont dans [`benchmarks/figures/`](./benchmarks/figures).
Le rapport est disponible en source LaTeX et en PDF :
[`article_biblioquad.tex`](./benchmarks/article_biblioquad.tex) et
[`article_biblioquad.pdf`](./benchmarks/article_biblioquad.pdf).

Pour compiler le rapport avec MiKTeX :

```powershell
Set-Location .\benchmarks
pdflatex -interaction=nonstopmode article_biblioquad.tex
pdflatex -interaction=nonstopmode article_biblioquad.tex
```

## Limites méthodologiques

Le benchmark HTTP mesure un `GET /` de bout en bout : serveur HTTP, framework,
rendu, accès éventuels à MySQL, réseau local et cache ne sont pas séparés.
Les pages d'accueil n'effectuent donc pas nécessairement le même traitement ;
les résultats ne constituent pas une comparaison parfaitement isolée des
langages. Les tests doivent être reproduits sur le même matériel, avec les
mêmes données, versions et conditions de charge.

## Publication GitHub

Le dépôt est préparé mais aucune publication ni aucun `push` n'a été effectué.
Avant de rendre le dépôt public :

1. relire `git status` et `git diff --stat` ;
2. vérifier qu'aucun `.env`, mot de passe réel, clé ou artefact généré n'est
   suivi ;
3. décider si les adresses e-mail des auteurs dans le PDF et le `.tex` doivent
   rester publiques ;
4. créer un dépôt GitHub vide, sans README ni licence générés automatiquement ;
5. initialiser et publier le dépôt localement :

```powershell
git init
git branch -M main
git add .
git status
git commit -m "Prepare BiblioQuad for GitHub"
git remote add origin https://github.com/<compte>/<depot>.git
git push -u origin main
```

La commande `git push` ne doit être exécutée qu'après la confirmation des
fichiers à publier et du dépôt distant.
