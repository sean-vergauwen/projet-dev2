import sqlite3 

# Gestion de la base de données
class DatabaseManager:
    """
    Classe pour gérer la base de données SQLite utilisée pour stocker les catégories et les cartes flash.
    """
    @staticmethod
    def setup_database():
        """
        Crée les tables nécessaires dans la base de données si elles n'existent pas déjà.
        """
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
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
        Récupère toutes les cartes d'une catégorie donnée.
        """
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, question, answer FROM flashcards WHERE category_id = ?", (category_id,))
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