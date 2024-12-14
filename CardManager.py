from DatabaseManager import DatabaseManager


# Gestion des cartes flash
class CardManager:
    """
    Classe pour gérer les cartes flash, y compris leur navigation et mise à jour.
    """
    def __init__(self):
        self.db_manager = DatabaseManager()  # Instance de DatabaseManager
        self.cards = []  # Liste des cartes flash
        self.current_card_index = 0  # Index de la carte actuelle

    def load_cards(self, category_id):
        """
        Charge toutes les cartes d'une catégorie spécifique et les trie par score croissant.
        """
        self.cards = self.db_manager.get_cards_by_category(category_id)
        self.cards.sort(key=lambda card: card[3])  # Trier par review_score
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
        Augmente le score de la carte actuelle après une réponse correcte.
        """
        if self.cards:
            card_id = self.cards[self.current_card_index][0]
            self.db_manager.update_card_score(card_id, True)
            self.cards.pop(self.current_card_index)
            # Ajuster l'index si nécessaire
            if self.current_card_index >= len(self.cards):
                self.current_card_index = 0  # Retourner au début si l'index dépasse

    def mark_card_as_incorrect(self):
        """
        Passe à la carte suivante après avoir enregistré le score incorrect.
        """
        if self.cards:
            card_id = self.cards[self.current_card_index][0]
            self.db_manager.update_card_score(card_id, False)
            # Passer à la carte suivante uniquement si la liste n'est pas vide
            if len(self.cards) > 1:
                self.current_card_index = (self.current_card_index + 1) % len(self.cards)
            else:
                self.current_card_index = 0