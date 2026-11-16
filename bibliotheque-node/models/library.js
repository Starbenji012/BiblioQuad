const db = require('../db');

async function dashboard() {
  const [[stats]] = await db.query('SELECT COUNT(*) livres, COALESCE(SUM(quantite),0) exemplaires FROM livres');
  const [[active]] = await db.query("SELECT COUNT(*) emprunts FROM emprunts WHERE statut='en_cours' AND date_retour IS NULL");
  return { ...stats, emprunts: active.emprunts };
}
async function books(q = '') {
  const params = q ? [`%${q}%`, `%${q}%`] : [];
  const sql = `SELECT l.*, l.quantite-COALESCE(SUM(CASE WHEN e.statut='en_cours' AND e.date_retour IS NULL THEN 1 ELSE 0 END),0) disponibles
    FROM livres l LEFT JOIN emprunts e ON e.livre_id=l.id ${q ? 'WHERE l.titre LIKE ? OR l.auteur LIKE ?' : ''}
    GROUP BY l.id ORDER BY l.titre`;
  const [rows] = await db.query(sql, params); return rows;
}
async function borrowers() { const [rows] = await db.query('SELECT * FROM emprunteurs ORDER BY nom'); return rows; }
async function loans() { const [rows] = await db.query('SELECT e.*,l.titre,p.nom emprunteur FROM emprunts e JOIN livres l ON l.id=e.livre_id JOIN emprunteurs p ON p.id=e.emprunteur_id ORDER BY e.id DESC'); return rows; }
async function addBook(b) { await db.query('INSERT INTO livres (titre,auteur,categorie,quantite) VALUES (?,?,?,?)', [b.titre,b.auteur,b.categorie,b.quantite]); }
async function updateBook(id,b) { await db.query('UPDATE livres SET titre=?,auteur=?,categorie=?,quantite=? WHERE id=?',[b.titre,b.auteur,b.categorie,b.quantite,id]); }
async function deleteBook(id) { const [[row]] = await db.query('SELECT COUNT(*) count FROM emprunts WHERE livre_id=?',[id]); if (row.count) throw new Error('Impossible de supprimer un livre déjà emprunté.'); await db.query('DELETE FROM livres WHERE id=?',[id]); }
async function addBorrower(b) { await db.query('INSERT INTO emprunteurs (nom,telephone) VALUES (?,?)', [b.nom,b.telephone]); }
async function loan(bookId, borrowerId) {
  const c = await db.getConnection();
  try { await c.beginTransaction(); const [[book]] = await c.query("SELECT quantite,(SELECT COUNT(*) FROM emprunts WHERE livre_id=? AND statut='en_cours' AND date_retour IS NULL) actifs FROM livres WHERE id=? FOR UPDATE", [bookId,bookId]);
    if (!book || book.quantite <= book.actifs) throw new Error('Aucun exemplaire disponible.');
    await c.query("INSERT INTO emprunts (livre_id,emprunteur_id,date_emprunt,statut) VALUES (?,?,CURDATE(),'en_cours')", [bookId,borrowerId]); await c.commit();
  } catch (e) { await c.rollback(); throw e; } finally { c.release(); }
}
async function returnLoan(id) {
  const c = await db.getConnection();
  try { await c.beginTransaction(); const [[row]] = await c.query("SELECT id FROM emprunts WHERE id=? AND statut='en_cours' AND date_retour IS NULL FOR UPDATE",[id]);
    if (!row) throw new Error('Emprunt déjà retourné ou introuvable.');
    await c.query("UPDATE emprunts SET date_retour=CURDATE(),statut='retourne' WHERE id=?",[id]); await c.commit();
  } catch (e) { await c.rollback(); throw e; } finally { c.release(); }
}
module.exports = { dashboard,books,borrowers,loans,addBook,updateBook,deleteBook,addBorrower,loan,returnLoan };
