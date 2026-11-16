-- Jeu commun, non destructif et réexécutable sur chaque base.
INSERT INTO livres (titre, auteur, categorie, quantite)
SELECT 'Le Petit Prince', 'Antoine de Saint-Exupéry', 'Roman', 3
WHERE NOT EXISTS (SELECT 1 FROM livres WHERE titre='Le Petit Prince' AND auteur='Antoine de Saint-Exupéry');
INSERT INTO livres (titre, auteur, categorie, quantite)
SELECT 'Une si longue lettre', 'Mariama Bâ', 'Littérature', 2
WHERE NOT EXISTS (SELECT 1 FROM livres WHERE titre='Une si longue lettre' AND auteur='Mariama Bâ');
INSERT INTO livres (titre, auteur, categorie, quantite)
SELECT 'Clean Code', 'Robert C. Martin', 'Informatique', 2
WHERE NOT EXISTS (SELECT 1 FROM livres WHERE titre='Clean Code' AND auteur='Robert C. Martin');
INSERT INTO emprunteurs (nom, telephone)
SELECT 'Aminata Diallo', '0600000001'
WHERE NOT EXISTS (SELECT 1 FROM emprunteurs WHERE nom='Aminata Diallo' AND telephone='0600000001');
INSERT INTO emprunteurs (nom, telephone)
SELECT 'Paul Martin', '0600000002'
WHERE NOT EXISTS (SELECT 1 FROM emprunteurs WHERE nom='Paul Martin' AND telephone='0600000002');
