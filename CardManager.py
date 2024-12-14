from DatabaseManager import DatabaseManager


# Gestion des cartes flash
class CardManager:
    """
    Classe pour gérer les cartes flash, y compris leur navigation et mise à jour.
    """
    def __init__(self):
        self.cards = []  # Liste des cartes flash
        self.current_card_index = 0  # Index de la carte actuelle

    def load_cards(self, category_id):
        """
        Charge toutes les cartes d'une catégorie spécifique.
        """
        self.cards = DatabaseManager.get_cards_by_category(category_id)
        self.current_card_index = 0

    def get_next_card(self):
        """
        Retourne la carte actuelle. Si aucune carte n'est disponible, retourne None.
        """
        if not self.cards:
            return None
        return self.cards[self.current_card_index]

    def mark_card_as_correct(self):
        """
        Supprime la carte actuelle après qu'elle a été marquée comme correcte.
        """
        if self.cards:
            self.cards.pop(self.current_card_index)

    def mark_card_as_incorrect(self):
        """
        Passe à la carte suivante après qu'elle a été marquée comme incorrecte.
        """
        if self.cards:
            self.current_card_index = (self.current_card_index + 1) % len(self.cards)