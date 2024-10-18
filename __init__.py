from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour vérifier si l'administrateur est authentifié
def admin_authentifie():
    return session.get('authentifie')

# Fonction pour vérifier si un utilisateur est authentifié
def user_authentifie():
    return session.get('authentification_utilisateur')

def est_connecte():
    return admin_authentifie() or user_authentifie()

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if admin_authentifie():
        return "<h1>Bonjour, vous êtes connecté en tant qu'administrateur</h1>"
    if user_authentifie():
        return "<h1>Bonjour, vous êtes connecté à votre espace utilisateur</h1>"
    else:
        return redirect(url_for('authentification'))

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password': # password à cacher
            session['authentifie'] = True
            session['authentification_utilisateur'] = False
            return redirect(url_for('lecture'))
        elif request.form['username'] == 'user' and request.form['password'] == '12345': # password à cacher
            session['authentification_utilisateur'] = True
            session['authentifie'] = False
            return redirect(url_for('lecture'))
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/fiche_nom/<string:nom>', methods=['GET', 'POST'])
def FicheNom(nom):
    if user_authentifie():
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
        data = cursor.fetchall()
        conn.close()
        return render_template('read_data.html', data=data)
    else:
        return f'<h1>Bonjour, vous n\'êtes pas connecté à votre espace utilisateur</h1><p><a href="{url_for("authentification")}">Authentification</a></p>', 403

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')

# Ajouter un contrôle d'authentification pour l'administrateur (enregistrement de livres)
@app.route('/enregistrer_livre', methods=['GET'])
def formulaire_livre():
    return render_template('formulaire_livre.html')

@app.route('/enregistrer_livre', methods=['POST'])
def enregistrer_livre():
    if not admin_authentifie():
        return f'<h1>Accès refusé, vous devez être administrateur pour enregistrer un livre.<p><a href="{url_for("authentification")}">Authentification</a></p>', 403
    titre = request.form['titre']
    auteur = request.form['auteur']
    quantite = request.form['quantite']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO livres (titre, auteur, quantite) VALUES (?, ?, ?)', (titre, auteur, quantite))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Livre ajouté avec succès'})

# Ajouter un contrôle d'authentification pour l'administrateur (suppression de livres)
@app.route('/supprimer_livre/<int:livre_id>', methods=['DELETE'])
def supprimer_livre(livre_id):
    if not admin_authentifie():
        return f'<h1>Accès refusé, vous devez être administrateur pour supprimer un livre.<p><a href="{url_for("authentification")}">Authentification</a></p>', 403
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM livres WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Livre supprimé avec succès'})

# Ajouter un contrôle d'authentification pour l'administrateur (gestion des utilisateurs)
@app.route('/gestion_utilisateurs', methods=['GET'])
def gestion_utilisateurs():
    if not admin_authentifie():
        return f'<h1>Accès refusé, vous devez être administrateur pour gérer les utilisateurs.<p><a href="{url_for("authentification")}">Authentification</a></p>', 403
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients')
    utilisateurs = cursor.fetchall()
    conn.close()
    
    return render_template('gestion_utilisateurs.html', utilisateurs=utilisateurs)

# Ajouter un contrôle d'authentification pour l'administrateur (gestion des stocks)
@app.route('/gestion_stocks', methods=['GET'])
def gestion_stocks():
    if not admin_authentifie():
        return f'<h1>Accès refusé, vous devez être administrateur pour gérer les utilisateurs.<p><a href="{url_for("authentification")}">Authentification</a></p>', 403
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres')
    stocks = cursor.fetchall()
    conn.close()
    
    return render_template('gestion_stocks.html', stocks=stocks)

# Ajouter un contrôle d'authentification pour les utilisateurs (recherche de livres disponibles)
@app.route('/recherche_livres', methods=['GET'])
def recherche_livres():
    if not est_connecte():
        return f'<h1>Accès refusé, vous devez être connecté pour gérer les livres.<p><a href="{url_for("authentification")}">Authentification</a></p>', 403
    
    titre = request.args.get('titre')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if titre:
        cursor.execute('SELECT * FROM livres WHERE titre LIKE ?', ('%' + titre + '%',))
    else:
        cursor.execute('SELECT * FROM livres WHERE quantite > 0')
    
    data = cursor.fetchall()
    conn.close()
    
    return render_template('read_data.html', data=data)

# Ajouter un contrôle d'authentification pour les utilisateurs (emprunter un livre)
@app.route('/emprunter_livre/<int:livre_id>', methods=['POST'])
def emprunter_livre(livre_id):
    if not est_connecte():
        return f'<h1>Accès refusé, vous devez être connecté pour gérer les livres.<p><a href="{url_for("authentification")}">Authentification</a></p>', 403
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT quantite FROM livres WHERE id = ?', (livre_id,))
    livre = cursor.fetchone()
    
    if livre and livre[0] > 0:
        cursor.execute('UPDATE livres SET quantite = quantite - 1 WHERE id = ?', (livre_id,))
        conn.commit()
        conn.close()
        return '<h1>Livre emprunté avec succès</h1>'
    else:
        conn.close()
        return '<h1>Livre non disponible</h1>', 400

if __name__ == "__main__":
    app.run(debug=True)
