import os
import statistics
import time

import mysql.connector


WARMUP_REPETITIONS = 5
MEASURED_REPETITIONS = 30
cfg = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "biblio_python"),
)
db = mysql.connector.connect(**cfg)
db.autocommit = True
cur = db.cursor()
results = {
    key: [] for key in ("insertion", "recherche", "lecture", "modification", "suppression")
}
temporary_ids = []

try:
    for i in range(WARMUP_REPETITIONS + MEASURED_REPETITIONS):
        measure = i >= WARMUP_REPETITIONS
        title = f"BENCH_{time.perf_counter_ns()}_{i}"

        start = time.perf_counter_ns()
        cur.execute(
            "INSERT INTO livres(titre,auteur,categorie,quantite) VALUES(%s,%s,%s,%s)",
            (title, "Benchmark", "Test", 1),
        )
        book_id = cur.lastrowid
        temporary_ids.append(book_id)
        if measure:
            results["insertion"].append((time.perf_counter_ns() - start) / 1_000_000)

        start = time.perf_counter_ns()
        cur.execute("SELECT id FROM livres WHERE titre LIKE %s", (f"%{title}%",))
        cur.fetchall()
        if measure:
            results["recherche"].append((time.perf_counter_ns() - start) / 1_000_000)

        start = time.perf_counter_ns()
        cur.execute("SELECT * FROM livres ORDER BY id")
        cur.fetchall()
        if measure:
            results["lecture"].append((time.perf_counter_ns() - start) / 1_000_000)

        start = time.perf_counter_ns()
        cur.execute(
            "UPDATE livres SET titre=%s WHERE id=%s", (title + "_EDIT", book_id)
        )
        if measure:
            results["modification"].append((time.perf_counter_ns() - start) / 1_000_000)

        start = time.perf_counter_ns()
        cur.execute("DELETE FROM livres WHERE id=%s", (book_id,))
        if measure:
            results["suppression"].append((time.perf_counter_ns() - start) / 1_000_000)
finally:
    for book_id in temporary_ids:
        cur.execute("DELETE FROM livres WHERE id=%s", (book_id,))
    cur.close()
    db.close()

for operation, values in results.items():
    print(f"{operation}: {statistics.median(values):.3f} ms")
