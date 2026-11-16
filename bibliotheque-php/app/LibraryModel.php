<?php
require_once __DIR__ . '/Database.php';

final class LibraryModel {
    public function __construct(private PDO $db) {}

    public function books(string $search = ''): array {
        $sql = "SELECT l.*, l.quantite - COALESCE(SUM(
            CASE WHEN e.statut='en_cours' AND e.date_retour IS NULL THEN 1 ELSE 0 END
        ), 0) disponibles FROM livres l LEFT JOIN emprunts e ON e.livre_id=l.id";
        $params = [];
        if ($search !== '') {
            $sql .= ' WHERE l.titre LIKE ? OR l.auteur LIKE ?';
            $params = ["%$search%", "%$search%"];
        }
        $sql .= ' GROUP BY l.id ORDER BY l.titre';
        $query = $this->db->prepare($sql);
        $query->execute($params);
        return $query->fetchAll();
    }

    public function dashboard(): array {
        $stats = $this->db->query('SELECT COUNT(*) livres, COALESCE(SUM(quantite),0) exemplaires FROM livres')->fetch();
        $stats['emprunts'] = $this->db->query("SELECT COUNT(*) FROM emprunts WHERE statut='en_cours' AND date_retour IS NULL")->fetchColumn();
        return $stats;
    }

    public function borrowers(): array { return $this->db->query('SELECT * FROM emprunteurs ORDER BY nom')->fetchAll(); }
    public function loans(): array { return $this->db->query('SELECT e.*,l.titre,p.nom emprunteur FROM emprunts e JOIN livres l ON l.id=e.livre_id JOIN emprunteurs p ON p.id=e.emprunteur_id ORDER BY e.id DESC')->fetchAll(); }
    public function addBorrower(array $data): void { $q=$this->db->prepare('INSERT INTO emprunteurs(nom,telephone) VALUES(?,?)'); $q->execute([$data['nom'],$data['telephone']]); }
    public function addBook(array $data): void { $q=$this->db->prepare('INSERT INTO livres(titre,auteur,categorie,quantite) VALUES(?,?,?,?)'); $q->execute([$data['titre'],$data['auteur'],$data['categorie'],$data['quantite']]); }
    public function updateBook(array $data): void { $q=$this->db->prepare('UPDATE livres SET titre=?,auteur=?,categorie=?,quantite=? WHERE id=?'); $q->execute([$data['titre'],$data['auteur'],$data['categorie'],$data['quantite'],$data['id']]); }
    public function deleteBook(int $id): void { $q=$this->db->prepare('SELECT COUNT(*) FROM emprunts WHERE livre_id=?'); $q->execute([$id]); if($q->fetchColumn()) throw new RuntimeException('Impossible de supprimer un livre déjà emprunté.'); $q=$this->db->prepare('DELETE FROM livres WHERE id=?'); $q->execute([$id]); }

    public function createLoan(int $bookId, int $borrowerId): void {
        $this->db->beginTransaction();
        try {
            $q=$this->db->prepare("SELECT quantite,(SELECT COUNT(*) FROM emprunts WHERE livre_id=? AND statut='en_cours' AND date_retour IS NULL) actifs FROM livres WHERE id=? FOR UPDATE");
            $q->execute([$bookId,$bookId]); $book=$q->fetch();
            if(!$book || $book['quantite'] <= $book['actifs']) throw new RuntimeException('Aucun exemplaire disponible.');
            $q=$this->db->prepare("INSERT INTO emprunts(livre_id,emprunteur_id,date_emprunt,statut) VALUES(?,?,CURDATE(),'en_cours')");
            $q->execute([$bookId,$borrowerId]); $this->db->commit();
        } catch(Throwable $error) { $this->db->rollBack(); throw $error; }
    }

    public function returnLoan(int $id): void {
        $this->db->beginTransaction();
        try {
            $q=$this->db->prepare("UPDATE emprunts SET date_retour=CURDATE(),statut='retourne' WHERE id=? AND statut='en_cours' AND date_retour IS NULL");
            $q->execute([$id]); if($q->rowCount() !== 1) throw new RuntimeException('Emprunt déjà retourné ou introuvable.'); $this->db->commit();
        } catch(Throwable $error) { $this->db->rollBack(); throw $error; }
    }
}
