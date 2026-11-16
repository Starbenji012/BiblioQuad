<?php
$config = require __DIR__ . '/../bibliotheque-php/config.php';
$db = new PDO(
    $config['dsn'],
    $config['user'],
    $config['password'],
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

const WARMUP_REPETITIONS = 5;
const MEASURED_REPETITIONS = 30;

function median(array $values): float
{
    sort($values, SORT_NUMERIC);
    $middle = count($values) / 2;
    return ($values[(int)$middle - 1] + $values[(int)$middle]) / 2;
}

$result = [
    'insertion' => [],
    'recherche' => [],
    'lecture' => [],
    'modification' => [],
    'suppression' => [],
];
$temporaryIds = [];

try {
    for ($i = 0; $i < WARMUP_REPETITIONS + MEASURED_REPETITIONS; $i++) {
        $measure = $i >= WARMUP_REPETITIONS;
        $title = 'BENCH_' . hrtime(true) . '_' . $i;

        $start = hrtime(true);
        $query = $db->prepare(
            'INSERT INTO livres(titre,auteur,categorie,quantite) VALUES(?,?,?,?)'
        );
        $query->execute([$title, 'Benchmark', 'Test', 1]);
        $id = (int)$db->lastInsertId();
        $temporaryIds[] = $id;
        if ($measure) {
            $result['insertion'][] = (hrtime(true) - $start) / 1e6;
        }

        $start = hrtime(true);
        $query = $db->prepare('SELECT id FROM livres WHERE titre LIKE ?');
        $query->execute(["%$title%"]);
        $query->fetchAll(PDO::FETCH_COLUMN);
        if ($measure) {
            $result['recherche'][] = (hrtime(true) - $start) / 1e6;
        }

        $start = hrtime(true);
        $db->query('SELECT * FROM livres ORDER BY id')->fetchAll();
        if ($measure) {
            $result['lecture'][] = (hrtime(true) - $start) / 1e6;
        }

        $start = hrtime(true);
        $query = $db->prepare('UPDATE livres SET titre=? WHERE id=?');
        $query->execute([$title . '_EDIT', $id]);
        if ($measure) {
            $result['modification'][] = (hrtime(true) - $start) / 1e6;
        }

        $start = hrtime(true);
        $query = $db->prepare('DELETE FROM livres WHERE id=?');
        $query->execute([$id]);
        if ($measure) {
            $result['suppression'][] = (hrtime(true) - $start) / 1e6;
        }
    }
} finally {
    if ($temporaryIds !== []) {
        $query = $db->prepare('DELETE FROM livres WHERE id=?');
        foreach ($temporaryIds as $id) {
            $query->execute([$id]);
        }
    }
    $db = null;
}

foreach ($result as $name => $values) {
    printf("%s: %.3f ms%s", $name, median($values), PHP_EOL);
}
