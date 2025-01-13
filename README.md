# Contenu du fichier formaté selon la structure demandée
project_readme = """
# Liberia - Système de Gestion de Bibliothèque

## Description

**Liberia** est un projet développé en janvier 2025 dans le cadre d’un projet académique. Ce système permet une gestion numérique et sécurisée des ressources littéraires, facilitant le prêt et la restitution des ouvrages.

### Objectifs du projet
- Faciliter l’accès au catalogue des ressources d’une bibliothèque.
- Intégrer un système de gestion des emprunts et des retours.
- Permettre la gestion des utilisateurs et des ressources via une interface administrateur.
- Respecter les normes RGPD pour la gestion des données personnelles.

---

## Fonctionnalités

### Utilisateur standard
- Consulter le catalogue.
- Emprunter et restituer des ressources.
- Gérer les informations personnelles.
- Consulter l’historique des emprunts.

### Administrateur
- Gérer les utilisateurs (ajout, modification, suppression).
- Ajouter, modifier et supprimer des ressources.
- Accéder aux statistiques d’utilisation et au tableau de bord.
- **Restriction** : Les administrateurs ne peuvent pas emprunter de ressources car ce compte est un compte de gestion.

### Conformité RGPD
- Accès à toutes les pages légales : mentions légales, conditions d'utilisation, politique de confidentialité, etc.

---

## Routes de l’application

### Accès public (sans authentification)
- **/** : Page d’accueil.
- **/catalogue** : Consultation du catalogue.
- **/inscription** : Création de compte utilisateur.
- **/authentification** : Connexion utilisateur/administrateur.
- **Pages légales** :
  - /mentions-legales
  - /conditions-d'utilisations
  - /politique-de-confidentialite
  - /rgpd
  - /à-propos

### Accès utilisateur authentifié
- **/emprunter** : Voir les ressources disponibles à emprunter.
- **/restituer** : Gestion des emprunts en cours.
- **/utilisateur/<post_id>** : Espace personnel.
- **/utilisateur/<post_id>/supprimer** : Suppression de compte.

### Accès administrateur
- **/administrateur** : Tableau de bord.
- **/stocks** : Gestion des stocks et des ressources.
- **/stocks/ajouter** : Ajouter une nouvelle ressource.
- **/stocks/supprimer/<id>** : Supprimer une ressource.

---

## Structure de la base de données

### Table : utilisateurs
| Champ                  | Type      | Description                                      |
|------------------------|-----------|--------------------------------------------------|
| `id`                  | INTEGER   | Identifiant unique de l'utilisateur.            |
| `nom`                 | TEXT      | Nom de l'utilisateur.                           |
| `prenom`              | TEXT      | Prénom de l'utilisateur.                        |
| `email`               | TEXT      | Adresse email unique.                           |
| `password`            | TEXT      | Mot de passe de l'utilisateur.                  |
| `nombre_emprunts_en_cours` | INTEGER | Nombre de ressources empruntées.               |
| `total_emprunts`      | INTEGER   | Total des emprunts réalisés.                    |
| `role`                | TEXT      | Rôle (utilisateur ou admin).                    |

### Table : ressources
| Champ                   | Type      | Description                                     |
|-------------------------|-----------|-------------------------------------------------|
| `id`                   | INTEGER   | Identifiant unique de la ressource.            |
| `titre`                | TEXT      | Titre de la ressource.                         |
| `auteur`               | TEXT      | Auteur de la ressource.                        |
| `type_ressource`       | TEXT      | Genre de la ressource.                         |
| `date_publication`     | DATE      | Date de publication.                           |
| `nombre_exemplaires_total` | INTEGER | Nombre total d'exemplaires disponibles.       |
| `nombre_emprunts_total`| INTEGER   | Nombre total d'emprunts.                       |

### Table : exemplaires
| Champ             | Type      | Description                                      |
|-------------------|-----------|--------------------------------------------------|
| `id`             | INTEGER   | Identifiant unique de l'exemplaire.             |
| `ressource_id`   | INTEGER   | Lien vers la ressource correspondante.           |
| `utilisateur_id` | INTEGER   | Identifiant de l'utilisateur emprunteur (ou NULL).|
| `emprunte`       | BOOLEAN   | Indique si l'exemplaire est emprunté.            |
| `date_emprunt`   | DATE      | Date d'emprunt de l'exemplaire.                 |

### Table : emprunts
| Champ            | Type      | Description                                      |
|------------------|-----------|--------------------------------------------------|
| `id`            | INTEGER   | Identifiant unique de l'emprunt.                |
| `utilisateur_id`| INTEGER   | Identifiant de l'utilisateur ayant emprunté.     |
| `ressource_id`  | INTEGER   | Identifiant de la ressource empruntée.           |
| `date_emprunt`  | DATE      | Date d'emprunt.                                  |

---

## Technologies utilisées

- **Backend** : Python (Flask)
- **Frontend** : HTML, CSS (Poppins)
- **Base de données** : SQLite
- **Hébergement** : Local ou serveur web
"""

# Enregistrer dans un fichier README.md
project_file_path = "/mnt/data/README_Liberia.md"
with open(project_file_path, "w") as project_file:
    project_file.write(project_readme)

project_file_path
