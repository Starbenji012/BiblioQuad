const mysql = require('mysql2/promise');

const WARMUP_REPETITIONS = 5;
const MEASURED_REPETITIONS = 30;
const db = mysql.createPool({
  host: process.env.DB_HOST || '127.0.0.1',
  port: Number(process.env.DB_PORT || 3306),
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'biblio_node'
});

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = sorted.length / 2;
  return (sorted[middle - 1] + sorted[middle]) / 2;
}

function elapsedMilliseconds(start) {
  return Number(process.hrtime.bigint() - start) / 1e6;
}

(async () => {
  const result = {
    insertion: [],
    recherche: [],
    lecture: [],
    modification: [],
    suppression: []
  };
  const temporaryIds = [];

  try {
    for (let i = 0; i < WARMUP_REPETITIONS + MEASURED_REPETITIONS; i += 1) {
      const measure = i >= WARMUP_REPETITIONS;
      const title = `BENCH_${process.hrtime.bigint()}_${i}`;

      let start = process.hrtime.bigint();
      const [insert] = await db.query(
        'INSERT INTO livres(titre,auteur,categorie,quantite) VALUES(?,?,?,?)',
        [title, 'Benchmark', 'Test', 1]
      );
      temporaryIds.push(insert.insertId);
      if (measure) {
        result.insertion.push(elapsedMilliseconds(start));
      }

      start = process.hrtime.bigint();
      await db.query('SELECT id FROM livres WHERE titre LIKE ?', [`%${title}%`]);
      if (measure) {
        result.recherche.push(elapsedMilliseconds(start));
      }

      start = process.hrtime.bigint();
      await db.query('SELECT * FROM livres ORDER BY id');
      if (measure) {
        result.lecture.push(elapsedMilliseconds(start));
      }

      start = process.hrtime.bigint();
      await db.query('UPDATE livres SET titre=? WHERE id=?', [`${title}_EDIT`, insert.insertId]);
      if (measure) {
        result.modification.push(elapsedMilliseconds(start));
      }

      start = process.hrtime.bigint();
      await db.query('DELETE FROM livres WHERE id=?', [insert.insertId]);
      if (measure) {
        result.suppression.push(elapsedMilliseconds(start));
      }
    }
  } finally {
    for (const id of temporaryIds) {
      await db.query('DELETE FROM livres WHERE id=?', [id]);
    }
    await db.end();
  }

  for (const [key, values] of Object.entries(result)) {
    console.log(`${key}: ${median(values).toFixed(3)} ms`);
  }
})().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
