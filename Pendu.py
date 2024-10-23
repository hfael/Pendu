import customtkinter as ctk
import string
from PIL import Image
import os
import threading
import time
import random
import json

current_directory = os.path.dirname(os.path.abspath(__file__))
image_directory = f'{current_directory}\\Images'
playerdata_directory = f"{current_directory}\\playerdata"
mot_choisi = ""
error_score = 0
lettres_trouvees = []
boutons = {}
game_state = "null"
username = ""
highest_winrate = 0
list_word = []

def init():
    global mot_choisi
    global error_score
    global lettres_trouvees
    global boutons
    global game_state
    global list_word
    mot_choisi = ""
    error_score = 0
    lettres_trouvees = []
    boutons = {}
    game_state = "null"
    list_word = []


class Pendu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jeu du Pendu")
        self.geometry("600x250")
        self.resizable(width="False", height="False")
        self.connexionPage()

    def connexionPage(self):
        if not os.path.exists(playerdata_directory):
            os.makedirs(playerdata_directory)
        self.name_label = ctk.CTkLabel(master=self, text="Nom d'utilisateur")
        self.name_label.pack()
        self.name_label.place(x=250, y=50)
        self.name_entry = ctk.CTkEntry(master=self, placeholder_text="Écrire ici...", width=200)
        self.name_entry.pack()
        self.name_entry.place(x=200, y=80)
        self.play_button = ctk.CTkButton(master=self, text="Jouer", command=self.connexion, width=75)
        self.play_button.pack()
        self.play_button.place(x=260, y=120)
        self.log_label = ctk.CTkLabel(master=self, text="", text_color="red")
    def connexion(self):
        try:
            self.name_value = self.name_entry.get()
            if len(self.name_value) > 3:
                if self.name_value.isalpha():
                    global username
                    self.log_label.configure(text="Connexion en cours", text_color="green")
                    self.log_label.pack()
                    self.log_label.place(x=240, y=150)
                    username = self.name_value.lower()
                    if not os.path.exists(f"{playerdata_directory}\\{username}.json"):
                        with open(f"{playerdata_directory}\\{username}.json", "w") as file:
                            data = {
                                "wins": 0,
                                "looses": 0,
                            }
                            json.dump(data, file, indent=4)
                    self.clear_window()
                    self.widgets()
                    self.start_game()
                else:
                    self.log_label.configure(text="Nom d'utilisateur n'est pas une chaine alphanumérique !", text_color="red")
                    self.log_label.pack()
                    self.log_label.place(x=150, y=150)
            else:
                self.log_label.configure(text="Nom d'utilisateur incorrecte !", text_color="red")
                self.log_label.pack()
                self.log_label.place(x=215, y=150)
        except Exception as e:
            print(f"Erreur {e}")
    def widgets(self):
        self.place_button()
        
        self.no_error_img = Image.open(f"{image_directory}\\no_error.png")
        self.no_error_image = ctk.CTkImage(self.no_error_img, size=(25, 25))
        x_default = 25

        for i in range(6):
            self.no_error = ctk.CTkLabel(master=self, image=self.no_error_image, text="")
            self.no_error.pack()
            self.no_error.place(x=x_default, y=210)
            x_default += 23

        self.win_percent = self.get_winrate()
        self.winrate_label = ctk.CTkLabel(master=self, text=f"Winrate: {self.win_percent}%")
        self.winrate_label.pack()
        self.winrate_label.place(x=250, y=7)
    def place_button(self):
        global boutons
        letters = list(string.ascii_uppercase)
        x_position = 370
        y_position = 95

        for index, letter in enumerate(letters):
            if letter != 'I':
                button = ctk.CTkButton(master=self, text=letter, command=lambda l=letter: self.press(l), width=10)
            else:
                button = ctk.CTkButton(master=self, text=letter, command=lambda l=letter: self.press(l), width=23)
            button.pack()
            button.place(x=x_position, y=y_position)
            boutons[letter] = button    
            if letter == 'G' or letter == 'N' or letter == 'U':
                x_position = 370
                y_position += 35
                if letter == 'U':
                    x_position = 400
            else:
               x_position += 30  

    def press(self, button):
        global game_state
        global list_word
        if game_state == "InGame":
            global lettres_trouvees
            print(button)
            letter_in_word = list(mot_choisi.upper())
            if button in letter_in_word:
                lettres_trouvees.append(button)
                boutons[button].configure(fg_color="green", state="disabled")
                self.display_correct_letters()
                print(lettres_trouvees)
                if set(lettres_trouvees) == set(list_word):
                    game_state = "End"
                    threading.Thread(target=self.end_game, args=("win",)).start()
                    print("Victoire ! ct facile")
                    pass
            else:
                boutons[button].configure(fg_color="red", state="disabled")
                self.new_error()
                pass
        else:
            print("Erreur: la partie n'est pas/plus en cours...")

    def start_game(self):
        global error_score
        global game_state
        game_state = "InGame"
        error_score = 0
        self.get_support()
        self.choose_word()
        self.get_underscore()

    def get_underscore(self):
        self.underscore_img = Image.open(f"{image_directory}\\underscore.png")

        self.word_lenght = len(mot_choisi)
        underscore_width = 30
        underscore_height = 30
        total_underscores_width = self.word_lenght * underscore_width
        start_x = 455 - (total_underscores_width / 2)
        self.underscore_image = ctk.CTkImage(self.underscore_img, size=(underscore_width, underscore_height))

        for i in range(self.word_lenght):
            self.underscore_label = ctk.CTkLabel(master=self, image=self.underscore_image, text="")
            self.underscore_label.pack()
            self.underscore_label.place(x=start_x + i * underscore_width, y=40)

    def new_error(self):
        global error_score
        error_score += 1
        self.error_img = Image.open(f"{image_directory}\\error.png")
        self.error_image = ctk.CTkImage(self.error_img, size=(25, 25))
        self.error = ctk.CTkLabel(master=self, image=self.error_image, text="")
        self.error.pack()
        self.x_error = 25
        self.y_error = 210
        if error_score == 1:
            self.error.place(x=self.x_error, y=self.y_error)
            self.cadavre("head")
        elif error_score == 2:
            self.error.place(x=self.x_error+23, y=self.y_error)
            self.cadavre("body")
        elif error_score == 3:
            self.error.place(x=self.x_error+46, y=self.y_error)
            self.cadavre("arm1")
        elif error_score == 4:
            self.error.place(x=self.x_error+69, y=self.y_error)
            self.cadavre("arm2")
        elif error_score == 5:
            self.error.place(x=self.x_error+92, y=self.y_error)
            self.cadavre("feet1")
        elif error_score == 6:
            self.error.place(x=self.x_error+115, y=self.y_error)
            self.cadavre("feet2")
            print("Vous avez perdu la partie !")
            threading.Thread(target=self.end_game, args=("loose",)).start()

    def cadavre(self, part):
        match part:
            case "head":
                self.head_img = Image.open(f"{image_directory}\\head_dead.png")
                self.head_image = ctk.CTkImage(self.head_img, size=(50, 50))
                self.head = ctk.CTkLabel(master=self, image=self.head_image, text="")
                self.head.pack()
                self.head.place(x=175, y=60)
            case "body":
                self.body_img = Image.open(f"{image_directory}\\body.png")
                self.body_image = ctk.CTkImage(self.body_img, size=(5, 60))
                self.body = ctk.CTkLabel(master=self, image=self.body_image, text="")
                self.body.pack()
                self.body.place(x=197, y=106)
            case "arm1":
                self.arm1_img = Image.open(f"{image_directory}\\right.png")
                self.arm1_image = ctk.CTkImage(self.arm1_img, size=(50, 50))
                self.arm1 = ctk.CTkLabel(master=self, image=self.arm1_image, text="")
                self.arm1.pack()
                self.arm1.place(x=202, y=113)
            case "arm2":
                self.arm2_img = Image.open(f"{image_directory}\\left.png")
                self.arm2_image = ctk.CTkImage(self.arm2_img, size=(50, 50))
                self.arm2 = ctk.CTkLabel(master=self, image=self.arm2_image, text="")
                self.arm2.pack()
                self.arm2.place(x=147, y=113)
            case "feet1":
                self.feet1_img = Image.open(f"{image_directory}\\left.png")
                self.feet1_image = ctk.CTkImage(self.feet1_img, size=(45, 45))
                self.feet1 = ctk.CTkLabel(master=self, image=self.feet1_image, text="")
                self.feet1.pack()
                self.feet1.place(x=151, y=163)
            case "feet2": 
                self.feet2_img = Image.open(f"{image_directory}\\right.png")
                self.feet2_image = ctk.CTkImage(self.feet2_img, size=(45, 45))
                self.feet2 = ctk.CTkLabel(master=self, image=self.feet2_image, text="")
                self.feet2.pack()
                self.feet2.place(x=202, y=163)
    def choose_word(self):
        global mot_choisi
        global list_word
        with open(f"{current_directory}\\words.txt", "r") as file: 
            allText = file.read() 
            words = list(map(str, allText.split()))
            mot_choisi = random.choice(words)
            mot_choisi2 = ''.join(sorted(set(mot_choisi), key=mot_choisi.index))
            mot_choisi2 = mot_choisi.upper()
            list_word = list(mot_choisi2)
            print(mot_choisi)

    def display_correct_letters(self):
        global mot_choisi
        global lettres_trouvees
        self.word_lenght = len(mot_choisi)
        underscore_width = 30
        total_underscores_width = self.word_lenght * underscore_width
        start_x = 455 - (total_underscores_width / 2)

        for i in range(self.word_lenght):
            if mot_choisi[i].upper() in lettres_trouvees:
                self.lettre_label = ctk.CTkLabel(master=self, text=mot_choisi[i].upper(), font=("Helvetica", 26))
                self.lettre_label.place(x=start_x + i * underscore_width + 7, y=35)
    def get_support(self):
        self.support_img = Image.open(f"{image_directory}\\support.png")
        self.support_image = ctk.CTkImage(self.support_img, size=(160, 160))
        self.support_label = ctk.CTkLabel(master=self, image=self.support_image, text="")
        self.support_label.pack()
        self.support_label.place(x=45, y=40)
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
    def get_winrate(self):
        global username
        with open(f"{playerdata_directory}\\{username}.json") as file:
            data = json.load(file)
        win = data["wins"]
        loose = data["looses"]
        if loose > 0 and win > 0:
            winrate = (win / (win + loose)) * 100
            return round(winrate, 2)
        else:
            if win > 0 and loose == 0:
                return 100
            elif win == 0 and loose > 0:
                return 0
    def end_game(self, state):
        global game_state
        game_state = "End"
        self.clear_window()
        global username
        self.text_label = ctk.CTkLabel(master=self, text="", font=("Arial", 30))
        self.text_description = ctk.CTkLabel(master=self, text="")
        self.text_label.pack()
        self.text_label.place(x=250, y=50)
        with open(f"{playerdata_directory}\\{username}.json") as fichier:
            data = json.load(fichier)
        if state == "win":
            data["wins"] += 1
            self.text_label.configure(text="Victoire !")
            self.text_description.configure(text="Vous avez gagné la partie !")
            self.text_description.pack()
            self.text_description.place(x=230, y=85)
        elif state == "loose":
            data["looses"] += 1
            self.text_label.configure(text="Défaite !")
            self.text_description.configure(text="Vous avez perdu la partie !")
            self.text_description.pack()
            self.text_description.place(x=230, y=85)
        with open(f"{playerdata_directory}\\{username}.json", "w") as file:
            json.dump(data, file, indent=4)
        self.play_again = ctk.CTkButton(master=self, text="Rejouer", fg_color="green", command=lambda:self.end_button("replay"), width=50)
        self.leave = ctk.CTkButton(master=self, text="Quitter", fg_color="red", command=lambda:self.end_button("end"), width=50)
        self.play_again.pack()
        self.play_again.place(x=200, y=120)
        self.leave.pack()
        self.leave.place(x=350, y=120)
    def end_button(self, text):
        if text == "replay":
            init()
            self.clear_window()
            self.widgets()
            self.start_game()
        else:
            self.destroy()

if __name__ == "__main__":
    application = Pendu()
    application.mainloop()