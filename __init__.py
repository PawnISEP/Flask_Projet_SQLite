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

@app.route('/consulter_client/<int:client_id>', methods=['GET'])
def consulter_client(client_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
    client_data = cursor.fetchone()
    conn.close()
    if client_data:
        return render_template('consulter_client.html', client=client_data)
    else:
        return f"<h1>Client avec l'ID {client_id} non trouvé</h1>", 404

@app.route('/supprimer_client/<int:client_id>', methods=['POST'])
def supprimer_client(client_id):
    if not admin_authentifie():
        return f"<h1>Accès interdit. Vous devez être administrateur pour effectuer cette action.</h1>", 403

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
    client_data = cursor.fetchone()

    if not client_data:
        conn.close()
        return f"<h1>Client avec l'ID {client_id} non trouvé</h1>", 404

    cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()

    return f"<h1>Client avec l'ID {client_id} supprimé avec succès</h1><p><a href='{url_for('ReadBDD')}'>Retour à la liste des clients</a></p>"

