from db import connection


def dashboard():
    db = connection()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS livres, COALESCE(SUM(quantite), 0) AS exemplaires FROM livres")
    stats = cur.fetchone()
    cur.execute("SELECT COUNT(*) AS emprunts FROM emprunts WHERE statut = 'en_cours' AND date_retour IS NULL")
    stats["emprunts"] = cur.fetchone()["emprunts"]
    cur.close()
    db.close()
    return stats


def books(search=""):
    db = connection()
    cur = db.cursor(dictionary=True)
    query = """SELECT l.*, l.quantite - COALESCE(SUM(
        CASE WHEN e.statut = 'en_cours' AND e.date_retour IS NULL THEN 1 ELSE 0 END
    ), 0) AS disponibles
    FROM livres l LEFT JOIN emprunts e ON e.livre_id = l.id"""
    params = []
    if search:
        query += " WHERE l.titre LIKE %s OR l.auteur LIKE %s"
        params = [f"%{search}%"] * 2
    query += " GROUP BY l.id ORDER BY l.titre"
    cur.execute(query, params)
    result = cur.fetchall()
    cur.close()
    db.close()
    return result


def borrowers():
    db = connection()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM emprunteurs ORDER BY nom")
    result = cur.fetchall()
    cur.close()
    db.close()
    return result


def loans():
    db = connection()
    cur = db.cursor(dictionary=True)
    cur.execute("""SELECT e.*, l.titre, p.nom AS emprunteur
                   FROM emprunts e JOIN livres l ON l.id=e.livre_id
                   JOIN emprunteurs p ON p.id=e.emprunteur_id
                   ORDER BY e.id DESC""")
    result = cur.fetchall()
    cur.close()
    db.close()
    return result


def add_book(data):
    db = connection()
    cur = db.cursor()
    cur.execute("INSERT INTO livres (titre, auteur, categorie, quantite) VALUES (%s,%s,%s,%s)",
                (data["titre"], data["auteur"], data.get("categorie"), data["quantite"]))
    db.commit()
    cur.close(); db.close()


def update_book(book_id, data):
    db = connection()
    cur = db.cursor()
    cur.execute("UPDATE livres SET titre=%s, auteur=%s, categorie=%s, quantite=%s WHERE id=%s",
                (data["titre"], data["auteur"], data.get("categorie"), data["quantite"], book_id))
    db.commit()
    cur.close(); db.close()


def delete_book(book_id):
    db = connection()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM emprunts WHERE livre_id=%s", (book_id,))
    if cur.fetchone()[0]:
        cur.close(); db.close()
        raise ValueError("Impossible de supprimer un livre déjà emprunté.")
    cur.execute("DELETE FROM livres WHERE id=%s", (book_id,))
    db.commit()
    cur.close(); db.close()


def add_borrower(data):
    db = connection()
    cur = db.cursor()
    cur.execute("INSERT INTO emprunteurs (nom, telephone) VALUES (%s,%s)", (data["nom"], data["telephone"]))
    db.commit()
    cur.close(); db.close()


def create_loan(book_id, borrower_id):
    db = connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT quantite, (SELECT COUNT(*) FROM emprunts WHERE livre_id=%s AND statut='en_cours' AND date_retour IS NULL) AS actifs FROM livres WHERE id=%s FOR UPDATE", (book_id, book_id))
        book = cur.fetchone()
        if not book or book["quantite"] <= book["actifs"]:
            raise ValueError("Aucun exemplaire disponible.")
        cur.execute("INSERT INTO emprunts (livre_id, emprunteur_id, date_emprunt, statut) VALUES (%s,%s,CURDATE(),'en_cours')", (book_id, borrower_id))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def return_loan(loan_id):
    db = connection()
    try:
        cur = db.cursor()
        cur.execute("SELECT id FROM emprunts WHERE id=%s AND statut='en_cours' AND date_retour IS NULL FOR UPDATE", (loan_id,))
        if not cur.fetchone():
            raise ValueError("Emprunt déjà retourné ou introuvable.")
        cur.execute("UPDATE emprunts SET date_retour=CURDATE(), statut='retourne' WHERE id=%s", (loan_id,))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
