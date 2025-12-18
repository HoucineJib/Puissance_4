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
ESPACE_ENTETE = 100

LARGEUR_GRILLE = COLONNES * TAILLE_CASE
HAUTEUR_GRILLE = LIGNES * TAILLE_CASE
LARGEUR_ECRAN = LARGEUR_GRILLE + (MARGE_X * 2)
HAUTEUR_ECRAN = MARGE_Y + ESPACE_ENTETE + HAUTEUR_GRILLE + MARGE_Y
TAILLE_FENETRE = (LARGEUR_ECRAN, HAUTEUR_ECRAN)

BLEU_GRILLE_MODERNE = (30, 96, 150)
COULEUR_FOND = (180, 180, 180)
NOIR = (44, 62, 80)
BLANC = (255, 255, 255)
COULEUR_BOUTON = (39, 174, 96)
COULEUR_BOUTON_HOVER = (46, 204, 113)
COULEUR_IA_FACILE = (46, 204, 113)
COULEUR_IA_MOYEN = (243, 156, 18)
COULEUR_IA_DIFFICILE = (231, 76, 60)

POLICE_TAILLE = 60
FPS = 60
VITESSE_CHUTE = 25

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
    Pays("Liban", "Drapeaux/drapeau_liban.png", (237, 28, 36)),
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
        return f"{self.pays.nom} a Gagné !!"
    
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
        pygame.display.set_caption("Puissance 4 - Expert")

        self.clock = pygame.time.Clock()
        self.police = pygame.font.SysFont("Arial", POLICE_TAILLE, bold=True)
        self.police_bouton = pygame.font.SysFont("Arial", 40, bold=True)
        self.police_petite = pygame.font.SysFont("Arial", 30, bold=True)

        self.etat_jeu = "MENU"
        self.mode_ia = False 
        self.niveau_ia = 1
        self.jeu_termine = False
        self.tour_index = 0

        self.anim_en_cours = False
        self.anim_col = 0
        self.anim_ligne_cible = 0
        self.anim_y_actuel = 0
        self.anim_y_cible = 0
        
        self.timer_ia = 0 

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

        return bouton_rect, bouton_ia_rect, btn_lancer_solo

    def afficher_selection_pays(self):
        self.ecran.fill(COULEUR_FOND)
        titre = self.police.render("Sélectionnez les pays", True, NOIR)
        self.ecran.blit(titre, (LARGEUR_ECRAN//2 - titre.get_width()//2, 30))

        for i in range(2):
            y_pos = 150 + i * 200
            
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
        return btn_demarrer

    def gerer_clic_souris(self, pos):
        if self.etat_jeu == "SELECTION_PAYS":
            for i in range(2):
                for j, dx in enumerate([-30, 240]):
                    btn_rect = pygame.Rect(200 + dx, 190 + i * 200, 60, 40)
                    if btn_rect.collidepoint(pos):
                        if j == 0:
                            self.pays_selectionnes[i] = (self.pays_selectionnes[i] - 1) % len(PAYS_DISPONIBLES)
                        else:
                            self.pays_selectionnes[i] = (self.pays_selectionnes[i] + 1) % len(PAYS_DISPONIBLES)
                        return
            
            btn_demarrer = pygame.Rect(LARGEUR_ECRAN//2 - 100, HAUTEUR_ECRAN - 100, 200, 60)
            if btn_demarrer.collidepoint(pos):
                self.demarrer_jeu()
        
        elif self.etat_jeu == "JEU" and self.jeu_termine:
            btn_rejouer = pygame.Rect(LARGEUR_ECRAN//2 - 100, HAUTEUR_ECRAN//2 + 80, 200, 60)
            if btn_rejouer.collidepoint(pos):
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
        self.anim_en_cours = False
    
    def reinitialiser_jeu(self):
        self.plateau.reinitialiser()
        self.jeu_termine = False
        self.tour_index = 0
        self.anim_en_cours = False

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

            if self.plateau.verifier_victoire(self.tour_index + 1):
                self.jeu_termine = True
            else:
                self.tour_index = (self.tour_index + 1) % 2
                self.timer_ia = 0

    def dessiner_plateau_et_animation(self, mouse_x=None):
        self.ecran.fill(COULEUR_FOND)
        debut_grille_y = MARGE_Y + ESPACE_ENTETE

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
        
        if not self.jeu_termine and not self.anim_en_cours and mouse_x is not None and not joueur_actuel.est_ia():
            drapeau = joueur_actuel.obtenir_drapeau()
            pos_y = MARGE_Y + ESPACE_ENTETE - TAILLE_DRAPEAU
            pos_x = mouse_x - (TAILLE_DRAPEAU // 2)
            
            limite_gauche = MARGE_X + MARGE_DRAPEAU
            limite_droite = MARGE_X + LARGEUR_GRILLE - TAILLE_DRAPEAU - MARGE_DRAPEAU
            
            if pos_x < limite_gauche:
                pos_x = limite_gauche
            elif pos_x > limite_droite:
                pos_x = limite_droite
                
            self.ecran.blit(drapeau, (pos_x, pos_y))

        if self.jeu_termine:
            message = self.joueurs[self.tour_index].obtenir_message_victoire()
            texte_victoire = self.police.render(message, True, NOIR)
            ombre_rect = texte_victoire.get_rect(center=(LARGEUR_ECRAN//2, 50))
            pygame.draw.rect(self.ecran, (255, 255, 255, 180), 
                           (ombre_rect.x-10, ombre_rect.y-10, 
                            ombre_rect.width+20, ombre_rect.height+20))
            pygame.draw.rect(self.ecran, NOIR, 
                           (ombre_rect.x-10, ombre_rect.y-10, 
                            ombre_rect.width+20, ombre_rect.height+20), 2)
            self.ecran.blit(texte_victoire, ombre_rect)

            btn_rejouer = pygame.Rect(LARGEUR_ECRAN//2 - 100, HAUTEUR_ECRAN//2 + 80, 200, 60)
            pygame.draw.rect(self.ecran, COULEUR_BOUTON, btn_rejouer, border_radius=10)
            pygame.draw.rect(self.ecran, NOIR, btn_rejouer, 2, border_radius=10)
            txt_rejouer = self.police_bouton.render("REJOUER", True, BLANC)
            self.ecran.blit(txt_rejouer, txt_rejouer.get_rect(center=btn_rejouer.center))

    def boucle_principale(self):
        mouse_x = LARGEUR_ECRAN // 2

        while True:
            if self.etat_jeu == "JEU" and not self.jeu_termine and not self.anim_en_cours:
                joueur_actuel = self.joueurs[self.tour_index]
                if joueur_actuel.est_ia():
                    self.timer_ia += 1
                    if self.timer_ia > 10:
                        col_ia = joueur_actuel.choisir_colonne(self.plateau)
                        self.debuter_coup(col_ia)
                        self.timer_ia = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    mouse_x = event.pos[0]

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.etat_jeu == "MENU":
                        btn_2j, btn_ia, btn_solo = self.afficher_menu()
                        if btn_2j.collidepoint(event.pos):
                            self.mode_ia = False
                            self.etat_jeu = "SELECTION_PAYS"
                        elif btn_ia.collidepoint(event.pos):
                            self.niveau_ia = (self.niveau_ia % 3) + 1
                        elif btn_solo.collidepoint(event.pos):
                            self.mode_ia = True
                            self.etat_jeu = "SELECTION_PAYS"

                    elif self.etat_jeu != "JEU":
                        self.gerer_clic_souris(event.pos)
                    else:
                        if self.jeu_termine:
                             self.gerer_clic_souris(event.pos)
                        elif not self.anim_en_cours:
                            joueur_actuel = self.joueurs[self.tour_index]
                            if not joueur_actuel.est_ia():
                                pos_relative_x = event.pos[0] - MARGE_X
                                if 0 <= pos_relative_x < COLONNES * TAILLE_CASE:
                                    col = int(pos_relative_x / TAILLE_CASE)
                                    self.debuter_coup(col)

            if self.etat_jeu == "JEU":
                self.mettre_a_jour_animation()

            if self.etat_jeu == "MENU":
                self.afficher_menu()
            elif self.etat_jeu == "SELECTION_PAYS":
                self.afficher_selection_pays()
            elif self.etat_jeu == "JEU":
                self.dessiner_plateau_et_animation(mouse_x)

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    try:
        Jeu().boucle_principale()
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        pygame.quit()
        sys.exit()

        #test