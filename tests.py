import unittest
import os
from DatabaseManager import DatabaseManager
from CategoryManager import CategoryManager
from CardManager import CardManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        """Création d'une db temporaire pour les tests"""
        self.test_db_name = 'test_flashcards.db'
        self.db_manager = DatabaseManager(self.test_db_name)
        self.db_manager.setup_database()

    def tearDown(self):
        """Destruction de la db temporaire pour les tests"""
        self.db_manager._disconnect()
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)

    def test_add_category(self):
        """Test d'ajout d'une catégorie"""
        self.db_manager.add_category("Test Category")
        categories = self.db_manager.get_all_categories()
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0][1], "Test Category")

    def test_add_card(self):
        """Test d'ajout d'une flashcard"""
        self.db_manager.add_category("Test Category")
        categories = self.db_manager.get_all_categories()
        category_id = categories[0][0]
        
        self.db_manager.add_card(category_id, "Test Question", "Test Answer")
        cards = self.db_manager.get_cards_by_category(category_id)
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0][1], "Test Question")
        self.assertEqual(cards[0][2], "Test Answer")

    def test_update_card_score(self):
        """Test de mise à jour des scores"""
        self.db_manager.add_category("Test Category")
        category_id = self.db_manager.get_all_categories()[0][0]
        self.db_manager.add_card(category_id, "Test Question", "Test Answer")
        card_id = self.db_manager.get_cards_by_category(category_id)[0][0]
        
        # Test correct answer
        self.db_manager.update_card_score(card_id, True)
        card = self.db_manager.get_cards_by_category(category_id)[0]
        self.assertEqual(card[3], 1)  # Check review_score
        
        # Test incorrect answer
        self.db_manager.update_card_score(card_id, False)
        card = self.db_manager.get_cards_by_category(category_id)[0]
        self.assertEqual(card[3], 0)  # Score should reset to 0

    def test_delete_card(self):
        """Test supprimer une flashcard"""
        self.db_manager.add_category("Test Category")
        category_id = self.db_manager.get_all_categories()[0][0]
        self.db_manager.add_card(category_id, "Test Question", "Test Answer")
        card_id = self.db_manager.get_cards_by_category(category_id)[0][0]
        
        self.db_manager.delete_card(card_id)
        cards = self.db_manager.get_cards_by_category(category_id)
        self.assertEqual(len(cards), 0)

    def test_global_stats(self):
        """Test du tracking des stats globales"""
        initial_stats = self.db_manager.get_global_stats()
        self.assertEqual(initial_stats[0], 0)  # total_sessions
        
        self.db_manager.update_global_stats(5, 2, 7)
        updated_stats = self.db_manager.get_global_stats()
        self.assertEqual(updated_stats[0], 1)  # total_sessions
        self.assertEqual(updated_stats[1], 5)  # total_correct
        self.assertEqual(updated_stats[2], 2)  # total_incorrect
        self.assertEqual(updated_stats[3], 7)  # total_reviewed

class TestCategoryManager(unittest.TestCase):
    def setUp(self):
        """Création d'une db temporaire pour les tests"""
        self.test_db_name = 'test_flashcards.db'
        self.db_manager = DatabaseManager(self.test_db_name)
        self.db_manager.setup_database()
        self.category_manager = CategoryManager()
        # Override the database connection to use test database
        self.category_manager.db_manager = self.db_manager

    def tearDown(self):
        """Destruction de la db temporaire pour les tests"""
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)

    def test_add_category(self):
        """Test d'ajout d'une catégorie"""
        initial_count = len(self.category_manager.get_category_names())
        self.category_manager.add_category("Test Category")
        updated_count = len(self.category_manager.get_category_names())
        self.assertEqual(updated_count, initial_count + 1)
        self.assertIn("Test Category", self.category_manager.get_category_names())

    def test_get_category_names(self):
        """Test requêtes catégories"""
        test_categories = ["Category 1", "Category 2", "Category 3"]
        for category in test_categories:
            self.category_manager.add_category(category)
        
        retrieved_categories = self.category_manager.get_category_names()
        for category in test_categories:
            self.assertIn(category, retrieved_categories)

class TestCardManager(unittest.TestCase):
    def setUp(self):
        """Création d'une db temporaire pour les tests'"""
        self.test_db_name = 'test_flashcards.db'
        self.db_manager = DatabaseManager(self.test_db_name)
        self.db_manager.setup_database()
        self.card_manager = CardManager()
        # Override the database connection
        self.card_manager.db_manager = self.db_manager
        
        # Add a test category and some cards
        self.db_manager.add_category("Test Category")
        self.category_id = self.db_manager.get_all_categories()[0][0]
        self.db_manager.add_card(self.category_id, "Q1", "A1")
        self.db_manager.add_card(self.category_id, "Q2", "A2")

    def tearDown(self):
        """Destruction de la db temporaire pour les tests"""
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)

    def test_load_cards(self):
        """Test du chargment des cartes d'une catégorie"""
        self.card_manager.load_cards(self.category_id)
        self.assertEqual(len(self.card_manager.cards), 2)
        self.assertEqual(self.card_manager.current_card_index, 0)

    def test_get_next_card(self):
        """Test recevoir prochaine carte"""
        self.card_manager.load_cards(self.category_id)
        first_card = self.card_manager.get_next_card()
        self.assertIsNotNone(first_card)
        self.assertEqual(first_card[1], "Q1")  # Check question

    def test_mark_card_as_correct(self):
        """Test carte correcte"""
        self.card_manager.load_cards(self.category_id)
        initial_count = len(self.card_manager.cards)
        self.card_manager.mark_card_as_correct()
        self.assertEqual(len(self.card_manager.cards), initial_count - 1)

    def test_mark_card_as_incorrect(self):
        """Test carte incorrecte"""
        self.card_manager.load_cards(self.category_id)
        initial_index = self.card_manager.current_card_index
        self.card_manager.mark_card_as_incorrect()
        # For two cards, after marking incorrect, index should be 1
        self.assertEqual(self.card_manager.current_card_index, (initial_index + 1) % len(self.card_manager.cards))

if __name__ == '__main__':
    unittest.main()
