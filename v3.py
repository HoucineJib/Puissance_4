import pygame
import sys
import math
import random
import copy

LIGNES = 6
COLONNES = 7
TAILLE_CASE = 100

MARGE_DRAPEAU = 6
TAILLE_DRAPEAU = TAILLE_CASE - MARGE_DRAPEAU * 2
RAYON_PION = int(TAILLE_CASE / 2 - 8)

MARGE_X = 50
MARGE_Y = 50
ESPACE_ENTETE = 150 

LARGEUR_GRILLE = COLONNES * TAILLE_CASE
HAUTEUR_GRILLE = LIGNES * TAILLE_CASE
LARGEUR_ECRAN = LARGEUR_GRILLE + (MARGE_X * 2)
HAUTEUR_ECRAN = MARGE_Y + ESPACE_ENTETE + HAUTEUR_GRILLE + MARGE_Y
TAILLE_FENETRE = (LARGEUR_ECRAN, HAUTEUR_ECRAN)

BLEU_GRILLE_MODERNE = (30, 96, 150)
COULEUR_FOND = (180, 180, 180)
NOIR = (44, 62, 80)
BLANC = (255, 255, 255)
GRIS_DESACTIVE = (120, 120, 120)
COULEUR_BOUTON = (39, 174, 96)
COULEUR_BOUTON_HOVER = (46, 204, 113)
COULEUR_IA_FACILE = (46, 204, 113)
COULEUR_IA_MOYEN = (243, 156, 18)
COULEUR_IA_DIFFICILE = (231, 76, 60)
ROUGE_ALERT = (231, 76, 60)
OR_VICTOIRE = (255, 215, 0)
VIOLET_MISSCLICK = (142, 68, 173)

POLICE_TAILLE = 60
FPS = 60
VITESSE_CHUTE = 35
TEMPS_PAR_TOUR = 15
MANCHES_PAR_DEFAUT = 2

class Pays:
    def __init__(self, nom, fichier_drapeau, couleur_fond):
        self.nom = nom
        self.fichier_drapeau = fichier_drapeau
        self.couleur_fond = couleur_fond
        self._drapeau_image = None

    def charger_drapeau(self):
        if self._drapeau_image is None:
            try:
                image = pygame.image.load(self.fichier_drapeau)
                self._drapeau_image = pygame.transform.scale(image, (TAILLE_DRAPEAU, TAILLE_DRAPEAU))
            except:
                self._drapeau_image = pygame.Surface((TAILLE_DRAPEAU, TAILLE_DRAPEAU))
                self._drapeau_image.fill(self.couleur_fond)
        return self._drapeau_image

PAYS_DISPONIBLES = [
    Pays("Algérie", "Drapeaux/drapeau_algérie.png", (206, 17, 38)),
    Pays("Maroc", "Drapeaux/drapeau_maroc.png", (206, 60, 60)),
    Pays("Tunisie", "Drapeaux/drapeau_tunisie.png", (0, 35, 149)),
    Pays("Brésil", "Drapeaux/drapeau_brésil.png", (0, 0, 0)),
    Pays("Espagne", "Drapeaux/drapeau_espagne.png", (0, 140, 69)),
    Pays("France", "Drapeaux/drapeau_france.png", (170, 21, 27)),
    Pays("Libye", "Drapeaux/drapeau_libye.png", (0, 156, 59)),
    Pays("Malaisie", "Drapeaux/drapeau_malaisie.png", (116, 172, 223)),
    Pays("Mali", "Drapeaux/drapeau_mali.png", (188, 0, 45)),
    Pays("Palestine", "Drapeaux/drapeau_palestine.png", (255, 0, 0)),
    Pays("Russie", "Drapeaux/drapeau_russie.png", (179, 25, 66)),
    Pays("Sénégal", "Drapeaux/drapeau_sénégal.png", (1, 33, 105))
]

class Joueur:
    def __init__(self, numero_pion, pays):
        self.numero_pion = numero_pion
        self.pays = pays
        self._drapeau_image = pays.charger_drapeau()

    def obtenir_drapeau(self):
        return self._drapeau_image

    def obtenir_message_victoire(self):
        return f"{self.pays.nom} remporte la manche !"
    
    def est_ia(self):
        return False

class JoueurHumain(Joueur):
    def est_ia(self):
        return False

class JoueurOrdinateur(Joueur):
    def __init__(self, numero_pion, pays, difficulte):
        super().__init__(numero_pion, pays)
        self.difficulte = difficulte

    def est_ia(self):
        return True 
    
    def choisir_colonne(self, plateau):
        colonnes_valides = []
        for c in range(COLONNES):
            if plateau.est_colonne_valide(c):
                colonnes_valides.append(c)
        
        if not colonnes_valides:
            return 0

        if self.difficulte == 1:
            return random.choice(colonnes_valides)
        
        profondeur = 2 if self.difficulte == 2 else 4
        colonne, score = self.minimax(plateau.grille, profondeur, -math.inf, math.inf, True)
        
        if colonne is None:
            return random.choice(colonnes_valides)
        return colonne

    def evaluer_fenetre(self, fenetre, piece):
        score = 0
        piece_adverse = 1 if piece == 2 else 2

        if fenetre.count(piece) == 4:
            score += 100
        elif fenetre.count(piece) == 3 and fenetre.count(0) == 1:
            score += 5
        elif fenetre.count(piece) == 2 and fenetre.count(0) == 2:
            score += 2

        if fenetre.count(piece_adverse) == 3 and fenetre.count(0) == 1:
            score -= 4

        return score

    def score_position(self, grille, piece):
        score = 0
        col_centre = [grille[r][COLONNES // 2] for r in range(LIGNES)]
        score += col_centre.count(piece) * 3

        for r in range(LIGNES):
            ligne_array = grille[r]
            for c in range(COLONNES - 3):
                fenetre = ligne_array[c:c+4]
                score += self.evaluer_fenetre(fenetre, piece)

        for c in range(COLONNES):
            col_array = [grille[r][c] for r in range(LIGNES)]
            for r in range(LIGNES - 3):
                fenetre = col_array[r:r+4]
                score += self.evaluer_fenetre(fenetre, piece)

        for r in range(LIGNES - 3):
            for c in range(COLONNES - 3):
                fenetre = [grille[r+i][c+i] for i in range(4)]
                score += self.evaluer_fenetre(fenetre, piece)

        for r in range(LIGNES - 3):
            for c in range(COLONNES - 3):
                fenetre = [grille[r+3-i][c+i] for i in range(4)]
                score += self.evaluer_fenetre(fenetre, piece)

        return score

    def noeud_terminal(self, grille):
        return self.verifier_gagnant(grille, 1) or self.verifier_gagnant(grille, 2) or len(self.obtenir_cols_valides(grille)) == 0

    def minimax(self, grille, depth, alpha, beta, maximizingPlayer):
        cols_valides = self.obtenir_cols_valides(grille)
        est_terminal = self.noeud_terminal(grille)
        
        if depth == 0 or est_terminal:
            if est_terminal:
                if self.verifier_gagnant(grille, self.numero_pion):
                    return (None, 100000000000000)
                elif self.verifier_gagnant(grille, 1 if self.numero_pion == 2 else 2):
                    return (None, -10000000000000)
                else:
                    return (None, 0)
            else:
                return (None, self.score_position(grille, self.numero_pion))

        if maximizingPlayer:
            value = -math.inf
            colonne = random.choice(cols_valides)
            for col in cols_valides:
                row = self.obtenir_prochaine_ligne(grille, col)
                b_copy = copy.deepcopy(grille)
                b_copy[row][col] = self.numero_pion
                new_score = self.minimax(b_copy, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    colonne = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return colonne, value
        else:
            value = math.inf
            colonne = random.choice(cols_valides)
            adversaire = 1 if self.numero_pion == 2 else 2
            for col in cols_valides:
                row = self.obtenir_prochaine_ligne(grille, col)
                b_copy = copy.deepcopy(grille)
                b_copy[row][col] = adversaire
                new_score = self.minimax(b_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    colonne = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return colonne, value

    def obtenir_cols_valides(self, grille):
        valides = []
        for c in range(COLONNES):
            if grille[0][c] == 0:
                valides.append(c)
        return valides

    def obtenir_prochaine_ligne(self, grille, col):
        for r in range(LIGNES - 1, -1, -1):
            if grille[r][col] == 0:
                return r
        return -1

    def verifier_gagnant(self, grille, piece):
        for c in range(COLONNES - 3):
            for r in range(LIGNES):
                if all(grille[r][c+i] == piece for i in range(4)): return True
        for c in range(COLONNES):
            for r in range(LIGNES - 3):
                if all(grille[r+i][c] == piece for i in range(4)): return True
        for c in range(COLONNES - 3):
            for r in range(3, LIGNES):
                if all(grille[r-i][c+i] == piece for i in range(4)): return True
        for c in range(COLONNES - 3):
            for r in range(LIGNES - 3):
                if all(grille[r+i][c+i] == piece for i in range(4)): return True
        return False
    
class Plateau:
    def __init__(self, lignes, colonnes):
        self.lignes = lignes
        self.colonnes = colonnes
        self.grille = self._creer_grille()

    def _creer_grille(self):
        return [[0] * self.colonnes for _ in range(self.lignes)]

    def est_colonne_valide(self, col):
        return 0 <= col < self.colonnes and self.grille[0][col] == 0

    def obtenir_prochaine_ligne_libre(self, col):
        for r in range(self.lignes - 1, -1, -1):
            if self.grille[r][col] == 0:
                return r
        return -1

    def deposer_pion(self, ligne, col, pion):
        self.grille[ligne][col] = pion
    
    def retirer_pion(self, ligne, col):
        self.grille[ligne][col] = 0

    def verifier_victoire(self, pion):
        for c in range(self.colonnes - 3):
            for r in range(self.lignes):
                if all(self.grille[r][c+i] == pion for i in range(4)): return True
        for c in range(self.colonnes):
            for r in range(self.lignes - 3):
                if all(self.grille[r+i][c] == pion for i in range(4)): return True
        for c in range(self.colonnes - 3):
            for r in range(3, self.lignes):
                if all(self.grille[r-i][c+i] == pion for i in range(4)): return True
        for c in range(self.colonnes - 3):
            for r in range(self.lignes - 3):
                if all(self.grille[r+i][c+i] == pion for i in range(4)): return True
        return False
    
    def reinitialiser(self):
        self.grille = self._creer_grille()

class Jeu:
    def __init__(self):
        pygame.init()
        self.plateau = Plateau(LIGNES, COLONNES)
        self.pays_selectionnes = [0, 1]
        self.joueurs = []

        self.ecran = pygame.display.set_mode(TAILLE_FENETRE)
        pygame.display.set_caption("Puissance 4 - Ultimate")

        self.clock = pygame.time.Clock()
        self.police = pygame.font.SysFont("Arial", POLICE_TAILLE, bold=True)
        self.police_bouton = pygame.font.SysFont("Arial", 40, bold=True)
        self.police_petite = pygame.font.SysFont("Arial", 30, bold=True)
        self.police_chrono = pygame.font.SysFont("Consolas", 40, bold=True)
        self.police_regles = pygame.font.SysFont("Arial", 24)

        self.etat_jeu = "MENU"
        self.mode_ia = False 
        self.niveau_ia = 1
        
        self.jeu_termine = False
        self.match_termine = False
        self.score_cible = MANCHES_PAR_DEFAUT
        self.scores = [0, 0]
        
        self.tour_index = 0
        self.anim_en_cours = False
        self.anim_col = 0
        self.anim_ligne_cible = 0
        self.anim_y_actuel = 0
        self.anim_y_cible = 0
        
        self.timer_ia = 0 
        self.compteur_frame = 0
        self.temps_restant = TEMPS_PAR_TOUR

        self.historique_coups = []
        self.missclick_dispo = [True, True]

        self.surface_grille_bleue = self._creer_surface_grille()

    def _creer_surface_grille(self):
        surface = pygame.Surface((LARGEUR_GRILLE, HAUTEUR_GRILLE), pygame.SRCALPHA)
        surface.fill(BLEU_GRILLE_MODERNE)

        for c in range(COLONNES):
            for r in range(LIGNES):
                center_x = int(c * TAILLE_CASE + TAILLE_CASE / 2)
                center_y = int(r * TAILLE_CASE + TAILLE_CASE / 2)
                pygame.draw.circle(surface, (0, 0, 0, 0), (center_x, center_y), RAYON_PION)

        return surface

    def changer_pays(self, joueur_idx, direction):
        autre_joueur_idx = (joueur_idx + 1) % 2
        index_interdit = self.pays_selectionnes[autre_joueur_idx]
        
        nouveau_index = (self.pays_selectionnes[joueur_idx] + direction) % len(PAYS_DISPONIBLES)
        while nouveau_index == index_interdit:
            nouveau_index = (nouveau_index + direction) % len(PAYS_DISPONIBLES)
        self.pays_selectionnes[joueur_idx] = nouveau_index

    def afficher_menu(self):
        self.ecran.fill(COULEUR_FOND)
        titre_surf = self.police.render("PUISSANCE 4", True, NOIR)
        titre_rect = titre_surf.get_rect(center=(LARGEUR_ECRAN/2, HAUTEUR_ECRAN/4))
        self.ecran.blit(titre_surf, titre_rect)

        mouse_pos = pygame.mouse.get_pos()

        bouton_rect = pygame.Rect(0, 0, 300, 80)
        bouton_rect.center = (LARGEUR_ECRAN/2, HAUTEUR_ECRAN/2)
        couleur_btn = COULEUR_BOUTON_HOVER if bouton_rect.collidepoint(mouse_pos) else COULEUR_BOUTON
        pygame.draw.rect(self.ecran, couleur_btn, bouton_rect, border_radius=15)
        pygame.draw.rect(self.ecran, NOIR, bouton_rect, width=3, border_radius=15)
        texte_bouton = self.police_bouton.render("2 JOUEURS", True, BLANC)
        self.ecran.blit(texte_bouton, texte_bouton.get_rect(center=bouton_rect.center))

        bouton_ia_rect = pygame.Rect(0, 0, 350, 80)
        bouton_ia_rect.center = (LARGEUR_ECRAN/2, HAUTEUR_ECRAN/2 + 120)
        
        if self.niveau_ia == 1:
            couleur_base_ia = COULEUR_IA_FACILE
            txt_niveau = "IA: FACILE"
        elif self.niveau_ia == 2:
            couleur_base_ia = COULEUR_IA_MOYEN
            txt_niveau = "IA: MOYEN"
        else:
            couleur_base_ia = COULEUR_IA_DIFFICILE
            txt_niveau = "IA: DIFFICILE"

        pygame.draw.rect(self.ecran, couleur_base_ia, bouton_ia_rect, border_radius=15)
        pygame.draw.rect(self.ecran, NOIR, bouton_ia_rect, width=3, border_radius=15)
        
        texte_ia = self.police_bouton.render(txt_niveau, True, BLANC)
        self.ecran.blit(texte_ia, texte_ia.get_rect(center=bouton_ia_rect.center))

        msg_info = self.police_petite.render("(Cliquez pour changer le niveau)", True, NOIR)
        self.ecran.blit(msg_info, msg_info.get_rect(center=(LARGEUR_ECRAN/2, HAUTEUR_ECRAN/2 + 180)))

        btn_lancer_solo = pygame.Rect(0, 0, 350, 60)
        btn_lancer_solo.center = (LARGEUR_ECRAN/2, HAUTEUR_ECRAN/2 + 250)
        pygame.draw.rect(self.ecran, NOIR, btn_lancer_solo, border_radius=10)
        txt_solo = self.police_bouton.render("LANCER SOLO", True, BLANC)
        self.ecran.blit(txt_solo, txt_solo.get_rect(center=btn_lancer_solo.center))

        btn_regles = pygame.Rect(LARGEUR_ECRAN - 150, 20, 130, 50)
        pygame.draw.rect(self.ecran, (52, 152, 219), btn_regles, border_radius=10)
        pygame.draw.rect(self.ecran, NOIR, btn_regles, 2, border_radius=10)
        txt_regles = self.police_petite.render("RÈGLES", True, BLANC)
        self.ecran.blit(txt_regles, txt_regles.get_rect(center=btn_regles.center))

        return bouton_rect, bouton_ia_rect, btn_lancer_solo, btn_regles

    def afficher_regles(self):
        s = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        s.set_alpha(240)
        s.fill(COULEUR_FOND)
        self.ecran.blit(s, (0, 0))

        cadre_regles = pygame.Rect(0, 0, 600, 500)
        cadre_regles.center = (LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2)
        pygame.draw.rect(self.ecran, BLANC, cadre_regles, border_radius=20)
        pygame.draw.rect(self.ecran, NOIR, cadre_regles, 3, border_radius=20)

        titre = self.police_bouton.render("RÈGLES DU JEU", True, NOIR)
        self.ecran.blit(titre, titre.get_rect(center=(LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2 - 200)))

        lignes = [
            "BUT DU JEU :",
            "Aligner 4 pions de sa couleur horizontalement,",
            "verticalement ou en diagonale.",
            "",
            "NOUVEAU : MISSCLICK",
            "Chaque joueur a le droit d'annuler 1 coup",
            "par manche (Bouton violet).",
            "",
            "MODES :",
            "- Solo vs IA : Parties illimitées.",
            "- 2 Joueurs : Premier à X victoires gagne."
        ]

        y_txt = HAUTEUR_ECRAN//2 - 130
        for ligne in lignes:
            txt = self.police_regles.render(ligne, True, NOIR)
            self.ecran.blit(txt, (cadre_regles.x + 30, y_txt))
            y_txt += 30

        btn_retour = pygame.Rect(0, 0, 200, 50)
        btn_retour.center = (LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2 + 200)
        pygame.draw.rect(self.ecran, ROUGE_ALERT, btn_retour, border_radius=10)
        pygame.draw.rect(self.ecran, NOIR, btn_retour, 2, border_radius=10)
        txt_ret = self.police_bouton.render("RETOUR", True, BLANC)
        self.ecran.blit(txt_ret, txt_ret.get_rect(center=btn_retour.center))

        return btn_retour

    def afficher_selection_pays(self):
        self.ecran.fill(COULEUR_FOND)
        titre = self.police.render("Sélectionnez les pays", True, NOIR)
        self.ecran.blit(titre, (LARGEUR_ECRAN//2 - titre.get_width()//2, 30))

        btn_moins = None
        btn_plus = None
        
        if not self.mode_ia:
            y_manches = 90
            txt_obj = self.police_petite.render(f"Victoire à {self.score_cible} manches", True, NOIR)
            self.ecran.blit(txt_obj, (LARGEUR_ECRAN//2 - txt_obj.get_width()//2, y_manches))
            
            btn_moins = pygame.Rect(LARGEUR_ECRAN//2 - 150, y_manches - 5, 40, 40)
            btn_plus = pygame.Rect(LARGEUR_ECRAN//2 + 110, y_manches - 5, 40, 40)
            
            pygame.draw.rect(self.ecran, COULEUR_BOUTON, btn_moins, border_radius=5)
            pygame.draw.rect(self.ecran, COULEUR_BOUTON, btn_plus, border_radius=5)
            
            txt_m = self.police_petite.render("-", True, BLANC)
            txt_p = self.police_petite.render("+", True, BLANC)
            
            self.ecran.blit(txt_m, txt_m.get_rect(center=btn_moins.center))
            self.ecran.blit(txt_p, txt_p.get_rect(center=btn_plus.center))

        for i in range(2):
            y_pos = 160 + i * 200
            
            nom_joueur = f"Joueur {i+1}"
            if self.mode_ia and i == 1:
                niv = ["Facile", "Moyen", "Difficile"][self.niveau_ia - 1]
                nom_joueur = f"Ordi ({niv})"
                
            joueur_text = self.police_bouton.render(f"{nom_joueur}:", True, NOIR)
            self.ecran.blit(joueur_text, (50, y_pos))

            pays = PAYS_DISPONIBLES[self.pays_selectionnes[i]]
            drapeau = pays.charger_drapeau()
            cadre_rect = pygame.Rect(200, y_pos-10, 200, 100)
            pygame.draw.rect(self.ecran, NOIR, cadre_rect, 2)
            
            drapeau_rect = drapeau.get_rect(center=cadre_rect.center)
            self.ecran.blit(drapeau, drapeau_rect)
            
            for j, (dx, texte) in enumerate([(-30, "<"), (240, ">")]):
                btn_rect = pygame.Rect(200 + dx, y_pos + 40, 60, 40)
                couleur = (200, 200, 200) if (i == 0 and j == 0) or (i == 1 and j == 1) else COULEUR_BOUTON
                pygame.draw.rect(self.ecran, couleur, btn_rect)
                pygame.draw.rect(self.ecran, NOIR, btn_rect, 2)
                text_surf = self.police_bouton.render(texte, True, NOIR)
                self.ecran.blit(text_surf, (btn_rect.centerx - text_surf.get_width()//2, 
                                            btn_rect.centery - text_surf.get_height()//2))

        btn_demarrer = pygame.Rect(LARGEUR_ECRAN//2 - 100, HAUTEUR_ECRAN - 100, 200, 60)
        pygame.draw.rect(self.ecran, COULEUR_BOUTON, btn_demarrer)
        pygame.draw.rect(self.ecran, NOIR, btn_demarrer, 2)
        demarrer_text = self.police_bouton.render("Démarrer", True, BLANC)
        self.ecran.blit(demarrer_text, (btn_demarrer.centerx - demarrer_text.get_width()//2, 
                                        btn_demarrer.centery - demarrer_text.get_height()//2))
        
        return btn_demarrer, btn_moins, btn_plus

    def afficher_pause(self):
        s = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        s.set_alpha(180)
        s.fill((0, 0, 0))
        self.ecran.blit(s, (0, 0))

        rect_menu = pygame.Rect(0, 0, 400, 300)
        rect_menu.center = (LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2)
        pygame.draw.rect(self.ecran, BLANC, rect_menu, border_radius=20)
        pygame.draw.rect(self.ecran, NOIR, rect_menu, 3, border_radius=20)

        txt_pause = self.police.render("PAUSE", True, NOIR)
        self.ecran.blit(txt_pause, txt_pause.get_rect(center=(LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2 - 80)))

        btn_reprendre = pygame.Rect(0, 0, 250, 60)
        btn_reprendre.center = (LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2 + 10)
        pygame.draw.rect(self.ecran, COULEUR_BOUTON, btn_reprendre, border_radius=10)
        txt_rep = self.police_bouton.render("Reprendre", True, BLANC)
        self.ecran.blit(txt_rep, txt_rep.get_rect(center=btn_reprendre.center))

        btn_quitter = pygame.Rect(0, 0, 250, 60)
        btn_quitter.center = (LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2 + 90)
        pygame.draw.rect(self.ecran, ROUGE_ALERT, btn_quitter, border_radius=10)
        txt_quit = self.police_bouton.render("Menu Principal", True, BLANC)
        self.ecran.blit(txt_quit, txt_quit.get_rect(center=btn_quitter.center))

        return btn_reprendre, btn_quitter

    def afficher_ecran_victoire_match(self):
        s = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        self.ecran.blit(s, (0, 0))

        rect_win = pygame.Rect(0, 0, 600, 400)
        rect_win.center = (LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2)
        pygame.draw.rect(self.ecran, BLANC, rect_win, border_radius=20)
        pygame.draw.rect(self.ecran, OR_VICTOIRE, rect_win, 8, border_radius=20)

        txt_felicitation = self.police.render("FÉLICITATIONS !", True, NOIR)
        self.ecran.blit(txt_felicitation, txt_felicitation.get_rect(center=(LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2 - 100)))

        nom_gagnant = self.joueurs[self.tour_index].pays.nom
        
        txt_vainqueur = self.police.render(f"Vainqueur : {nom_gagnant}", True, OR_VICTOIRE)
        self.ecran.blit(txt_vainqueur, txt_vainqueur.get_rect(center=(LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2)))

        btn_action = pygame.Rect(0, 0, 300, 70)
        btn_action.center = (LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2 + 100)
        
        pygame.draw.rect(self.ecran, ROUGE_ALERT, btn_action, border_radius=10)
        txt_btn = self.police_bouton.render("RETOUR MENU", True, BLANC)
            
        pygame.draw.rect(self.ecran, NOIR, btn_action, 2, border_radius=10)
        self.ecran.blit(txt_btn, txt_btn.get_rect(center=btn_action.center))

        return btn_action

    def gerer_clic_souris(self, pos):
        if self.etat_jeu == "SELECTION_PAYS":
            btn_demarrer, btn_moins, btn_plus = self.afficher_selection_pays()
            
            if btn_moins and btn_moins.collidepoint(pos):
                self.score_cible = max(1, self.score_cible - 1)
            if btn_plus and btn_plus.collidepoint(pos):
                self.score_cible = min(10, self.score_cible + 1)

            for i in range(2):
                for j, dx in enumerate([-30, 240]):
                    btn_rect = pygame.Rect(200 + dx, 160 + i * 200 + 40, 60, 40)
                    if btn_rect.collidepoint(pos):
                        direction = -1 if j == 0 else 1
                        self.changer_pays(i, direction)
                        return
            
            if btn_demarrer.collidepoint(pos):
                self.demarrer_jeu()
        
        elif self.etat_jeu == "REGLES":
            btn_retour = self.afficher_regles()
            if btn_retour.collidepoint(pos):
                self.etat_jeu = "MENU"

        elif self.etat_jeu == "PAUSE":
            btn_reprendre, btn_quitter = self.afficher_pause()
            if btn_reprendre.collidepoint(pos):
                self.etat_jeu = "JEU"
            elif btn_quitter.collidepoint(pos):
                self.etat_jeu = "MENU"
                self.scores = [0, 0]

        elif self.etat_jeu == "JEU":
            if self.match_termine and not self.mode_ia:
                btn_retour = self.afficher_ecran_victoire_match()
                if btn_retour.collidepoint(pos):
                    self.etat_jeu = "MENU"
                    self.scores = [0, 0]
                    self.match_termine = False
                    self.jeu_termine = False
                return

            btn_pause = pygame.Rect(LARGEUR_ECRAN - 140, 20, 120, 50)
            if btn_pause.collidepoint(pos):
                self.etat_jeu = "PAUSE"
                return
            
            if not self.jeu_termine and not self.anim_en_cours:
                if not self.mode_ia or (self.mode_ia and not self.joueurs[0].est_ia()):
                     btn_missclick_j1 = pygame.Rect(20, HAUTEUR_ECRAN - 80, 180, 50)
                     if btn_missclick_j1.collidepoint(pos):
                         self.action_missclick(0)
                         return

                if not self.mode_ia:
                    btn_missclick_j2 = pygame.Rect(LARGEUR_ECRAN - 200, HAUTEUR_ECRAN - 80, 180, 50)
                    if btn_missclick_j2.collidepoint(pos):
                        self.action_missclick(1)
                        return

            if self.jeu_termine:
                self.reinitialiser_jeu()

    def demarrer_jeu(self):
        p1 = JoueurHumain(1, PAYS_DISPONIBLES[self.pays_selectionnes[0]])
        if self.mode_ia:
            p2 = JoueurOrdinateur(2, PAYS_DISPONIBLES[self.pays_selectionnes[1]], self.niveau_ia)
        else:
            p2 = JoueurHumain(2, PAYS_DISPONIBLES[self.pays_selectionnes[1]])

        self.joueurs = [p1, p2]
        self.etat_jeu = "JEU"
        self.plateau = Plateau(LIGNES, COLONNES)
        self.tour_index = 0
        self.jeu_termine = False
        self.match_termine = False
        self.anim_en_cours = False
        self.temps_restant = TEMPS_PAR_TOUR
        
        self.missclick_dispo = [True, True]
        self.historique_coups = []
    
    def reinitialiser_jeu(self):
        self.plateau.reinitialiser()
        self.jeu_termine = False
        self.tour_index = (self.scores[0] + self.scores[1]) % 2 
        self.anim_en_cours = False
        self.temps_restant = TEMPS_PAR_TOUR
        
        self.missclick_dispo = [True, True]
        self.historique_coups = []

    def action_missclick(self, joueur_idx):
        if not self.missclick_dispo[joueur_idx]:
            return
        
        if not self.historique_coups:
            return

        if self.mode_ia and joueur_idx == 0:
            if len(self.historique_coups) >= 2:
                last_move_ia = self.historique_coups.pop()
                self.plateau.retirer_pion(last_move_ia[0], last_move_ia[1])
                
                last_move_j = self.historique_coups.pop()
                self.plateau.retirer_pion(last_move_j[0], last_move_j[1])
                
                self.missclick_dispo[joueur_idx] = False
                self.tour_index = 0 
                self.temps_restant = TEMPS_PAR_TOUR
                
        elif not self.mode_ia:
            dernier_coup = self.historique_coups[-1]
            joueur_qui_a_joue = dernier_coup[2]
            
            if joueur_qui_a_joue == joueur_idx:
                move = self.historique_coups.pop()
                self.plateau.retirer_pion(move[0], move[1])
                self.missclick_dispo[joueur_idx] = False
                self.tour_index = joueur_idx 
                self.temps_restant = TEMPS_PAR_TOUR

    def debuter_coup(self, col):
        if not self.plateau.est_colonne_valide(col) or self.anim_en_cours:
            return
        ligne = self.plateau.obtenir_prochaine_ligne_libre(col)
        if ligne == -1:
            return
        self.anim_en_cours = True
        self.anim_col = col
        self.anim_ligne_cible = ligne
        self.anim_y_actuel = MARGE_Y + ESPACE_ENTETE - TAILLE_CASE 
        self.anim_y_cible = MARGE_Y + ESPACE_ENTETE + ligne * TAILLE_CASE

    def mettre_a_jour_animation(self):
        if not self.anim_en_cours:
            return

        self.anim_y_actuel += VITESSE_CHUTE
        
        if self.anim_y_actuel >= self.anim_y_cible:
            self.anim_y_actuel = self.anim_y_cible
            self.anim_en_cours = False
            self.plateau.deposer_pion(self.anim_ligne_cible, self.anim_col, self.tour_index + 1)
            
            self.historique_coups.append((self.anim_ligne_cible, self.anim_col, self.tour_index))

            if self.plateau.verifier_victoire(self.tour_index + 1):
                self.jeu_termine = True
                self.scores[self.tour_index] += 1
                
                if not self.mode_ia and self.scores[self.tour_index] >= self.score_cible:
                    self.match_termine = True
            else:
                self.tour_index = (self.tour_index + 1) % 2
                self.timer_ia = 0
                self.temps_restant = TEMPS_PAR_TOUR

    def dessiner_plateau_et_animation(self, mouse_x=None):
        self.ecran.fill(COULEUR_FOND)
        debut_grille_y = MARGE_Y + ESPACE_ENTETE

        txt_scores = self.police_bouton.render(f"SCORE: {self.scores[0]} - {self.scores[1]}", True, NOIR)
        self.ecran.blit(txt_scores, (20, 20))
        
        if not self.mode_ia:
            txt_obj = self.police_petite.render(f"Objectif: {self.score_cible}", True, NOIR)
            self.ecran.blit(txt_obj, (20, 60))

        if not self.mode_ia and not self.jeu_termine:
            couleur_chrono = NOIR if self.temps_restant > 5 else ROUGE_ALERT
            txt_chrono = self.police_chrono.render(f"00:{self.temps_restant:02d}", True, couleur_chrono)
            rect_chrono = txt_chrono.get_rect(center=(LARGEUR_ECRAN // 2, 50))
            self.ecran.blit(txt_chrono, rect_chrono)

        btn_pause = pygame.Rect(LARGEUR_ECRAN - 140, 20, 120, 50)
        pygame.draw.rect(self.ecran, (52, 152, 219), btn_pause, border_radius=8)
        pygame.draw.rect(self.ecran, NOIR, btn_pause, 2, border_radius=8)
        txt_pause = self.police_petite.render("PAUSE", True, BLANC)
        self.ecran.blit(txt_pause, txt_pause.get_rect(center=btn_pause.center))
        
        if not self.jeu_termine and not self.match_termine:
            if not self.mode_ia or (self.mode_ia and not self.joueurs[0].est_ia()):
                btn_j1 = pygame.Rect(20, HAUTEUR_ECRAN - 80, 180, 50)
                couleur_j1 = VIOLET_MISSCLICK if self.missclick_dispo[0] else GRIS_DESACTIVE
                
                actif = self.missclick_dispo[0]
                if self.mode_ia and len(self.historique_coups) < 2: actif = False
                if not self.mode_ia and (not self.historique_coups or self.historique_coups[-1][2] != 0): actif = False
                
                if not actif: couleur_j1 = GRIS_DESACTIVE
                
                pygame.draw.rect(self.ecran, couleur_j1, btn_j1, border_radius=10)
                pygame.draw.rect(self.ecran, NOIR, btn_j1, 2, border_radius=10)
                txt_mc = self.police_petite.render("Annuler", True, BLANC)
                self.ecran.blit(txt_mc, txt_mc.get_rect(center=btn_j1.center))

            if not self.mode_ia:
                btn_j2 = pygame.Rect(LARGEUR_ECRAN - 200, HAUTEUR_ECRAN - 80, 180, 50)
                couleur_j2 = VIOLET_MISSCLICK if self.missclick_dispo[1] else GRIS_DESACTIVE
                
                actif = self.missclick_dispo[1]
                if not self.historique_coups or self.historique_coups[-1][2] != 1: actif = False
                if not actif: couleur_j2 = GRIS_DESACTIVE

                pygame.draw.rect(self.ecran, couleur_j2, btn_j2, border_radius=10)
                pygame.draw.rect(self.ecran, NOIR, btn_j2, 2, border_radius=10)
                txt_mc2 = self.police_petite.render("Annuler", True, BLANC)
                self.ecran.blit(txt_mc2, txt_mc2.get_rect(center=btn_j2.center))

        for c in range(COLONNES):
            for r in range(LIGNES):
                pion_val = self.plateau.grille[r][c]
                if pion_val != 0:
                    joueur = self.joueurs[pion_val - 1]
                    drapeau = joueur.obtenir_drapeau()
                    pos_x = MARGE_X + c * TAILLE_CASE + MARGE_DRAPEAU
                    pos_y = debut_grille_y + r * TAILLE_CASE + MARGE_DRAPEAU
                    self.ecran.blit(drapeau, (pos_x, pos_y))

        if self.anim_en_cours:
            joueur_anim = self.joueurs[self.tour_index]
            drapeau_anim = joueur_anim.obtenir_drapeau()
            pos_x_anim = MARGE_X + self.anim_col * TAILLE_CASE + MARGE_DRAPEAU
            pos_y_anim = int(self.anim_y_actuel) + MARGE_DRAPEAU
            self.ecran.blit(drapeau_anim, (pos_x_anim, pos_y_anim))

        self.ecran.blit(self.surface_grille_bleue, (MARGE_X, debut_grille_y))

        joueur_actuel = self.joueurs[self.tour_index]
        if not self.jeu_termine and not self.anim_en_cours and mouse_x is not None and not joueur_actuel.est_ia() and self.etat_jeu != "PAUSE" and not self.match_termine:
            drapeau = joueur_actuel.obtenir_drapeau()
            pos_y = MARGE_Y + ESPACE_ENTETE - TAILLE_DRAPEAU
            pos_x = mouse_x - (TAILLE_DRAPEAU // 2)
            limite_gauche = MARGE_X + MARGE_DRAPEAU
            limite_droite = MARGE_X + LARGEUR_GRILLE - TAILLE_DRAPEAU - MARGE_DRAPEAU
            if pos_x < limite_gauche: pos_x = limite_gauche
            elif pos_x > limite_droite: pos_x = limite_droite
            self.ecran.blit(drapeau, (pos_x, pos_y))

        if self.jeu_termine and not self.match_termine:
            bandeau = pygame.Surface((LARGEUR_ECRAN, 100))
            bandeau.set_alpha(230)
            bandeau.fill(OR_VICTOIRE)
            self.ecran.blit(bandeau, (0, HAUTEUR_ECRAN//2 - 50))

            nom_gagnant = self.joueurs[self.tour_index].pays.nom.upper()
            if self.mode_ia:
                if self.joueurs[self.tour_index].est_ia():
                    msg = "L'IA REMPORTE LA MANCHE !"
                else:
                    msg = "VOUS REMPORTEZ LA MANCHE !"
            else:
                msg = f"MANCHE POUR {nom_gagnant} !"

            txt_main = self.police_bouton.render(msg, True, NOIR)
            txt_sub = self.police_petite.render("CLIQUEZ POUR CONTINUER...", True, NOIR)

            self.ecran.blit(txt_main, txt_main.get_rect(center=(LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2 - 15)))
            self.ecran.blit(txt_sub, txt_sub.get_rect(center=(LARGEUR_ECRAN//2, HAUTEUR_ECRAN//2 + 35)))
        
        if self.match_termine and not self.mode_ia:
            self.afficher_ecran_victoire_match()

    def boucle_principale(self):
        mouse_x = LARGEUR_ECRAN // 2

        while True:
            if self.etat_jeu == "JEU" and not self.jeu_termine and not self.anim_en_cours:
                joueur_actuel = self.joueurs[self.tour_index]
                if joueur_actuel.est_ia():
                    self.timer_ia += 1
                    if self.timer_ia > 20: 
                        col_ia = joueur_actuel.choisir_colonne(self.plateau)
                        self.debuter_coup(col_ia)
                        self.timer_ia = 0
                else:
                    if not self.mode_ia:
                        self.compteur_frame += 1
                        if self.compteur_frame >= FPS:
                            self.temps_restant -= 1
                            self.compteur_frame = 0
                            if self.temps_restant < 0:
                                valides = []
                                for c in range(COLONNES):
                                    if self.plateau.est_colonne_valide(c): valides.append(c)
                                if valides: self.debuter_coup(random.choice(valides))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    mouse_x = event.pos[0]

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.etat_jeu == "MENU":
                        btn_2j, btn_ia, btn_solo, btn_regles = self.afficher_menu()
                        if btn_2j.collidepoint(event.pos):
                            self.mode_ia = False
                            self.score_cible = MANCHES_PAR_DEFAUT
                            self.etat_jeu = "SELECTION_PAYS"
                        elif btn_ia.collidepoint(event.pos):
                            self.niveau_ia = (self.niveau_ia % 3) + 1
                        elif btn_solo.collidepoint(event.pos):
                            self.mode_ia = True
                            self.etat_jeu = "SELECTION_PAYS"
                        elif btn_regles.collidepoint(event.pos):
                            self.etat_jeu = "REGLES"

                    elif self.etat_jeu == "JEU":
                        if self.match_termine:
                            self.gerer_clic_souris(event.pos)
                            continue

                        btn_pause = pygame.Rect(LARGEUR_ECRAN - 140, 20, 120, 50)
                        
                        btn_miss_p1 = pygame.Rect(20, HAUTEUR_ECRAN - 80, 180, 50)
                        btn_miss_p2 = pygame.Rect(LARGEUR_ECRAN - 200, HAUTEUR_ECRAN - 80, 180, 50)
                        
                        if btn_pause.collidepoint(event.pos):
                            self.gerer_clic_souris(event.pos)
                            continue
                        
                        elif btn_miss_p1.collidepoint(event.pos) or btn_miss_p2.collidepoint(event.pos):
                             self.gerer_clic_souris(event.pos)
                             continue

                        if self.jeu_termine:
                             self.gerer_clic_souris(event.pos)
                        elif not self.anim_en_cours:
                            joueur_actuel = self.joueurs[self.tour_index]
                            if not joueur_actuel.est_ia():
                                pos_relative_x = event.pos[0] - MARGE_X
                                if 0 <= pos_relative_x < COLONNES * TAILLE_CASE:
                                    col = int(pos_relative_x / TAILLE_CASE)
                                    self.debuter_coup(col)
                    
                    else:
                        self.gerer_clic_souris(event.pos)

            if self.etat_jeu == "JEU":
                self.mettre_a_jour_animation()
                self.dessiner_plateau_et_animation(mouse_x)
            elif self.etat_jeu == "MENU":
                self.afficher_menu()
            elif self.etat_jeu == "SELECTION_PAYS":
                self.afficher_selection_pays()
            elif self.etat_jeu == "PAUSE":
                self.dessiner_plateau_et_animation(None)
                self.afficher_pause()
            elif self.etat_jeu == "REGLES":
                self.afficher_regles()

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    try:
        Jeu().boucle_principale()
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        pygame.quit()
        sys.exit()