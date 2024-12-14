import sqlite3

class DatabaseManager:
    """
    Classe pour gérer la base de données SQLite utilisée pour stocker les catégories et les cartes flash.
    """
    def __init__(self, db_name='flashcards.db'):
        """
        Initialise la connexion à la base de données.
        :param db_name: Nom du fichier de la base de données SQLite.
        """
        self._db_name = db_name  # Nom de la base de données encapsulé
        self._connection = None  # Connexion privée à la base de données

    def _connect(self):
        """
        Établit une connexion à la base de données.
        """
        if not self._connection:
            self._connection = sqlite3.connect(self._db_name)
            self._connection.execute('PRAGMA foreign_keys = ON;')  # Activer les clés étrangères

    def _disconnect(self):
        """
        Ferme la connexion à la base de données.
        """
        if self._connection:
            self._connection.close()
            self._connection = None

    def setup_database(self):
        """
        Crée les tables nécessaires dans la base de données si elles n'existent pas déjà.
        """
        self._connect()
        cursor = self._connection.cursor()

        # Création des tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                review_score INTEGER DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_sessions INTEGER DEFAULT 0,
                total_correct INTEGER DEFAULT 0,
                total_incorrect INTEGER DEFAULT 0,
                total_reviewed INTEGER DEFAULT 0
            )
        ''')
        # Initialisation des statistiques globales si elles n'existent pas
        cursor.execute('''
            INSERT OR IGNORE INTO global_stats (id, total_sessions, total_correct, total_incorrect, total_reviewed)
            VALUES (1, 0, 0, 0, 0)
        ''')

        self._connection.commit()
        self._disconnect()

    def add_category(self, name):
        """
        Ajoute une nouvelle catégorie à la base de données.
        """
        self._connect()
        cursor = self._connection.cursor()
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
        self._connection.commit()
        self._disconnect()

    def get_all_categories(self):
        """
        Récupère toutes les catégories de la base de données.
        """
        self._connect()
        cursor = self._connection.cursor()
        cursor.execute("SELECT id, name FROM categories")
        categories = cursor.fetchall()
        self._disconnect()
        return categories

    def add_card(self, category_id, question, answer):
        """
        Ajoute une nouvelle carte flash à une catégorie spécifique.
        """
        self._connect()
        cursor = self._connection.cursor()
        cursor.execute("INSERT INTO flashcards (category_id, question, answer) VALUES (?, ?, ?)",
                       (category_id, question, answer))
        self._connection.commit()
        self._disconnect()

    def get_cards_by_category(self, category_id):
        """
        Récupère toutes les cartes d'une catégorie donnée triées par score.
        """
        self._connect()
        cursor = self._connection.cursor()
        cursor.execute("SELECT id, question, answer, review_score FROM flashcards WHERE category_id = ? ORDER BY review_score ASC", (category_id,))
        cards = cursor.fetchall()
        self._disconnect()
        return cards

    def delete_card(self, card_id):
        """
        Supprime une carte flash de la base de données en fonction de son ID.
        """
        self._connect()
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))
        self._connection.commit()
        self._disconnect()

    def update_card_score(self, card_id, is_correct):
        """
        Met à jour le score de la carte en fonction de la réponse.
        """
        self._connect()
        cursor = self._connection.cursor()
        if is_correct:
            cursor.execute("UPDATE flashcards SET review_score = review_score + 1 WHERE id = ?", (card_id,))
        else:
            cursor.execute("UPDATE flashcards SET review_score = 0 WHERE id = ?", (card_id,))
        self._connection.commit()
        self._disconnect()

    def get_global_stats(self):
        """
        Récupère les statistiques globales.
        """
        self._connect()
        cursor = self._connection.cursor()
        cursor.execute('SELECT total_sessions, total_correct, total_incorrect, total_reviewed FROM global_stats WHERE id = 1')
        stats = cursor.fetchone()
        self._disconnect()
        return stats

    def update_global_stats(self, correct, incorrect, reviewed):
        """
        Met à jour les statistiques globales en ajoutant les statistiques d'une session.
        """
        self._connect()
        cursor = self._connection.cursor()
        cursor.execute('''
            UPDATE global_stats
            SET total_sessions = total_sessions + 1,
                total_correct = total_correct + ?,
                total_incorrect = total_incorrect + ?,
                total_reviewed = total_reviewed + ?
            WHERE id = 1
        ''', (correct, incorrect, reviewed))
        self._connection.commit()
        self._disconnect()