from DatabaseManager import DatabaseManager


# Gestion des catégories
class CategoryManager:
    """
    Classe pour gérer les catégories, y compris leur récupération et ajout.
    """
    def __init__(self):
        # Charge toutes les catégories depuis la base de données
        self.categories = DatabaseManager.get_all_categories()

    def get_category_names(self):
        """
        Retourne une liste des noms des catégories.
        """
        return [category[1] for category in self.categories]

    def add_category(self, name):
        """
        Ajoute une catégorie et met à jour la liste des catégories.
        """
        DatabaseManager.add_category(name)
        self.categories = DatabaseManager.get_all_categories()