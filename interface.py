import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

# base de données
def setup_database():
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

setup_database()

# fct pour ajouter une nouvelle catégorie
def add_category(name):
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

# fct pour obtenir toutes les catégories
def get_all_categories():
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    conn.close()
    return categories

# fct oour Ajouter une nouvelle carte
def add_card(category_id, question, answer):
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO flashcards (category_id, question, answer) VALUES (?, ?, ?)",
                   (category_id, question, answer))
    conn.commit()
    conn.close()

# fct pour obtenir les cartes par catégorie
def get_cards_by_category(category_id):
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, answer FROM flashcards WHERE category_id = ?", (category_id,))
    cards = cursor.fetchall()
    conn.close()
    return cards

# fct pour supprimer une carte
def delete_card(card_id):
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))
    conn.commit()
    conn.close()

# fct pour modifier une carte
def update_card(card_id, new_question, new_answer):
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE flashcards SET question = ?, answer = ? WHERE id = ?", (new_question, new_answer, card_id))
    conn.commit()
    conn.close()

# Interface utilisateur
class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcards")
        self.root.geometry("600x500")
        self.root.config(bg="#F4F4F9")  # Couleur de fond générale

        self.categories = get_all_categories()
        self.selected_category_id = None
        self.cards = []
        self.current_card_index = 0
        self.studied_cards = []

        # Interface pour ajouter des catégories
        self.category_entry = tk.Entry(root, width=40, bg="#E9ECEF", fg="#495057", font=("Arial", 12))
        self.category_entry.pack(pady=5)
        tk.Button(root, text="Ajouter la catégorie", command=self.add_category, bg="#007BFF", fg="white", font=("Arial", 12)).pack(pady=5)

        # Menu de sélection des catégories
        self.category_var = tk.StringVar(root)
        self.category_var.set("Sélectionner une catégorie")
        self.category_menu = tk.OptionMenu(root, self.category_var, *self.get_category_names(), command=self.select_category)
        self.category_menu.config(bg="#E9ECEF", fg="#495057", font=("Arial", 12))
        self.category_menu.pack(pady=5)

        # Interface pour ajouter des cartes
        self.question_entry = tk.Entry(root, width=40, bg="#E9ECEF", fg="#495057", font=("Arial", 12))
        self.question_entry.pack(pady=5)
        self.answer_entry = tk.Entry(root, width=40, bg="#E9ECEF", fg="#495057", font=("Arial", 12))
        self.answer_entry.pack(pady=5)
        tk.Button(root, text="Ajouter la carte", command=self.add_card, bg="#28A745", fg="white", font=("Arial", 12)).pack(pady=5)

        # Interface de révision
        self.question_label = tk.Label(root, text="", wraplength=400, bg="#F4F4F9", font=("Arial", 14))
        self.question_label.pack(pady=10)
        self.answer_label = tk.Label(root, text="", wraplength=400, bg="#F4F4F9", font=("Arial", 12))
        self.answer_label.pack(pady=5)
        self.show_answer = False

        tk.Button(root, text="Révéler la réponse", command=self.reveal_answer, bg="#FFC107", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="Correct", command=self.mark_correct, bg="#17A2B8", fg="white", font=("Arial", 12)).pack(side="left", padx=10, pady=10)
        tk.Button(root, text="Mauvais", command=self.mark_incorrect, bg="#DC3545", fg="white", font=("Arial", 12)).pack(side="left", padx=10, pady=10)
        tk.Button(root, text="Supprimer la carte", command=self.delete_current_card, bg="#6C757D", fg="white", font=("Arial", 12)).pack(pady=10)

        # Affiche toutes les cartes et catégories dans une fenêtre pop-up
        self.show_all_button = tk.Button(root, text="Voir toutes les cartes et catégories", command=self.show_all_cards, bg="#6F42C1", fg="white", font=("Arial", 12))
        self.show_all_button.pack(pady=10)

    def get_category_names(self):
        return [category[1] for category in self.categories]

    def add_category(self):
        category_name = self.category_entry.get()
        if category_name:
            add_category(category_name)
            messagebox.showinfo("Succès", "Catégorie ajoutée avec succès")
            self.categories = get_all_categories()
            self.category_var.set("Sélectionner une catégorie")
            self.update_category_menu()
            self.category_entry.delete(0, tk.END)

    def update_category_menu(self):
        menu = self.category_menu["menu"]
        menu.delete(0, "end")
        for category in self.get_category_names():
            menu.add_command(label=category, command=lambda value=category: self.select_category(value))

    def select_category(self, category_name):
        category = next((cat for cat in self.categories if cat[1] == category_name), None)
        if category:
            self.selected_category_id = category[0]
            self.cards = get_cards_by_category(self.selected_category_id)
            self.current_card_index = 0
            self.studied_cards = []
            self.show_next_card()

    def add_card(self):
        question = self.question_entry.get()
        answer = self.answer_entry.get()
        if self.selected_category_id and question and answer:
            add_card(self.selected_category_id, question, answer)
            messagebox.showinfo("Succès", "Carte ajoutée avec succès")
            self.cards = get_cards_by_category(self.selected_category_id)
            self.question_entry.delete(0, tk.END)
            self.answer_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Erreur", "Veuillez sélectionner une catégorie et remplir les champs")

    def show_next_card(self):
        if not self.cards:
            self.question_label.config(text="Aucune carte disponible.")
            self.answer_label.config(text="")
            return

        if len(self.studied_cards) == len(self.cards):
            messagebox.showinfo("Félicitations", "Vous avez terminé toutes les cartes de cette catégorie !")
            self.question_label.config(text="Révision terminée.")
            self.answer_label.config(text="")
            return

        self.show_answer = False
        card = self.cards[self.current_card_index]
        self.current_card_id = card[0]
        self.question_label.config(text=f"Question : {card[1]}")
        self.answer_label.config(text="Cliquez pour révéler la réponse")

    def reveal_answer(self):
        if not self.show_answer and self.cards:
            card = self.cards[self.current_card_index]
            self.answer_label.config(text=f"Réponse : {card[2]}")
            self.show_answer = True

    def mark_correct(self):
        if self.cards:
            self.studied_cards.append(self.cards[self.current_card_index])
            self.current_card_index = (self.current_card_index + 1) % len(self.cards)
            self.show_next_card()

    def mark_incorrect(self):
        if self.cards:
            self.cards.append(self.cards.pop(self.current_card_index))
            self.show_next_card()

    def delete_current_card(self):
        if self.cards:
            card_id = self.current_card_id
            delete_card(card_id)
            self.cards = get_cards_by_category(self.selected_category_id)
            self.show_next_card()

    def show_all_cards(self):
        popup = tk.Toplevel(self.root)
        popup.title("Toutes les cartes et catégories")
        popup.geometry("400x400")

        category_listbox = tk.Listbox(popup, selectmode="single", width=50, height=10)
        category_listbox.pack(pady=5)

        for category in self.categories:
            category_listbox.insert(tk.END, category[1])

        def on_category_select(event):
            selected_category = category_listbox.get(category_listbox.curselection())
            category = next((cat for cat in self.categories if cat[1] == selected_category), None)
            if category:
                cards = get_cards_by_category(category[0])
                card_listbox.delete(0, tk.END)
                for card in cards:
                    card_info = f"{card[1]} - {card[2]}"
                    card_listbox.insert(tk.END, card_info)

        category_listbox.bind("<<ListboxSelect>>", on_category_select)

        card_listbox = tk.Listbox(popup, selectmode="single", width=50, height=10)
        card_listbox.pack(pady=5)

        popup.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
