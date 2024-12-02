from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Définir une clé API pour l'administrateur
ADMIN_API_KEY = "votre_cle_secrete"

# Fonction pour vérifier si l'administrateur est authentifié
def admin_authentifie():
    return session.get('authentifie') or request.headers.get('X-API-KEY') == ADMIN_API_KEY

# Fonction pour vérifier si un utilisateur est authentifié
def user_authentifie():
    return session.get('authentification_utilisateur')

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':  # password à cacher
            session['authentifie'] = True
            session['authentification_utilisateur'] = False
            return redirect(url_for('lecture'))
        elif request.form['username'] == 'user' and request.form['password'] == '12345':  # password à cacher
            session['authentification_utilisateur'] = True
            session['authentifie'] = False
            return redirect(url_for('lecture'))
        else:
            return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

@app.route('/lecture')
def lecture():
    if admin_authentifie():
        return "<h1>Bonjour, vous êtes connecté en tant qu'administrateur</h1>"
    if user_authentifie():
        return "<h1>Bonjour, vous êtes connecté à votre espace utilisateur</h1>"
    else:
        return redirect(url_for('authentification'))

# Route pour ajouter un client
@app.route('/ajouter_client', methods=['POST'])
def ajouter_client():
    if not admin_authentifie():  # Vérifie si l'utilisateur est admin via clé API ou session
        return jsonify({'error': 'Non autorisé'}), 403

    data = request.json
    nom = data.get('nom')
    prenom = data.get('prenom')
    adresse = data.get('adresse')

    if not nom or not prenom or not adresse:
        return jsonify({'error': 'Les champs nom, prenom et adresse sont obligatoires'}), 400

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)',
        (nom, prenom, adresse)
    )
    conn.commit()
    client_id = cursor.lastrowid
    conn.close()

    return jsonify({'message': 'Client ajouté avec succès', 'client_id': client_id}), 201

# API consultation : Lire tous les clients
@app.route('/clients', methods=['GET'])
def lire_clients():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, created, nom, prenom, adresse FROM clients')
    data = cursor.fetchall()
    conn.close()

    clients = [
        {
            'id': row[0],
            'created': row[1],
            'nom': row[2],
            'prenom': row[3],
            'adresse': row[4]
        }
        for row in data
    ]
    return jsonify(clients), 200

# Route pour supprimer un client
@app.route('/supprimer_client/<int:client_id>', methods=['DELETE'])
def supprimer_client(client_id):
    if not admin_authentifie():  # Vérifie si l'utilisateur est admin via clé API ou session
        return jsonify({'error': 'Non autorisé'}), 403

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
    client_data = cursor.fetchone()

    if not client_data:
        conn.close()
        return jsonify({'error': f'Client avec l\'ID {client_id} non trouvé'}), 404

    cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Client avec l\'ID {client_id} supprimé avec succès'}), 200

# API consultation détaillée : Récupérer un client par ID
@app.route('/fiche_client/<int:post_id>', methods=['GET'])
def fiche_client(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchone()
    conn.close()

    if data:
        client = {
            'id': data[0],
            'created': data[1],
            'nom': data[2],
            'prenom': data[3],
            'adresse': data[4]
        }
        return jsonify(client), 200
    else:
        return jsonify({'error': f'Client avec l\'ID {post_id} non trouvé'}), 404

if __name__ == '__main__':
    app.run(debug=True)
