PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        nombre_emprunts_en_cours INTEGER DEFAULT 0,
        total_emprunts INTEGER DEFAULT 0,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    , role TEXT DEFAULT 'utilisateur');
INSERT INTO utilisateurs VALUES(1,'Utilisateur',' ','user','12345',0,0,'Ad vitam æternam','utilisateur');
INSERT INTO utilisateurs VALUES(2,'De la Fontaine','Adélaïde','adelaide.delafontaine@gmail.com','Ad3l@!2025',0,0,'2025-01-12 04:22:56','utilisateur');
INSERT INTO utilisateurs VALUES(3,'Château','Bastien','bastien.chateau@outlook.fr','B@sti3n_95',0,0,'2025-01-12 04:22:56','utilisateur');
INSERT INTO utilisateurs VALUES(4,'Rousseau','Élise','elise.rousseau@live.fr','R0usseau_123',0,0,'2025-01-12 04:22:56','utilisateur');
INSERT INTO utilisateurs VALUES(5,'Montmorency','Thibault','thibault.montmorency@yahoo.fr','Th!bault2025',0,0,'2025-01-12 04:22:56','utilisateur');
INSERT INTO utilisateurs VALUES(6,'Beaumont','Camille','camille.beaumont@protonmail.com','C@mi115ecure',0,0,'2025-01-12 04:22:56','utilisateur');
CREATE TABLE ressources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        auteur TEXT NOT NULL,
        type_ressource TEXT NOT NULL,
        date_publication DATE,
        nombre_exemplaires_total INTEGER NOT NULL,
        nombre_emprunts_total INTEGER DEFAULT 0
    );
INSERT INTO ressources VALUES(1,'Les Misérables','Victor Hugo','Historique','1862-01-01',5,0);
INSERT INTO ressources VALUES(2,'Le Rouge et le Noir','Stendhal','Psychologique','1830-01-01',4,0);
INSERT INTO ressources VALUES(3,'Madame Bovary','Gustave Flaubert','Realisme','1857-01-01',6,0);
INSERT INTO ressources VALUES(4,'Le Petit Prince','Antoine de Saint-Exupéry','Philosophique','1943-01-01',10,0);
INSERT INTO ressources VALUES(5,'Candide','Voltaire','Philosophique','1759-01-01',8,0);
INSERT INTO ressources VALUES(6,'À la recherche du temps perdu','Marcel Proust','Moderniste','1913-01-01',3,0);
INSERT INTO ressources VALUES(7,'Germinal','Émile Zola','Naturaliste','1885-01-01',4,0);
INSERT INTO ressources VALUES(8,'Les Fleurs du Mal','Charles Baudelaire','Poésie','1857-01-01',6,0);
INSERT INTO ressources VALUES(9,'Le Comte de Monte-Cristo','Alexandre Dumas','Aventure','1844-01-01',5,0);
INSERT INTO ressources VALUES(10,'L''Etranger','Albert Camus','Absurdiste','1942-01-01',7,0);
CREATE TABLE exemplaires (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ressource_id INTEGER NOT NULL,
        utilisateur_id INTEGER DEFAULT NULL,
        emprunte BOOLEAN DEFAULT 0,
        date_emprunt DATE DEFAULT NULL,
        FOREIGN KEY(ressource_id) REFERENCES ressources(id) ON DELETE CASCADE,
        FOREIGN KEY(utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
    );
INSERT INTO exemplaires VALUES(1,1,NULL,0,NULL);
INSERT INTO exemplaires VALUES(2,1,NULL,0,NULL);
INSERT INTO exemplaires VALUES(3,1,NULL,0,NULL);
INSERT INTO exemplaires VALUES(4,1,NULL,0,NULL);
INSERT INTO exemplaires VALUES(5,1,NULL,0,NULL);
INSERT INTO exemplaires VALUES(6,2,NULL,0,NULL);
INSERT INTO exemplaires VALUES(7,2,NULL,0,NULL);
INSERT INTO exemplaires VALUES(8,2,NULL,0,NULL);
INSERT INTO exemplaires VALUES(9,2,NULL,0,NULL);
INSERT INTO exemplaires VALUES(10,3,NULL,0,NULL);
INSERT INTO exemplaires VALUES(11,3,NULL,0,NULL);
INSERT INTO exemplaires VALUES(12,3,NULL,0,NULL);
INSERT INTO exemplaires VALUES(13,3,NULL,0,NULL);
INSERT INTO exemplaires VALUES(14,4,NULL,0,NULL);
INSERT INTO exemplaires VALUES(15,4,NULL,0,NULL);
INSERT INTO exemplaires VALUES(16,4,NULL,0,NULL);
INSERT INTO exemplaires VALUES(17,4,NULL,0,NULL);
INSERT INTO exemplaires VALUES(18,4,NULL,0,NULL);
INSERT INTO exemplaires VALUES(19,5,NULL,0,NULL);
INSERT INTO exemplaires VALUES(20,5,NULL,0,NULL);
INSERT INTO exemplaires VALUES(21,5,NULL,0,NULL);
INSERT INTO exemplaires VALUES(22,5,NULL,0,NULL);
INSERT INTO exemplaires VALUES(23,5,NULL,0,NULL);
INSERT INTO exemplaires VALUES(24,6,NULL,0,NULL);
INSERT INTO exemplaires VALUES(25,6,NULL,0,NULL);
INSERT INTO exemplaires VALUES(26,6,NULL,0,NULL);
INSERT INTO exemplaires VALUES(27,7,NULL,0,NULL);
INSERT INTO exemplaires VALUES(28,7,NULL,0,NULL);
INSERT INTO exemplaires VALUES(29,7,NULL,0,NULL);
INSERT INTO exemplaires VALUES(30,7,NULL,0,NULL);
INSERT INTO exemplaires VALUES(31,8,NULL,0,NULL);
INSERT INTO exemplaires VALUES(32,8,NULL,0,NULL);
INSERT INTO exemplaires VALUES(33,8,NULL,0,NULL);
INSERT INTO exemplaires VALUES(34,8,NULL,0,NULL);
INSERT INTO exemplaires VALUES(35,8,NULL,0,NULL);
INSERT INTO exemplaires VALUES(36,9,NULL,0,NULL);
INSERT INTO exemplaires VALUES(37,9,NULL,0,NULL);
INSERT INTO exemplaires VALUES(38,9,NULL,0,NULL);
INSERT INTO exemplaires VALUES(39,9,NULL,0,NULL);
INSERT INTO exemplaires VALUES(40,10,NULL,0,NULL);
INSERT INTO exemplaires VALUES(41,10,NULL,0,NULL);
INSERT INTO exemplaires VALUES(42,10,NULL,0,NULL);
INSERT INTO exemplaires VALUES(43,10,NULL,0,NULL);
INSERT INTO exemplaires VALUES(44,10,NULL,0,NULL);
CREATE TABLE emprunts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        utilisateur_id INTEGER NOT NULL,
        ressource_id INTEGER NOT NULL,
        date_emprunt DATE NOT NULL,
        FOREIGN KEY(utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
        FOREIGN KEY(ressource_id) REFERENCES ressources(id) ON DELETE CASCADE
    );
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('utilisateurs',6);
INSERT INTO sqlite_sequence VALUES('ressources',10);
INSERT INTO sqlite_sequence VALUES('exemplaires',44);
CREATE TRIGGER apres_emprunt
    AFTER INSERT ON emprunts
    BEGIN
        UPDATE ressources
        SET nombre_emprunts_total = nombre_emprunts_total + 1
        WHERE id = NEW.ressource_id;

        UPDATE utilisateurs
        SET nombre_emprunts_en_cours = nombre_emprunts_en_cours + 1,
            total_emprunts = total_emprunts + 1
        WHERE id = NEW.utilisateur_id;
    END;
CREATE TRIGGER retour_emprunt
    AFTER DELETE ON emprunts
    BEGIN
        UPDATE utilisateurs
        SET nombre_emprunts_en_cours = nombre_emprunts_en_cours - 1
        WHERE id = OLD.utilisateur_id;
    END;
CREATE TRIGGER apres_suppression_utilisateur AFTER DELETE ON utilisateurs BEGIN UPDATE exemplaires SET emprunte = 0, utilisateur_id = NULL, date_emprunt = NULL WHERE utilisateur_id = OLD.id; UPDATE ressources SET nombre_exemplaires_total = nombre_exemplaires_total + (SELECT COUNT(*) FROM exemplaires WHERE utilisateur_id = OLD.id AND ressource_id = ressources.id) WHERE id IN (SELECT ressource_id FROM exemplaires WHERE utilisateur_id = OLD.id); DELETE FROM emprunts WHERE utilisateur_id = OLD.id; END;
CREATE TRIGGER supprimer_ressource_si_vide AFTER DELETE ON exemplaires BEGIN DELETE FROM ressources WHERE id = OLD.ressource_id AND NOT EXISTS (SELECT 1 FROM exemplaires WHERE ressource_id = OLD.ressource_id); END;
COMMIT;
