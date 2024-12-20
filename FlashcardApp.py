import tkinter as tk
from tkinter import messagebox
import time
from DatabaseManager import DatabaseManager
from CategoryManager import CategoryManager
from CardManager import CardManager

# Interface utilisateur principale
class FlashcardApp:
    """
    Classe principale pour l'application Flashcard avec interface Tkinter.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcards")
        self.root.geometry("600x500")
        self.root.config(bg="#F4F4F9")  # Couleur de fond de l'application

        self.db_manager = DatabaseManager()
        self.db_manager.setup_database()

        # Gestion des catégories et des cartes
        self.category_manager = CategoryManager()
        self.card_manager = CardManager()
        self.selected_category_id = None

        # Statistiques
        self.start_time = None  # Temps de début de la révision
        self.total_cards_reviewed = 0  # Nombre total de cartes révisées
        self.correct_answers = 0  # Nombre de réponses correctes
        self.incorrect_answers = 0  # Nombre de réponses incorrectes

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_widgets()
        self.display_global_stats()

    def create_widgets(self):
        """
        Crée tous les widgets de l'interface utilisateur.
        """
        # Interface pour ajouter des catégories
        self.category_entry = tk.Entry(self.root, width=40, bg="#E9ECEF", fg="#495057", font=("Arial", 12))
        self.category_entry.pack(pady=5)
        tk.Button(self.root, text="Ajouter la catégorie", command=self.add_category,
                  bg="#007BFF", fg="white", font=("Arial", 12)).pack(pady=5)

        # Menu de sélection des catégories
        self.category_var = tk.StringVar(self.root)
        self.category_var.set("Sélectionner une catégorie")
        categories = self.category_manager.get_category_names()
        if not categories:
            categories = ["Aucune catégorie disponible"]
        self.category_menu = tk.OptionMenu(self.root, self.category_var, *categories, command=self.select_category)

        self.category_menu.config(bg="#E9ECEF", fg="#495057", font=("Arial", 12))
        self.category_menu.pack(pady=5)

        # Interface pour ajouter des cartes
        self.question_entry = tk.Entry(self.root, width=40, bg="#E9ECEF", fg="#495057", font=("Arial", 12))
        self.question_entry.pack(pady=5)
        self.answer_entry = tk.Entry(self.root, width=40, bg="#E9ECEF", fg="#495057", font=("Arial", 12))
        self.answer_entry.pack(pady=5)
        tk.Button(self.root, text="Ajouter la carte", command=self.add_card,
                  bg="#28A745", fg="white", font=("Arial", 12)).pack(pady=5)

        # Interface pour la révision
        self.question_label = tk.Label(self.root, text="", wraplength=400, bg="#F4F4F9", font=("Arial", 14))
        self.question_label.pack(pady=10)
        self.answer_label = tk.Label(self.root, text="", wraplength=400, bg="#F4F4F9", font=("Arial", 12))
        self.answer_label.pack(pady=5)

        # Boutons pour gérer les actions de révision
        tk.Button(self.root, text="Révéler la réponse", command=self.reveal_answer,
                  bg="#FFC107", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Correct", command=self.mark_correct,
                  bg="#17A2B8", fg="white", font=("Arial", 12)).pack(side="left", padx=5, pady=5)
        tk.Button(self.root, text="Mauvais", command=self.mark_incorrect,
                  bg="#DC3545", fg="white", font=("Arial", 12)).pack(side="left", padx=5, pady=5)

        # Bouton pour supprimer une carte
        tk.Button(self.root, text="Supprimer la carte", command=self.delete_current_card,
                  bg="#6C757D", fg="white", font=("Arial", 12)).pack(pady=5)

        # Boutons pour afficher les cartes et les statistiques
        tk.Button(self.root, text="Voir toutes les cartes et catégories",
                  command=self.show_all_cards, bg="#6F42C1", fg="white", font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Voir les statistiques de la session",
                  command=self.show_statistics, bg="#343A40", fg="white", font=("Arial", 12)).pack(pady=10)

    def start_review(self):
        """
        Enregistre le temps de début de la révision.
        """
        self.start_time = time.time()

    def add_category(self):
        """
        Ajoute une nouvelle catégorie à partir de l'entrée utilisateur.
        """
        category_name = self.category_entry.get().strip()  # Supprime les espaces inutiles
        if not category_name:  # Vérifie si le champ est vide
            messagebox.showwarning("Erreur", "Le nom de la catégorie ne peut pas être vide.")
            return
        self.category_manager.add_category(category_name)
        self.update_category_menu()
        messagebox.showinfo("Succès", "Catégorie ajoutée avec succès.")
        self.category_entry.delete(0, tk.END)

    def update_category_menu(self):
        """
        Met à jour le menu déroulant des catégories avec les nouvelles catégories ajoutées.
        """
        menu = self.category_menu["menu"]
        menu.delete(0, "end")
        categories = self.category_manager.get_category_names()
        if not categories:
            categories = ["Aucune catégorie disponible"]
        for category in categories:
            menu.add_command(label=category, command=lambda value=category: self.select_category(value))

    def select_category(self, category_name):
        """
        Sélectionne une catégorie et charge ses cartes flash pour la révision.
        """
        category = next((cat for cat in self.category_manager.categories if cat[1] == category_name), None)
        if category:
            self.selected_category_id = category[0]
            self.card_manager.load_cards(self.selected_category_id)
            self.start_review()
            self.show_next_card()

    def add_card(self):
        """
        Ajoute une carte flash à la catégorie sélectionnée.
        """
        question = self.question_entry.get().strip()
        answer = self.answer_entry.get().strip()
        if not question or not answer:
            messagebox.showwarning("Erreur", "Les champs question et réponse ne peuvent pas être vides.")
            return
        if self.selected_category_id:
            self.db_manager.add_card(self.selected_category_id, question, answer)
            messagebox.showinfo("Succès", "Carte ajoutée avec succès.")
            self.question_entry.delete(0, tk.END)
            self.answer_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Erreur", "Veuillez sélectionner une catégorie avant d'ajouter une carte.")

    def reveal_answer(self):
        """
        Affiche la réponse de la carte actuelle.
        """
        card = self.card_manager.get_next_card()
        if card:
            self.answer_label.config(text=f"Réponse : {card[2]}")

    def mark_correct(self):
        """
        Marque la carte actuelle comme correcte et passe à la suivante.
        """
        if not self.card_manager.cards:
            messagebox.showinfo("Révision terminée", "Vous avez terminé toutes les cartes.")
            self.question_label.config(text="Aucune carte restante.")
            self.answer_label.config(text="")
            return

        self.correct_answers += 1
        self.total_cards_reviewed += 1
        self.card_manager.mark_card_as_correct()
        self.show_next_card()

    def mark_incorrect(self):
        """
        Marque la carte actuelle comme incorrecte et passe à la suivante.
        """
        if not self.card_manager.cards:
            messagebox.showinfo("Révision terminée", "Vous avez terminé toutes les cartes.")
            self.question_label.config(text="Aucune carte restante.")
            self.answer_label.config(text="")
            return

        self.incorrect_answers += 1
        self.total_cards_reviewed += 1
        self.card_manager.mark_card_as_incorrect()
        self.show_next_card()

    def delete_current_card(self):
        """
        Supprime la carte actuelle de la base de données et passe à la suivante.
        """
        card = self.card_manager.get_next_card()
        if card:
            self.db_manager.delete_card(card[0])
            self.card_manager.load_cards(self.selected_category_id)
            self.show_next_card()

    def show_next_card(self):
        """
        Affiche la prochaine carte à réviser ou indique qu'il n'y a plus de cartes.
        """
        if not self.card_manager.cards:  # Si aucune carte n'est disponible
            self.question_label.config(text="Aucune carte disponible.")
            self.answer_label.config(text="")
            return

        card = self.card_manager.get_next_card()
        if card:
            self.question_label.config(text=f"Question : {card[1]}")
            self.answer_label.config(text="Réponse masquée")

    def show_all_cards(self):
        """
        Ouvre une fenêtre affichant toutes les cartes par catégorie.
        """
        popup = tk.Toplevel(self.root)
        popup.title("Toutes les cartes et catégories")
        popup.geometry("400x400")

        # Liste des catégories
        category_listbox = tk.Listbox(popup, selectmode="single", width=50, height=10)
        category_listbox.pack(pady=5)

        for category in self.category_manager.categories:
            category_listbox.insert(tk.END, category[1])

        # Fonction pour afficher les cartes d'une catégorie sélectionnée
        def on_category_select(event):
            selected_category = category_listbox.get(category_listbox.curselection())
            category = next((cat for cat in self.category_manager.categories if cat[1] == selected_category), None)
            if category:
                cards = self.db_manager.get_cards_by_category(category[0])
                card_listbox.delete(0, tk.END)
                for card in cards:
                    card_info = f"{card[1]} - {card[2]}"
                    card_listbox.insert(tk.END, card_info)

        category_listbox.bind("<<ListboxSelect>>", on_category_select)

        # Liste des cartes
        card_listbox = tk.Listbox(popup, selectmode="single", width=50, height=10)
        card_listbox.pack(pady=5)

    def show_statistics(self):
        """
        Affiche les statistiques de révision dans une fenêtre pop-up.
        """
        popup = tk.Toplevel(self.root)
        popup.title("Statistiques")
        popup.geometry("400x300")
        popup.config(bg="#F4F4F9")

        # Calcul des statistiques
        time_elapsed = time.time() - self.start_time if self.start_time else 0
        time_elapsed_minutes = round(time_elapsed / 60, 2)
        success_rate = (self.correct_answers / self.total_cards_reviewed) * 100 if self.total_cards_reviewed else 0

        stats = [
            f"Temps passé en révision : {time_elapsed_minutes:.2f} minutes",
            f"Nombre total de cartes révisées : {self.total_cards_reviewed}",
            f"Nombre de bonnes réponses : {self.correct_answers}",
            f"Nombre de mauvaises réponses : {self.incorrect_answers}",
            f"Taux de réussite : {success_rate:.2f}%",
        ]

        # Affichage des statistiques
        for stat in stats:
            tk.Label(popup, text=stat, font=("Arial", 12), bg="#F4F4F9", wraplength=350).pack(pady=5)

        # Bouton pour fermer la fenêtre
        tk.Button(popup, text="Fermer", command=popup.destroy,
                  bg="#DC3545", fg="white", font=("Arial", 12)).pack(pady=10)
    
    def display_global_stats(self):
        """
        Affiche les statistiques globales au démarrage.
        """
        stats = self.db_manager.get_global_stats()
        if stats:
            messagebox.showinfo(
                "Statistiques Globales",
                f"Sessions totales : {stats[0]}\n"
                f"Bonnes réponses : {stats[1]}\n"
                f"Mauvaises réponses : {stats[2]}\n"
                f"Cartes révisées : {stats[3]}"
            )
            self.root.after(100, self.reset_focus)

    def save_session_stats(self):
        """
        Ajoute les statistiques de la session actuelle aux statistiques globales.
        """
        self.db_manager.update_global_stats(
            self.correct_answers,
            self.incorrect_answers,
            self.total_cards_reviewed
        )

    def on_closing(self):
        """
        Gère la fermeture de l'application.
        """
        self.save_session_stats()  # Enregistre les statistiques de la session
        self.root.destroy()  # Ferme la fenêtre

    def reset_focus(self):
        """
        Forcer le focus sur la fenêtre principale et le champ texte après un délai.
        """
        self.root.focus_force()  # Garantir que la fenêtre principale est au premier plan
        self.category_entry.focus_set()  # Donner le focus au champ de texte pour qu'il soit cliquable