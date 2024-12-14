import sqlite3 

# Gestion de la base de données
class DatabaseManager:
    """
    Classe pour gérer la base de données SQLite utilisée pour stocker les catégories et les cartes flash.
    """
    @staticmethod
    def setup_database():
        conn = sqlite3.connect('flashcards.db')
        conn.execute('PRAGMA foreign_keys = ON;')  # Activer les clés étrangères
        cursor = conn.cursor()

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
                review_score INTEGER DEFAULT 0,  -- Champ pour le suivi des performances
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        # Table des statistiques globales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_sessions INTEGER DEFAULT 0,
                total_correct INTEGER DEFAULT 0,
                total_incorrect INTEGER DEFAULT 0,
                total_reviewed INTEGER DEFAULT 0
            )
        ''')
        # Initialiser les statistiques globales si elles n'existent pas
        cursor.execute('''
            INSERT OR IGNORE INTO global_stats (id, total_sessions, total_correct, total_incorrect, total_reviewed)
            VALUES (1, 0, 0, 0, 0)
        ''')

        conn.commit()
        conn.close()
    
    @staticmethod
    def add_category(name):
        """
        Ajoute une nouvelle catégorie à la base de données.
        Si la catégorie existe déjà, aucune action n'est effectuée.
        """
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_categories():
        """
        Récupère toutes les catégories de la base de données.
        """
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories")
        categories = cursor.fetchall()
        conn.close()
        return categories

    @staticmethod
    def add_card(category_id, question, answer):
        """
        Ajoute une nouvelle carte flash à une catégorie spécifique.
        """
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO flashcards (category_id, question, answer) VALUES (?, ?, ?)",
                       (category_id, question, answer))
        conn.commit()
        conn.close()

    @staticmethod
    def get_cards_by_category(category_id):
        """
        Récupère toutes les cartes d'une catégorie donnée triées par score.
        """
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, question, answer, review_score FROM flashcards WHERE category_id = ? ORDER BY review_score ASC", (category_id,))
        cards = cursor.fetchall()
        conn.close()
        return cards

    @staticmethod
    def delete_card(card_id):
        """
        Supprime une carte flash de la base de données en fonction de son ID.
        """
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def update_card_score(card_id, is_correct):
        """
        Met à jour le score de la carte en fonction de la réponse.
        """
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        if is_correct:
            cursor.execute("UPDATE flashcards SET review_score = review_score + 1 WHERE id = ?", (card_id,))
        else:
            cursor.execute("UPDATE flashcards SET review_score = 0 WHERE id = ?", (card_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_global_stats():
        """
        Récupère les statistiques globales.
        """
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute('SELECT total_sessions, total_correct, total_incorrect, total_reviewed FROM global_stats WHERE id = 1')
        stats = cursor.fetchone()
        conn.close()
        return stats

    @staticmethod
    def update_global_stats(correct, incorrect, reviewed):
        """
        Met à jour les statistiques globales en ajoutant les statistiques d'une session.
        """
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE global_stats
            SET total_sessions = total_sessions + 1,
                total_correct = total_correct + ?,
                total_incorrect = total_incorrect + ?,
                total_reviewed = total_reviewed + ?
            WHERE id = 1
        ''', (correct, incorrect, reviewed))
        conn.commit()
        conn.close()