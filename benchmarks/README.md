# Protocole de comparaison

Chaque lanceur mesure directement les opérations SQL depuis le processus
serveur, sans navigateur, rendu HTML ni réseau HTTP. Le même scénario est
répété `30` fois après `5` répétitions d'échauffement :

1. insertion d'un livre temporaire ;
2. recherche par titre ;
3. lecture de la liste des livres ;
4. modification du livre temporaire ;
5. suppression du livre temporaire.

Chaque mesure utilise une horloge monotone en nanosecondes. Le résultat
affiche la médiane en millisecondes pour chaque opération. Les identifiants
temporaires sont préfixés par `BENCH_` et sont supprimés à la fin. Un résultat
ne doit être comparé qu'avec le même ordinateur, la même version MySQL, les
mêmes données et le même nombre de répétitions.

Les cinq opérations sont mesurées dans cet ordre : insertion, recherche,
lecture, modification, suppression. Les lectures de résultats sont entièrement
consommées avant l'arrêt du chronomètre. La médiane de 30 mesures est la
moyenne des 15e et 16e valeurs après tri. Les écritures sont en autocommit
dans les quatre lanceurs afin de ne pas ajouter un coût de transaction
différent selon le pilote.

Les valeurs de connexion existantes sont conservées. Les valeurs par défaut
des bases (`biblio_php`, `biblio_node`, `biblio_python` et `biblio_java`)
restent donc différentes : pour une comparaison directe, configurez les
variables de connexion vers des bases contenant le même jeu de données et le
même schéma. Les pilotes et la préparation des requêtes restent propres à
chaque langage ; ces différences peuvent influencer les résultats.

Les scripts sont préparés mais non exécutés. Renseigner les variables de
connexion et obtenir l'autorisation avant toute exécution. Le lanceur Java
(`Benchmark.java`) se compile avec le connecteur JDBC MySQL du projet Java.

## Benchmark HTTP commun

Le script `benchmark_http.py` envoie uniquement des requêtes `GET` vers les
pages d'accueil suivantes : PHP (`8000`), Node.js (`3000`), Python (`5000`) et
Java (`8080`). Les applications sont testées successivement. Pour chaque
application et chaque niveau de concurrence (`1`, `5`, `10`, `20`), le script
effectue 5 requêtes d'échauffement non enregistrées puis 30 requêtes mesurées.
Chaque mesure utilise `perf_counter_ns`, un délai d'expiration total de 10
secondes et enregistre le code HTTP ou l'erreur rencontrée.

Depuis la racine du projet, après avoir démarré les quatre applications,
exécuter :

```powershell
.\.venv\Scripts\python.exe .\benchmarks\benchmark_http.py
```

Les résultats sont écrits dans `resultats_http_bruts.csv` (une ligne par
requête mesurée) et `resultats_http_synthese.csv` (moyenne, médiane, 95e
percentile, taux d'erreur et débit). Le taux d'erreur et le débit portent sur
les 30 tentatives, y compris les réponses en erreur. Le 95e percentile utilise
la valeur du rang supérieur (ceil(0,95 × 30)).

Ce test mesure le temps HTTP de bout en bout depuis le client et ne sépare pas
le serveur web, le framework, le rendu de la page, les accès éventuels à la
base de données, le réseau ou la mise en cache. Les pages d'accueil peuvent
donc exécuter des traitements différents : ce résultat ne constitue pas une
comparaison parfaitement isolée des langages. Les tests ne modifient aucune
application ni aucune base de données.

## Graphiques HTTP

Le script `generer_figures_http.py` lit les valeurs réelles de
`resultats_http_synthese.csv` et génère deux images dans `figures` :

```powershell
.\.venv\Scripts\python.exe .\benchmarks\generer_figures_http.py
```

Il produit un graphique en barres à concurrence 20 et un graphique en lignes
pour les concurrences 1, 5, 10 et 20. Les graphiques ne recalculent ni ne
modifient les mesures du CSV.
