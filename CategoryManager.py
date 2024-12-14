from DatabaseManager import DatabaseManager


# Gestion des catégories
class CategoryManager:
    """
    Classe pour gérer les catégories, y compris leur récupération et ajout.
    """
    def __init__(self):
        # Charger toutes les catégories depuis une instance de DatabaseManager
        self.db_manager = DatabaseManager()
        self.categories = self.db_manager.get_all_categories()

    def get_category_names(self):
        """
        Retourne une liste des noms des catégories.
        """
        return [category[1] for category in self.categories]

    def add_category(self, name):
        """
        Ajoute une catégorie et met à jour la liste des catégories.
        """
        self.db_manager.add_category(name)
        self.categories = self.db_manager.get_all_categories()