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
        Augmente le score de la carte actuelle après qu'elle a été marquée comme correcte.
        """
        if self.cards:
            card_id = self.cards[self.current_card_index][0]
            DatabaseManager.update_card_score(card_id, True)
            self.cards.pop(self.current_card_index)

    def mark_card_as_incorrect(self):
        """
        Ne modifie pas le score et passe à la carte suivante.
        """
        if self.cards:
            card_id = self.cards[self.current_card_index][0]
            DatabaseManager.update_card_score(card_id, False)
            self.current_card_index = (self.current_card_index + 1) % len(self.cards)