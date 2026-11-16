import java.sql.*;
import java.util.*;

/** Mesure les requêtes JDBC sans démarrer le serveur web ni rendre de vue. */
public class Benchmark {
    static final int WARMUP_REPETITIONS = 5;
    static final int MEASURED_REPETITIONS = 30;

    static long now() {
        return System.nanoTime();
    }

    static double median(List<Double> values) {
        Collections.sort(values);
        int middle = values.size() / 2;
        return (values.get(middle - 1) + values.get(middle)) / 2;
    }

    public static void main(String[] args) throws Exception {
        String url = System.getenv().getOrDefault("DB_URL", "jdbc:mysql://127.0.0.1:3306/biblio_java");
        try (Connection db = DriverManager.getConnection(
                url,
                System.getenv().getOrDefault("DB_USER", "root"),
                System.getenv().getOrDefault("DB_PASSWORD", ""))) {
            db.setAutoCommit(true);
            Map<String, List<Double>> results = new LinkedHashMap<>();
            for (String name : List.of("insertion", "recherche", "lecture", "modification", "suppression")) {
                results.put(name, new ArrayList<>());
            }
            List<Long> temporaryIds = new ArrayList<>();

            try {
                for (int i = 0; i < WARMUP_REPETITIONS + MEASURED_REPETITIONS; i++) {
                    boolean measure = i >= WARMUP_REPETITIONS;
                    String title = "BENCH_" + System.nanoTime() + "_" + i;

                    long start = now();
                    long id;
                    try (PreparedStatement query = db.prepareStatement(
                            "INSERT INTO livres(titre,auteur,categorie,quantite) VALUES(?,?,?,?)",
                            Statement.RETURN_GENERATED_KEYS)) {
                        query.setString(1, title);
                        query.setString(2, "Benchmark");
                        query.setString(3, "Test");
                        query.setInt(4, 1);
                        query.executeUpdate();
                        try (ResultSet keys = query.getGeneratedKeys()) {
                            keys.next();
                            id = keys.getLong(1);
                        }
                    }
                    temporaryIds.add(id);
                    if (measure) {
                        results.get("insertion").add((now() - start) / 1_000_000.0);
                    }

                    start = now();
                    try (PreparedStatement query = db.prepareStatement(
                            "SELECT id FROM livres WHERE titre LIKE ?")) {
                        query.setString(1, "%" + title + "%");
                        try (ResultSet rows = query.executeQuery()) {
                            while (rows.next()) {
                                rows.getLong(1);
                            }
                        }
                    }
                    if (measure) {
                        results.get("recherche").add((now() - start) / 1_000_000.0);
                    }

                    start = now();
                    try (Statement query = db.createStatement();
                         ResultSet rows = query.executeQuery("SELECT * FROM livres ORDER BY id")) {
                        while (rows.next()) {
                            rows.getObject(1);
                        }
                    }
                    if (measure) {
                        results.get("lecture").add((now() - start) / 1_000_000.0);
                    }

                    start = now();
                    try (PreparedStatement query = db.prepareStatement(
                            "UPDATE livres SET titre=? WHERE id=?")) {
                        query.setString(1, title + "_EDIT");
                        query.setLong(2, id);
                        query.executeUpdate();
                    }
                    if (measure) {
                        results.get("modification").add((now() - start) / 1_000_000.0);
                    }

                    start = now();
                    try (PreparedStatement query = db.prepareStatement(
                            "DELETE FROM livres WHERE id=?")) {
                        query.setLong(1, id);
                        query.executeUpdate();
                    }
                    if (measure) {
                        results.get("suppression").add((now() - start) / 1_000_000.0);
                    }
                }
            } finally {
                try (PreparedStatement query = db.prepareStatement("DELETE FROM livres WHERE id=?")) {
                    for (long id : temporaryIds) {
                        query.setLong(1, id);
                        query.executeUpdate();
                    }
                }
            }

            results.forEach((name, values) -> System.out.printf("%s: %.3f ms%n", name, median(values)));
        }
    }
}
