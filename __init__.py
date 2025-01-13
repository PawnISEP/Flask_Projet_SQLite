#Importation de Flask et de ses modules
from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from werkzeug.utils import safe_join
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3


app = Flask(__name__)

# Configuration préalable 

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# @app.route - HTML & URL

@app.route('/')
def documentation():
    return render_template('Documentation.html')

@app.route('/accueil')
def accueil():
    return render_template('Accueil.html')

@app.route('/catalogue')
def catalogue():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.titre, 
                   r.auteur, 
                   r.date_publication, 
                   COUNT(CASE WHEN e.emprunte = 0 THEN 1 END) AS disponibles,
                   COUNT(CASE WHEN e.emprunte = 1 THEN 1 END) AS empruntes,
                   r.type_ressource
            FROM ressources r
            LEFT JOIN exemplaires e ON r.id = e.ressource_id
            GROUP BY r.id;
        """)
        livres = cursor.fetchall()
        conn.close()

        # Résultats pour le template

        return render_template(
            'Catalogue.html',
            livres=[
                {
                    'titre': livre[0] or "Titre inconnu",
                    'auteur': livre[1] or "Auteur inconnu",
                    'date_publication': datetime.strptime(livre[2], "%Y-%m-%d").strftime("%d/%m/%Y") if livre[2] else "N/A",
                    'nombre_exemplaires_disponibles': livre[3] or 0,
                    'nombre_exemplaires_empruntes': livre[4] or 0,
                    'type_ressource': livre[5] or "Non spécifié"
                }
                for livre in livres
            ]
        )

    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return render_template('erreur.html', message="Une erreur est survenue lors de l'accès à la base de données."), 500



@app.route('/emprunter', methods=['GET'])
def emprunter():
    if not session.get('authentifie'):
        return redirect(url_for('authentification', auth='login-required'))

    if session.get('role') != 'utilisateur':
        return redirect(url_for('stocks'))     

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT r.id AS ressource_id, r.titre, r.auteur, r.type_ressource, 
                   r.date_publication, COUNT(e.id) AS disponibles, MIN(e.id) AS exemplaire_id
            FROM ressources r
            LEFT JOIN exemplaires e ON r.id = e.ressource_id AND e.emprunte = 0
            GROUP BY r.id
        ''')
        ressources = cursor.fetchall()

        conn.close()

        ressources_disponibles = [
            {
                'id': ressource[0], 
                'titre': ressource[1],
                'auteur': ressource[2],
                'type_ressource': ressource[3],
                'date_publication': datetime.strptime(ressource[4], "%Y-%m-%d").strftime("%d/%m/%Y") if ressource[4] else "N/A",
                'nombre_exemplaires_disponibles': ressource[5],
                'exemplaire_id': ressource[6]  # Premier exemplaire disponible
            }
            for ressource in ressources
        ]

        return render_template('Emprunter.html', ressources=ressources_disponibles)
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return "Erreur interne du serveur.", 500

@app.route('/emprunter/<int:id_utilisateur>/<int:ressource_id>', methods=['POST'])
def emprunter_exemplaire(id_utilisateur, ressource_id):
    if not session.get('authentifie'):
        return "Accès refusé : Vous devez être connecté.", 403

    if session.get('role') != 'admin' and session.get('id_utilisateur') != id_utilisateur:
        return "Accès refusé : Vous ne pouvez pas emprunter pour un autre utilisateur.", 403

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Vérifiez si l'utilisateur existe

        cursor.execute("SELECT id FROM utilisateurs WHERE id = ?", (id_utilisateur,))
        utilisateur = cursor.fetchone()
        if not utilisateur:
            conn.close()
            return "Erreur : Utilisateur introuvable.", 404

        # Trouver un exemplaire disponible pour cette ressource

        cursor.execute("""
            SELECT id FROM exemplaires 
            WHERE ressource_id = ? AND emprunte = 0 LIMIT 1
        """, (ressource_id,))
        exemplaire = cursor.fetchone()
        if not exemplaire:
            conn.close()
            return "Erreur : Aucun exemplaire disponible.", 404

        # Emprunter l'exemplaire

        cursor.execute("""
            UPDATE exemplaires
            SET emprunte = 1, utilisateur_id = ?, date_emprunt = ?
            WHERE id = ?
        """, (id_utilisateur, datetime.now().strftime("%Y-%m-%d"), exemplaire[0]))

        # Mettre à jour les statistiques de l'utilisateur

        cursor.execute("""
            UPDATE utilisateurs
            SET nombre_emprunts_en_cours = nombre_emprunts_en_cours + 1, total_emprunts = total_emprunts + 1
            WHERE id = ?
        """, (id_utilisateur,))

        conn.commit()
        conn.close()

        return redirect(url_for('emprunter', request='success'))

    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return "Erreur interne du serveur.", 500



@app.route('/restituer', methods=['GET'])
def restituer():
    if not session.get('authentifie'):
        return redirect(url_for('authentification', auth='login-required'))
    
    if session.get('role') != 'utilisateur':
        return redirect(url_for('stocks'))  

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT e.id AS id_emprunt, r.titre, r.auteur, r.type_ressource, e.date_emprunt
            FROM exemplaires e
            JOIN ressources r ON e.ressource_id = r.id
            WHERE e.utilisateur_id = ? AND e.emprunte = 1
        ''', (session.get('id_utilisateur'),))
        emprunts = cursor.fetchall()

        conn.close()

        emprunts_utilisateur = [
            {
                'id_emprunt': emprunt[0],
                'titre': emprunt[1],
                'auteur': emprunt[2],
                'type_ressource': emprunt[3],
                'date_emprunt': datetime.strptime(emprunt[4], "%Y-%m-%d").strftime("%d/%m/%Y") if emprunt[4] else "N/A"
            }
            for emprunt in emprunts
        ]

        return render_template('Restituer.html', emprunts=emprunts_utilisateur)
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return "Erreur interne du serveur.", 500



@app.route('/restituer/<int:id_utilisateur>/<int:id_emprunt>', methods=['POST'])
def restituer_ressource(id_utilisateur, id_emprunt):
    if not session.get('authentifie'):
        return "Accès refusé : Vous devez être connecté.", 403

    # Seuls l'utilisateur lui-même ou un administrateur peuvent restituer

    if session.get('role') != 'admin' and session.get('id_utilisateur') != id_utilisateur:
        return "Accès refusé : Vous ne pouvez pas restituer cet emprunt.", 403

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Vérifier que l'emprunt existe et appartient à l'utilisateur

        cursor.execute('''
            SELECT id, ressource_id FROM exemplaires
            WHERE id = ? AND utilisateur_id = ? AND emprunte = 1
        ''', (id_emprunt, id_utilisateur))
        emprunt = cursor.fetchone()

        if not emprunt:
            conn.close()
            return "Erreur : Aucun emprunt correspondant trouvé.", 404

        exemplaire_id, ressource_id = emprunt

        # Libérer l'exemplaire

        cursor.execute('''
            UPDATE exemplaires
            SET emprunte = 0, utilisateur_id = NULL, date_emprunt = NULL
            WHERE id = ?
        ''', (exemplaire_id,))

        # Décrémenter le compteur d'emprunts en cours de l'utilisateur

        cursor.execute('''
            UPDATE utilisateurs
            SET nombre_emprunts_en_cours = nombre_emprunts_en_cours - 1
            WHERE id = ?
        ''', (id_utilisateur,))

        conn.commit()
        conn.close()

        # Redirection en fonction du rôle de l'utilisateur

        if session.get('role') == 'admin':
            return redirect(url_for('stocks', request='success'))
        else:
            return redirect(url_for('restituer', request='success'))

    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return "Erreur interne du serveur.", 500



@app.route('/authentification', methods=['GET', 'POST'])
def authentification():

    if session.get('authentifie'):
        session.clear()
        return redirect(url_for('authentification'))

    if request.method == 'POST':
        email = request.form.get('username')
        mot_de_passe = request.form.get('password')

        # Gestion des accès admin et utilisateur

        if email == 'admin' and mot_de_passe == 'password':
            session['authentifie'] = True
            session['role'] = 'admin'  # Rôle admin
            return redirect(url_for('accueil', auth='success'))

        # Vérification dans la base de données pour d'autres utilisateurs
        try:
            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM utilisateurs WHERE email = ? AND password = ?", (email, mot_de_passe))
            utilisateur = cursor.fetchone()
            connection.close()

            if utilisateur:
                session['authentifie'] = True
                session['role'] = 'utilisateur'
                session['id_utilisateur'] = utilisateur[0]
                return redirect(url_for('accueil', auth='success'))

            else:
                return redirect(url_for('authentification', auth='error'))
        except sqlite3.Error as e:
            print(f"Erreur SQLite : {e}")
            return redirect(url_for('authentification', auth='error'))

    return render_template('Authentification.html', erreur=request.args.get('auth') == 'error')


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():

    # Si l'utilisateur est connecté avec le rôle 'utilisateur', on le déconnecte

    if session.get('role') == 'utilisateurs':
        session.clear()
        return redirect(url_for('inscription'))

    if request.method == 'POST':

        # Récupération des données du formulaire

        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'utilisateur')  # Par défaut, le rôle est 'utilisateur'

        if nom and prenom and email and password:
            try:

                connection = sqlite3.connect('database.db')
                cursor = connection.cursor()

                # Insertion dans la base de données

                cursor.execute(
                    "INSERT INTO utilisateurs (nom, prenom, email, password, role) VALUES (?, ?, ?, ?, ?)",
                    (nom, prenom, email, password, role)
                )
                connection.commit()
                connection.close()


                if session.get('role') == 'admin':
                    return redirect(url_for('sessions', request='success'))
                else:
                    # Redirection pour une inscription depuis un utilisateur non connecté
                    return redirect(url_for('accueil', auth='success', inscription='success'))
            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
                return redirect(url_for('inscription', auth='error'))
        else:
            # Champs obligatoires non remplis
            return redirect(url_for('inscription', auth='error'))

    # Gestion des cas en GET (success ou error)
    
    statut_authentification = request.args.get('auth')
    if statut_authentification == 'success':
        return render_template('Accueil.html', afficher_notification=True)  # Notification activée
    elif statut_authentification == 'error':
        return render_template('Inscription.html', erreur=True)  # Page avec erreur
    else:
        return render_template('Inscription.html', erreur=False)  # Page sans erreur

    
@app.template_filter('format_datetime')
def format_datetime(value, format="%d/%m/%Y à %H:%M"):
    try:
        # Conversion explicite en chaîne
        value = str(value)
        date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return date.strftime(format)
    except (ValueError, TypeError):
        return value  # Retourne la valeur brute si le parsing échoue

@app.route('/utilisateur/<int:id>/supprimer', methods=['POST'])
def supprimer_utilisateur(id):

    if not session.get('authentifie'):
        return redirect(url_for('authentification', auth='login-required'))

    if session.get('id_utilisateur') != id and session.get('role') != 'admin':
        return "Accès refusé : Vous n'avez pas les permissions nécessaires pour supprimer ce compte.", 403

    if id == 1:
        return "Erreur : Ce compte est insupprimable.", 403

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM utilisateurs WHERE id = ?', (id,))
        conn.commit()
        conn.close()

    # Si l'utilisateur supprimé est celui connecté, déconnectez-le
        if session.get('id_utilisateur') == id:
            session.clear()

        if session.get('role') == 'admin':
            return redirect(url_for('sessions', request='success'))
        else:
            return redirect(url_for('accueil', request='success'))
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return "Erreur interne du serveur.", 500



@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect(url_for('accueil', logout='success'))

@app.template_filter('format_datetime')
def format_datetime(value, format="%d/%m/%Y à %H:%M"):
    try:
        # Conversion explicite en chaîne
        value = str(value)
        date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return date.strftime(format)
    except (ValueError, TypeError):
        return value  # Retourne la valeur brute si le parsing échoue

@app.route('/utilisateur/')
def redirection_utilisateur():
    if not session.get('authentifie') or session.get('role') != 'utilisateur':
        return redirect(url_for('authentification', auth='login-required'))

    id_utilisateur = session.get('id_utilisateur')
    return redirect(url_for('utilisateur', post_id=id_utilisateur))

    # Récupérez l'ID de l'utilisateur connecté depuis la session
    id_utilisateur = session.get('id_utilisateur')

    # Redirigez l'utilisateur vers /utilisateur/<ID>
    return redirect(url_for('utilisateur', post_id=id_utilisateur))

@app.route('/utilisateur/<int:post_id>')
def utilisateur(post_id):
    if not session.get('authentifie'):
        return redirect(url_for('authentification', auth='login-required'))

    if session.get('id_utilisateur') != post_id and session.get('role') != 'admin':
        return "Accès refusé : Vous ne pouvez pas consulter cette page car elle ne correspond pas à votre compte utilisateur.", 403

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Récupérer les informations de l'utilisateur
        cursor.execute('SELECT * FROM utilisateurs WHERE id = ?', (post_id,))
        utilisateur = cursor.fetchone()

        # Récupérer les emprunts de l'utilisateur
        cursor.execute('''
            SELECT e.id AS id_emprunt, r.titre, r.auteur, r.type_ressource, e.date_emprunt
            FROM exemplaires e
            JOIN ressources r ON e.ressource_id = r.id
            WHERE e.utilisateur_id = ? AND e.emprunte = 1
        ''', (post_id,))
        emprunts = cursor.fetchall()

        conn.close()

        emprunts = [
            {
                'id_emprunt': e[0],
                'titre': e[1],
                'auteur': e[2],
                'type': e[3],
                'date_emprunt': datetime.strptime(e[4], "%Y-%m-%d").strftime("%d/%m/%Y") if e[4] else "N/A"
            }
            for e in emprunts
        ]

        if utilisateur:
            # Rendre une page différente si c'est un admin
            if session.get('role') == 'admin':
                return render_template(
                    'Fiche.html', 
                    utilisateur={
                        'id': utilisateur[0],
                        'nom': utilisateur[1],
                        'prenom': utilisateur[2],
                        'email': utilisateur[3],
                        'nombre_emprunts_en_cours': utilisateur[5],
                        'total_emprunts': utilisateur[6],
                        'created': utilisateur[7]
                    },
                    emprunts=emprunts
                )
            else:
                return render_template(
                    'utilisateur.html', 
                    utilisateur={
                        'id': utilisateur[0],
                        'nom': utilisateur[1],
                        'prenom': utilisateur[2],
                        'email': utilisateur[3],
                        'nombre_emprunts_en_cours': utilisateur[5],
                        'total_emprunts': utilisateur[6],
                        'created': utilisateur[7]
                    },
                    emprunts=emprunts
                )
        else:
            return "Erreur : Utilisateur non trouvé.", 404
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return "Erreur interne du serveur.", 500


@app.route('/administrateur')
def administrateur():
    # Vérifier l'authentification et le rôle d'administrateur
    if not session.get('authentifie') or session.get('role') != 'admin':
        return "Accès refusé : Vous n'êtes pas autorisé à accéder à cette page.", 403

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Calcul des statistiques

    cursor.execute("SELECT COUNT(*) FROM utilisateurs")
    nombre_comptes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT ressource_id) FROM exemplaires")
    nombre_references = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM exemplaires WHERE emprunte = 0")
    livres_en_stock = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM exemplaires WHERE emprunte = 1")
    livres_empruntes = cursor.fetchone()[0]

    conn.close()

    # Passer les données au template
    return render_template(
        'administrateur.html',
        nombre_comptes=nombre_comptes,
        nombre_references=nombre_references,
        livres_en_stock=livres_en_stock,
        livres_empruntes=livres_empruntes
    )

@app.route('/sessions')
def sessions():

    if not session.get('authentifie') or session.get('role') != 'admin':
        return "Accès refusé : Vous n'êtes pas autorisé à accéder à cette page.", 403

    try:

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Calcul des statistiques générales

        cursor.execute("SELECT COUNT(*) FROM utilisateurs")
        nombre_utilisateurs = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(nombre_emprunts_en_cours) FROM utilisateurs")
        moyenne_emprunts = round(cursor.fetchone()[0] or 0, 2)

        cursor.execute("SELECT COUNT(*) FROM exemplaires WHERE emprunte = 1")
        livres_empruntes = cursor.fetchone()[0]

        # Récupération des utilisateurs

        cursor.execute("""
            SELECT id, nom, prenom, email, created, nombre_emprunts_en_cours, total_emprunts
            FROM utilisateurs
        """)
        utilisateurs = cursor.fetchall()

        utilisateurs_list = []
        for u in utilisateurs:
            try:
                created = datetime.strptime(u[4], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y à %H:%M")
            except ValueError:
                created = u[4] 

            utilisateurs_list.append({
                'id': u[0],
                'nom': u[1],
                'prenom': u[2],
                'email': u[3],
                'created': created,
                'emprunts_en_cours': u[5],
                'total_emprunts': u[6]
            })

        conn.close()

        return render_template(
            'Sessions.html',
            nombre_utilisateurs=nombre_utilisateurs,
            moyenne_emprunts=moyenne_emprunts,
            livres_empruntes=livres_empruntes,
            utilisateurs=utilisateurs_list
        )
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return "Erreur interne du serveur.", 500

@app.route('/stocks')
def stocks():
    if not session.get('authentifie') or session.get('role') != 'admin':
        return "Accès refusé : Vous n'êtes pas autorisé à accéder à cette page.", 403

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Statistiques générales

        cursor.execute("SELECT COUNT(DISTINCT ressource_id) FROM exemplaires")
        nombre_references = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM exemplaires WHERE emprunte = 0")
        livres_en_stock = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM exemplaires WHERE emprunte = 1")
        livres_empruntes = cursor.fetchone()[0] or 0

        # Liste des exemplaires

        cursor.execute("""
            SELECT 
                e.id AS exemplaire_id, 
                r.titre, 
                r.auteur, 
                r.type_ressource, 
                r.date_publication,
                e.emprunte, 
                u.id AS utilisateur_id, 
                u.nom AS utilisateur_nom, 
                u.prenom AS utilisateur_prenom
            FROM exemplaires e
            JOIN ressources r ON e.ressource_id = r.id
            LEFT JOIN utilisateurs u ON e.utilisateur_id = u.id
        """)
        exemplaires = cursor.fetchall()

        ressources = [
            {
                'id': row[0],
                'titre': row[1],
                'auteur': row[2],
                'type': row[3],
                'date_publication': datetime.strptime(row[4], "%Y-%m-%d").strftime("%d/%m/%Y") if row[4] else "N/A",
                'emprunte': row[5],
                'emprunte_par': {
                    'id': row[6],
                    'nom': row[7],
                    'prenom': row[8]
                } if row[6] else None
            }
            for row in exemplaires
        ]

        cursor.execute("SELECT id, nom, prenom FROM utilisateurs")
        utilisateurs = cursor.fetchall()
        utilisateurs_list = [
            {'id': u[0], 'nom': u[1], 'prenom': u[2]} for u in utilisateurs
        ]

        conn.close()


        return render_template(
            'Stocks.html',
            nombre_references=nombre_references,
            livres_en_stock=livres_en_stock,
            livres_empruntes=livres_empruntes,
            exemplaires=ressources,
            utilisateurs=utilisateurs_list 
        )
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return "Erreur interne du serveur.", 500


@app.route('/stocks/ajouter', methods=['POST'])
def ajouter_livre():

    if not session.get('authentifie') or session.get('role') != 'admin':
        return "Accès refusé : Cette page est réservée aux administrateurs.", 403

    try:
        # Récupération des données du formulaire
        titre = request.form['titre']
        auteur = request.form['auteur']
        genre = request.form['type']
        date_publication = request.form['date_publication']
        nombre_exemplaires = int(request.form['nombre_exemplaires'])

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Ajout de la ressource dans la table ressources

        cursor.execute('''
            INSERT INTO ressources (titre, auteur, type_ressource, date_publication, nombre_exemplaires_total, nombre_emprunts_total)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (titre, auteur, genre, date_publication, nombre_exemplaires))

        # Récupérer l'ID de la ressource nouvellement créée

        ressource_id = cursor.lastrowid

        # Ajouter les exemplaires dans la table exemplaires

        for _ in range(nombre_exemplaires):
            cursor.execute('''
                INSERT INTO exemplaires (ressource_id, utilisateur_id, emprunte, date_emprunt)
                VALUES (?, NULL, 0, NULL)
            ''', (ressource_id,))

        conn.commit()
        conn.close()

        return redirect(url_for('stocks', request='success'))
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return "Erreur interne du serveur.", 500
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return "Erreur interne du serveur.", 500


@app.route('/stocks/supprimer/<int:id>', methods=['POST'])
def supprimer_exemplaire(id):
    if not session.get('authentifie') or session.get('role') != 'admin':
        return "Accès refusé : Cette page est réservée aux administrateurs.", 403

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Vérifier si l'exemplaire existe

        cursor.execute('SELECT id, ressource_id, emprunte FROM exemplaires WHERE id = ?', (id,))
        exemplaire = cursor.fetchone()

        if not exemplaire:
            conn.close()
            return "Erreur : Exemplaire introuvable.", 404

        if exemplaire[2]: 
            conn.close()
            return "Impossible de supprimer un exemplaire actuellement emprunté.", 403

        # Supprimer l'exemplaire
        
        cursor.execute('DELETE FROM exemplaires WHERE id = ?', (id,))
        conn.commit()
        conn.close()

        return redirect(url_for('stocks', request='success'))
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return "Erreur interne du serveur.", 500



#********

@app.route("/conditions-d'utilisations")
def conditions_utilisation():
    return render_template("Conditions d'utilisations.html")

@app.route('/politique-de-confidentialité')
def politique_confidentialite():
    return render_template('Politique de confidentialité.html')

@app.route('/mentions-légales')
def mentions_legales():
    return render_template('Mentions légales.html')

@app.route('/rgpd')
def rgpd():
    return render_template('RGPD.html')

@app.route('/à-propos')
def a_propos():
    return render_template('À propos.html')


#Rédamarrage de FLask

if __name__ == '__main__':
    app.run(debug=True)
