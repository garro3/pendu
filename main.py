import pygame
import random
import sys
import os

def resource_path(relative_path):
    """
    Trouve le chemin correct d'un fichier, que ce soit en .py ou .exe PyInstaller.
    """
    if hasattr(sys, "_MEIPASS"):  # Si c'est un .exe PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

with open(resource_path("words_alpha.txt"), "r", encoding="utf-8") as f:
    words = [line.strip() for line in f if line.strip()]
    word_to_guess = random.choice(words) if words else None

with open(resource_path("best_score.txt"), "r", encoding="utf-8") as f:
    best_score = f.read().strip()
    best_score = int(best_score) if best_score.isdigit() else None


# Constantes
FILENAME = resource_path("words_alpha.txt")
BEST_SCORE_FILE = resource_path("best_score.txt")
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

def choose_word():
    """Choisit un mot aléatoire dans words_alpha.txt"""
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            words = [line.strip().lower() for line in f if line.strip()]
        words = [w for w in words if w.isalpha() and 3 <= len(w) <= 7]
        return random.choice(words)
    except Exception as e:
        print("Erreur lors du chargement des mots :", e)
        sys.exit(1)

def get_best_score():
    try:
        with open(BEST_SCORE_FILE, "r", encoding="utf-8") as f:
            score = f.read().strip()
            return int(score) if score.isdigit() else None
    except:
        return None

def save_best_score(score, best_score):
    try:
        with open(BEST_SCORE_FILE, "w", encoding="utf-8") as f:
            f.write(str(score))
    except FileNotFoundError:
        best_score = 999
    # except Exception as e:
    #     print("Impossible de sauvegarder le score :", e)


def draw_hangman(screen, erreurs): # Dessine le pendu selon le nombre d'erreurs
    if erreurs >= 1:  # Poteau vertical
        pygame.draw.line(screen, RED, (400, 200), (400, 450), width=3)
    if erreurs >= 2:  # Poteau horizontal
        pygame.draw.line(screen, RED, (300, 200), (400, 200), width=3)
    if erreurs >= 3:  # Corde
        pygame.draw.line(screen, RED, (300, 200), (300, 225), width=3)
    if erreurs >= 4:  # Tête
        pygame.draw.circle(screen, RED, (300, 250), 25, width=3)
    if erreurs >= 5:  # Corps
        pygame.draw.line(screen, RED, (300, 275), (300, 350), width=3)
    if erreurs >= 6:  # Bras gauche
        pygame.draw.line(screen, RED, (300, 290), (260, 320), width=3)
    if erreurs >= 7:  # Bras droit
        pygame.draw.line(screen, RED, (300, 290), (340, 320), width=3)
    if erreurs >= 8:  # Jambe gauche
        pygame.draw.line(screen, RED, (300, 350), (270, 400), width=3)
    if erreurs >= 9:  # Jambe droite
        pygame.draw.line(screen, RED, (300, 350), (330, 400), width=3)
    if erreurs >= 10:  # Base
        pygame.draw.line(screen, RED, (350, 450), (450, 450), width=3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jeu du Pendu")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # Charger l'image de fond si elle existe
    try:
        background = pygame.image.load(resource_path("bgimage.png"))
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print("Impossible de charger bgimage.png :", e)
        background = None  # fond blanc par défaut

    # Variables du jeu
    word = choose_word()
    guess_word = ["_"] * len(word)
    lettres_proposees = []
    erreurs = 0
    max_erreurs = 10
    running = True
    game_over = False
    victory = False
    input_text = ""
    message = ""
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Valider l'entrée
                        if input_text:
                            letter = input_text.lower()
                            
                            # Vérifier si c'est le mot entier
                            if len(letter) == len(word) and letter == word:
                                victory = True
                                game_over = True
                                message = f"C'est gagné! Le mot était {word}"
                                best_score = get_best_score()
                                if best_score is None or erreurs < best_score:
                                    save_best_score(erreurs)
                                    message += f"\nNouveau meilleur score: {erreurs} erreurs!"
                            # Vérifier si c'est une lettre valide
                            elif len(letter) == 1 and letter.isalpha():
                                if letter not in lettres_proposees:
                                    lettres_proposees.append(letter)
                                    if letter in word:
                                        # Mettre à jour guess_word
                                        for i in range(len(word)):
                                            if word[i] == letter:
                                                guess_word[i] = letter
                                        # Vérifier la victoire
                                        if "_" not in guess_word:
                                            victory = True
                                            game_over = True
                                            message = f"C'est gagné! Le mot était {word}"
                                            best_score = get_best_score()
                                            if best_score is None or erreurs < best_score:
                                                save_best_score(erreurs)
                                                message += f"\nNouveau meilleur score: {erreurs} erreurs!"
                                    else:
                                        erreurs += 1
                                        if erreurs >= max_erreurs:
                                            game_over = True
                                            message = f"Perdu... le mot était {word}"
                            input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 10:  # Limiter la longueur
                            input_text += event.unicode
            else:
                # Permettre de rejouer avec la touche R
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # Réinitialiser le jeu
                    word = choose_word()
                    guess_word = ["_"] * len(word)
                    lettres_proposees = []
                    erreurs = 0
                    game_over = False
                    victory = False
                    input_text = ""
                    message = ""
        
        # Affichage
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(WHITE)
        
        # Dessiner le pendu
        draw_hangman(screen, erreurs)
        
        # Afficher le mot à deviner
        word_display = " ".join(guess_word)
        text = font.render(word_display, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(text, text_rect)
        
        # Afficher les lettres proposées
        if lettres_proposees:
            letters_text = "Lettres proposées: " + ", ".join(lettres_proposees)
            text = small_font.render(letters_text, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 500))
            screen.blit(text, text_rect)
        
        # Afficher le nombre d'erreurs
        error_text = f"Erreurs: {erreurs}/{max_erreurs}"
        text = small_font.render(error_text, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 530))
        screen.blit(text, text_rect)
        
        # Afficher la zone de saisie
        if not game_over:
            input_label = small_font.render("Entrez une lettre ou le mot entier:", True, WHITE)
            screen.blit(input_label, (150, 560))
            # pygame.draw.rect(screen, WHITE, (380, 555, 100, 30), 2)
            # input_surface = small_font.render(input_text, True, WHITE)
            # screen.blit(input_surface, (385, 560))
        
        # Afficher le message de fin
        if game_over:
            color = GREEN if victory else RED
            for i, line in enumerate(message.split('\n')):
                text = font.render(line, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 50 + i*40))
                screen.blit(text, text_rect)
            
            restart_text = small_font.render("Appuyez sur R pour rejouer", True, WHITE)
            text_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, 570))
            screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()