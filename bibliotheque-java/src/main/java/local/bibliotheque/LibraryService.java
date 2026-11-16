package local.bibliotheque;
import java.util.*; import org.springframework.jdbc.core.JdbcTemplate; import org.springframework.stereotype.Service; import org.springframework.transaction.annotation.Transactional;
@Service public class LibraryService {
 private final JdbcTemplate db; public LibraryService(JdbcTemplate db){this.db=db;}
 public Map<String,Object> stats(){var s=db.queryForMap("SELECT COUNT(*) livres,COALESCE(SUM(quantite),0) exemplaires FROM livres"); s.put("emprunts",db.queryForObject("SELECT COUNT(*) FROM emprunts WHERE statut='en_cours' AND date_retour IS NULL",Integer.class)); return s;}
 public List<Map<String,Object>> books(String q){String sql="SELECT l.*,l.quantite-COALESCE(SUM(CASE WHEN e.statut='en_cours' AND e.date_retour IS NULL THEN 1 ELSE 0 END),0) disponibles FROM livres l LEFT JOIN emprunts e ON e.livre_id=l.id"; Object[] p=new Object[0]; if(q!=null&&!q.isBlank()){sql+=" WHERE l.titre LIKE ? OR l.auteur LIKE ?"; p=new Object[]{"%"+q+"%","%"+q+"%"};} sql+=" GROUP BY l.id ORDER BY l.titre"; return db.queryForList(sql,p);}
 public List<Map<String,Object>> borrowers(){return db.queryForList("SELECT * FROM emprunteurs ORDER BY nom");}
 public List<Map<String,Object>> loans(){return db.queryForList("SELECT e.*,l.titre,p.nom emprunteur FROM emprunts e JOIN livres l ON l.id=e.livre_id JOIN emprunteurs p ON p.id=e.emprunteur_id ORDER BY e.id DESC");}
 public void addBook(String t,String a,String c,int q){db.update("INSERT INTO livres(titre,auteur,categorie,quantite) VALUES(?,?,?,?)",t,a,c,q);}
 public void updateBook(int id,String t,String a,String c,int q){db.update("UPDATE livres SET titre=?,auteur=?,categorie=?,quantite=? WHERE id=?",t,a,c,q,id);}
 public void deleteBook(int id){if(db.queryForObject("SELECT COUNT(*) FROM emprunts WHERE livre_id=?",Integer.class,id)>0) throw new IllegalStateException("Impossible de supprimer un livre déjà emprunté."); db.update("DELETE FROM livres WHERE id=?",id);}
 public void addBorrower(String n,String t){db.update("INSERT INTO emprunteurs(nom,telephone) VALUES(?,?)",n,t);}
 @Transactional public void loan(int book,int borrower){var b=db.queryForMap("SELECT quantite,(SELECT COUNT(*) FROM emprunts WHERE livre_id=? AND statut='en_cours' AND date_retour IS NULL) actifs FROM livres WHERE id=? FOR UPDATE",book,book); if((Integer)b.get("quantite")<=((Number)b.get("actifs")).intValue()) throw new IllegalStateException("Aucun exemplaire disponible."); db.update("INSERT INTO emprunts(livre_id,emprunteur_id,date_emprunt,statut) VALUES(?,?,CURDATE(),'en_cours')",book,borrower);}
 @Transactional public void returnLoan(int id){if(db.update("UPDATE emprunts SET date_retour=CURDATE(),statut='retourne' WHERE id=? AND statut='en_cours' AND date_retour IS NULL",id)!=1) throw new IllegalStateException("Emprunt déjà retourné ou introuvable.");}
}
