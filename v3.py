import pygame
import sys
import math
import random
import copy

# =========================
# PARAMÈTRES GLOBAUX
# =========================
TAILLE_CASE = 100
MARGE_DRAPEAU = 6
RAYON_PION = int(TAILLE_CASE / 2 - 8)

MARGE_X = 50
MARGE_Y = 40
ESPACE_ENTETE = 150

POLICE_TAILLE = 60
FPS = 60
VITESSE_CHUTE = 35
TEMPS_PAR_TOUR = 30
MANCHES_PAR_DEFAUT = 2

GRILLES_DISPONIBLES = [(7, 6), (8, 7), (9, 8)]

# =========================
# COULEURS & THÈMES
# =========================
BLEU_GRILLE_MODERNE = (30, 96, 150)

THEME_CLAIR = {
    "fond": (180, 180, 180),
    "texte": (44, 62, 80),
    "texte_inverse": (255, 255, 255),
    "panel": (255, 255, 255),
    "panel_bord": (44, 62, 80),
    "gris_desactive": (120, 120, 120),
}

THEME_SOMBRE = {
    "fond": (25, 28, 35),
    "texte": (235, 235, 235),
    "texte_inverse": (25, 28, 35),
    "panel": (40, 45, 55),
    "panel_bord": (235, 235, 235),
    "gris_desactive": (95, 95, 95),
}

COULEUR_BOUTON = (39, 174, 96)
COULEUR_BOUTON_HOVER = (46, 204, 113)
COULEUR_IA_FACILE = (46, 204, 113)
COULEUR_IA_MOYEN = (243, 156, 18)
COULEUR_IA_DIFFICILE = (231, 76, 60)
ROUGE_ALERT = (231, 76, 60)
OR_VICTOIRE = (255, 215, 0)
VIOLET_MISSCLICK = (142, 68, 173)
BLEU_INFO = (52, 152, 219)
VIOLET_CREDITS = (155, 89, 182)

# =========================
# CLASSES PAYS / JOUEURS
# =========================
class Pays:
    def __init__(self, nom, fichier_drapeau, couleur_fond):
        self.nom = nom
        self.fichier_drapeau = fichier_drapeau
        self.couleur_fond = couleur_fond
        self._cache = {}  # size -> surface

    def charger_drapeau(self, taille_drapeau: int):
        taille_drapeau = max(10, int(taille_drapeau))
        if taille_drapeau not in self._cache:
            try:
                image = pygame.image.load(self.fichier_drapeau)
                self._cache[taille_drapeau] = pygame.transform.smoothscale(image, (taille_drapeau, taille_drapeau))
            except:
                surf = pygame.Surface((taille_drapeau, taille_drapeau))
                surf.fill(self.couleur_fond)
                self._cache[taille_drapeau] = surf
        return self._cache[taille_drapeau]


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
    Pays("Sénégal", "Drapeaux/drapeau_sénégal.png", (1, 33, 105)),
]


class Joueur:
    def __init__(self, numero_pion, pays: Pays, taille_drapeau: int):
        self.numero_pion = numero_pion
        self.pays = pays
        self._taille_drapeau = taille_drapeau
        self._drapeau_image = pays.charger_drapeau(taille_drapeau)

    def refresh_drapeau(self, taille_drapeau: int):
        self._taille_drapeau = taille_drapeau
        self._drapeau_image = self.pays.charger_drapeau(taille_drapeau)

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
    def __init__(self, numero_pion, pays, difficulte, taille_drapeau):
        super().__init__(numero_pion, pays, taille_drapeau)
        self.difficulte = difficulte

    def est_ia(self):
        return True

    def choisir_colonne(self, plateau):
        colonnes = plateau.colonnes
        colonnes_valides = [c for c in range(colonnes) if plateau.est_colonne_valide(c)]
        if not colonnes_valides:
            return 0

        if self.difficulte == 1:
            return random.choice(colonnes_valides)

        profondeur = 2 if self.difficulte == 2 else 4
        colonne, _ = self.minimax(plateau.grille, profondeur, -math.inf, math.inf, True)
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
        lignes = len(grille)
        colonnes = len(grille[0])
        score = 0

        col_centre = [grille[r][colonnes // 2] for r in range(lignes)]
        score += col_centre.count(piece) * 3

        for r in range(lignes):
            ligne_array = grille[r]
            for c in range(colonnes - 3):
                score += self.evaluer_fenetre(ligne_array[c : c + 4], piece)

        for c in range(colonnes):
            col_array = [grille[r][c] for r in range(lignes)]
            for r in range(lignes - 3):
                score += self.evaluer_fenetre(col_array[r : r + 4], piece)

        for r in range(lignes - 3):
            for c in range(colonnes - 3):
                fen = [grille[r + i][c + i] for i in range(4)]
                score += self.evaluer_fenetre(fen, piece)

        for r in range(lignes - 3):
            for c in range(colonnes - 3):
                fen = [grille[r + 3 - i][c + i] for i in range(4)]
                score += self.evaluer_fenetre(fen, piece)

        return score

    def noeud_terminal(self, grille):
        return (
            self.verifier_gagnant(grille, 1)
            or self.verifier_gagnant(grille, 2)
            or len(self.obtenir_cols_valides(grille)) == 0
        )

    def minimax(self, grille, depth, alpha, beta, maximizingPlayer):
        cols_valides = self.obtenir_cols_valides(grille)
        est_terminal = self.noeud_terminal(grille)

        if depth == 0 or est_terminal:
            if est_terminal:
                if self.verifier_gagnant(grille, self.numero_pion):
                    return (None, 10**14)
                elif self.verifier_gagnant(grille, 1 if self.numero_pion == 2 else 2):
                    return (None, -(10**13))
                else:
                    return (None, 0)
            return (None, self.score_position(grille, self.numero_pion))

        if maximizingPlayer:
            value = -math.inf
            colonne = random.choice(cols_valides)
            for col in cols_valides:
                row = self.obtenir_prochaine_ligne(grille, col)
                b_copy = copy.deepcopy(grille)
                b_copy[row][col] = self.numero_pion
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, False)[1]
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
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    colonne = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return colonne, value

    def obtenir_cols_valides(self, grille):
        colonnes = len(grille[0])
        return [c for c in range(colonnes) if grille[0][c] == 0]

    def obtenir_prochaine_ligne(self, grille, col):
        lignes = len(grille)
        for r in range(lignes - 1, -1, -1):
            if grille[r][col] == 0:
                return r
        return -1

    def verifier_gagnant(self, grille, piece):
        lignes = len(grille)
        colonnes = len(grille[0])
        for c in range(colonnes - 3):
            for r in range(lignes):
                if all(grille[r][c + i] == piece for i in range(4)):
                    return True
        for c in range(colonnes):
            for r in range(lignes - 3):
                if all(grille[r + i][c] == piece for i in range(4)):
                    return True
        for c in range(colonnes - 3):
            for r in range(3, lignes):
                if all(grille[r - i][c + i] == piece for i in range(4)):
                    return True
        for c in range(colonnes - 3):
            for r in range(lignes - 3):
                if all(grille[r + i][c + i] == piece for i in range(4)):
                    return True
        return False


# =========================
# PLATEAU
# =========================
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
                if all(self.grille[r][c + i] == pion for i in range(4)):
                    return True
        for c in range(self.colonnes):
            for r in range(self.lignes - 3):
                if all(self.grille[r + i][c] == pion for i in range(4)):
                    return True
        for c in range(self.colonnes - 3):
            for r in range(3, self.lignes):
                if all(self.grille[r - i][c + i] == pion for i in range(4)):
                    return True
        for c in range(self.colonnes - 3):
            for r in range(self.lignes - 3):
                if all(self.grille[r + i][c + i] == pion for i in range(4)):
                    return True
        return False

    def reinitialiser(self):
        self.grille = self._creer_grille()


# =========================
# JEU
# =========================
class Jeu:
    def __init__(self):
        pygame.init()

        # ✅ Fenêtre taille écran, décorée (déplaçable + réductible), NON redimensionnable
        info = pygame.display.Info()
        self.screen_w = info.current_w
        self.screen_h = info.current_h
        self.ecran = pygame.display.set_mode((self.screen_w, self.screen_h))  # pas de FULLSCREEN, pas RESIZABLE

        pygame.display.set_caption("Puissance 4 - Ultimate")
        self.clock = pygame.time.Clock()

        self.police = pygame.font.SysFont("Arial", POLICE_TAILLE, bold=True)
        self.police_bouton = pygame.font.SysFont("Arial", 40, bold=True)
        self.police_petite = pygame.font.SysFont("Arial", 28, bold=True)
        self.police_chrono = pygame.font.SysFont("Consolas", 40, bold=True)
        self.police_regles = pygame.font.SysFont("Arial", 24)

        self.mode_sombre = False
        self.theme = THEME_CLAIR

        self.etat_jeu = "MENU"
        self.mode_ia = False
        self.niveau_ia = 1

        self.colonnes, self.lignes = GRILLES_DISPONIBLES[0]
        self.scale = 1.0
        self.cell_px = TAILLE_CASE
        self.drapeau_px = TAILLE_CASE - 2 * MARGE_DRAPEAU
        self.grid_w_px = self.colonnes * self.cell_px
        self.grid_h_px = self.lignes * self.cell_px
        self.grid_origin_x = 0
        self.grid_origin_y = 0

        self.plateau = Plateau(self.lignes, self.colonnes)
        self.pays_selectionnes = [0, 1]
        self.joueurs = []

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

        self._recalc_layout_and_assets()

    # =========================
    # THÈME / SCALE
    # =========================
    def toggle_theme(self):
        self.mode_sombre = not self.mode_sombre
        self.theme = THEME_SOMBRE if self.mode_sombre else THEME_CLAIR

    def _compute_scale(self):
        bottom_reserved = 100
        max_w = self.screen_w - 2 * MARGE_X
        max_h = self.screen_h - (MARGE_Y + ESPACE_ENTETE + MARGE_Y + bottom_reserved)
        base_w = self.colonnes * TAILLE_CASE
        base_h = self.lignes * TAILLE_CASE
        s = min(max_w / base_w, max_h / base_h, 1.0)
        s = max(0.55, s)
        return s

    def _recalc_layout_and_assets(self):
        self.scale = self._compute_scale()
        self.cell_px = int(TAILLE_CASE * self.scale)
        self.drapeau_px = int((TAILLE_CASE - 2 * MARGE_DRAPEAU) * self.scale)
        self.grid_w_px = self.colonnes * self.cell_px
        self.grid_h_px = self.lignes * self.cell_px
        self.grid_origin_x = (self.screen_w - self.grid_w_px) // 2
        self.grid_origin_y = MARGE_Y + ESPACE_ENTETE
        self.surface_grille_bleue = self._creer_surface_grille()

        for j in self.joueurs:
            j.refresh_drapeau(self.drapeau_px)

    def appliquer_taille_grille(self, colonnes, lignes):
        self.colonnes, self.lignes = colonnes, lignes
        self._recalc_layout_and_assets()
        if self.etat_jeu != "JEU":
            self.plateau = Plateau(self.lignes, self.colonnes)

    def _creer_surface_grille(self):
        base_w = self.colonnes * TAILLE_CASE
        base_h = self.lignes * TAILLE_CASE
        base = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
        base.fill(BLEU_GRILLE_MODERNE)
        for c in range(self.colonnes):
            for r in range(self.lignes):
                cx = int(c * TAILLE_CASE + TAILLE_CASE / 2)
                cy = int(r * TAILLE_CASE + TAILLE_CASE / 2)
                pygame.draw.circle(base, (0, 0, 0, 0), (cx, cy), RAYON_PION)
        return pygame.transform.smoothscale(base, (self.grid_w_px, self.grid_h_px))

    # =========================
    # UI HELPERS
    # =========================
    def _dessiner_bouton(self, rect, texte, couleur, texte_couleur=(255, 255, 255), bord=True, rayon=12):
        pygame.draw.rect(self.ecran, couleur, rect, border_radius=rayon)
        if bord:
            pygame.draw.rect(self.ecran, self.theme["panel_bord"], rect, width=2, border_radius=rayon)
        surf = self.police_petite.render(texte, True, texte_couleur)
        self.ecran.blit(surf, surf.get_rect(center=rect.center))

    # =========================
    # MENU PRINCIPAL
    # =========================
    def afficher_menu(self):
        self.ecran.fill(self.theme["fond"])
        mouse_pos = pygame.mouse.get_pos()

        titre_surf = self.police.render("PUISSANCE 4", True, self.theme["texte"])
        self.ecran.blit(titre_surf, titre_surf.get_rect(center=(self.screen_w / 2, 90)))

        # Bloc ami
        bloc_ami = pygame.Rect(60, 150, self.screen_w - 120, 170)
        pygame.draw.rect(self.ecran, self.theme["panel"], bloc_ami, border_radius=18)
        pygame.draw.rect(self.ecran, self.theme["panel_bord"], bloc_ami, 2, border_radius=18)

        txt_ami = self.police_bouton.render("Jouer avec un ami", True, self.theme["texte"])
        self.ecran.blit(txt_ami, (bloc_ami.x + 25, bloc_ami.y + 20))

        btn_1v1 = pygame.Rect(0, 0, 260, 70)
        btn_1v1.center = (bloc_ami.centerx, bloc_ami.y + 115)

        couleur_btn_1v1 = COULEUR_BOUTON_HOVER if btn_1v1.collidepoint(mouse_pos) else COULEUR_BOUTON
        pygame.draw.rect(self.ecran, couleur_btn_1v1, btn_1v1, border_radius=14)
        pygame.draw.rect(self.ecran, self.theme["panel_bord"], btn_1v1, 2, border_radius=14)

        # ✅ Toujours blanc
        t1 = self.police_bouton.render("1v1", True, (255, 255, 255))
        self.ecran.blit(t1, t1.get_rect(center=btn_1v1.center))

        # ✅ Bloc IA agrandi pour que Difficile ne déborde plus
        bloc_ia = pygame.Rect(60, 350, self.screen_w - 120, 360) 
        pygame.draw.rect(self.ecran, self.theme["panel"], bloc_ia, border_radius=18)
        pygame.draw.rect(self.ecran, self.theme["panel_bord"], bloc_ia, 2, border_radius=18)

        txt_ia = self.police_bouton.render("Jouer contre l'IA", True, self.theme["texte"])
        self.ecran.blit(txt_ia, (bloc_ia.x + 25, bloc_ia.y + 20))

        btn_facile = pygame.Rect(0, 0, 260, 70)
        btn_moyen = pygame.Rect(0, 0, 260, 70)
        btn_dur = pygame.Rect(0, 0, 260, 70)

        btn_facile.center = (bloc_ia.centerx, bloc_ia.y + 120)
        btn_moyen.center = (bloc_ia.centerx, bloc_ia.y + 205)
        btn_dur.center = (bloc_ia.centerx, bloc_ia.y + 290) 


        def draw_diff(btn, label, color):
            pygame.draw.rect(self.ecran, color, btn, border_radius=14)
            pygame.draw.rect(self.ecran, self.theme["panel_bord"], btn, 2, border_radius=14)
            txt = self.police_petite.render(label, True, (255, 255, 255))
            self.ecran.blit(txt, txt.get_rect(center=btn.center))

        draw_diff(btn_facile, "Facile", COULEUR_IA_FACILE)
        draw_diff(btn_moyen, "Moyen", COULEUR_IA_MOYEN)
        draw_diff(btn_dur, "Difficile", COULEUR_IA_DIFFICILE)

        # Boutons bas : règles / crédits / thème / quitter
        btn_regles = pygame.Rect(30, self.screen_h - 80, 160, 50)
        btn_credits = pygame.Rect(210, self.screen_h - 80, 160, 50)
        btn_theme = pygame.Rect(self.screen_w - 410, self.screen_h - 80, 180, 50)
        btn_quitter = pygame.Rect(self.screen_w - 210, self.screen_h - 80, 180, 50)

        self._dessiner_bouton(btn_regles, "RÈGLES", BLEU_INFO, (255, 255, 255), rayon=10)
        self._dessiner_bouton(btn_credits, "CRÉDITS", VIOLET_CREDITS, (255, 255, 255), rayon=10)
        theme_txt = "Mode clair" if self.mode_sombre else "Mode sombre"
        self._dessiner_bouton(btn_theme, theme_txt, (127, 140, 141), (255, 255, 255), rayon=10)
        self._dessiner_bouton(btn_quitter, "Quitter", ROUGE_ALERT, (255, 255, 255), rayon=10)

        return btn_1v1, btn_facile, btn_moyen, btn_dur, btn_regles, btn_credits, btn_theme, btn_quitter

    # =========================
    # CRÉDITS
    # =========================
    def afficher_credits(self):
        self.ecran.fill(self.theme["fond"])

        cadre = pygame.Rect(0, 0, min(760, self.screen_w - 140), 460)
        cadre.center = (self.screen_w // 2, self.screen_h // 2)
        pygame.draw.rect(self.ecran, self.theme["panel"], cadre, border_radius=20)
        pygame.draw.rect(self.ecran, self.theme["panel_bord"], cadre, 3, border_radius=20)

        titre = self.police_bouton.render("CRÉDITS", True, self.theme["texte"])
        self.ecran.blit(titre, titre.get_rect(center=(cadre.centerx, cadre.y + 70)))

        lignes = [
            "Ce jeu est fait par :",
            "",
            "Jibril BOUCHAM",
            "Sulliman CHETOUANI",
            "Yassine TAMINE",
        ]
        y = cadre.y + 140
        for l in lignes:
            txt = self.police_regles.render(l, True, self.theme["texte"])
            self.ecran.blit(txt, txt.get_rect(center=(cadre.centerx, y)))
            y += 42

        btn_retour = pygame.Rect(0, 0, 240, 60)
        btn_retour.center = (cadre.centerx, cadre.bottom - 80)
        self._dessiner_bouton(btn_retour, "RETOUR", ROUGE_ALERT, (255, 255, 255), rayon=12)

        return btn_retour

    # =========================
    # RÈGLES
    # =========================
    def afficher_regles(self):
        s = pygame.Surface((self.screen_w, self.screen_h))
        s.set_alpha(240)
        s.fill(self.theme["fond"])
        self.ecran.blit(s, (0, 0))

        cadre = pygame.Rect(
    0,
    0,
    min(self.screen_w - 100, 1200),  # beaucoup plus large
    min(self.screen_h - 140, 650)
)

        cadre.center = (self.screen_w // 2, self.screen_h // 2)
        pygame.draw.rect(self.ecran, self.theme["panel"], cadre, border_radius=20)
        pygame.draw.rect(self.ecran, self.theme["panel_bord"], cadre, 3, border_radius=20)

        titre = self.police_bouton.render("RÈGLES DU JEU", True, self.theme["texte"])
        self.ecran.blit(titre, titre.get_rect(center=(cadre.centerx, cadre.y + 55)))

        lignes = [
            "BUT DU JEU :",
            "Aligner 4 pions horizontalement, verticalement ou en diagonale.",
            "",
            "TEMPS PAR COUP :",
            "Vous avez 30 seoncdes pour jouer. Si vous ne jouez pas",
            "au bout de ces 30 secondes, votre pion est placé aléatoirement.",
            "",
            "BOUTON MISSCLICK :",
            "Chaque joueur peut annuler son dernier coup 1 fois par",
            "match via le bouton violet  Annuler mon dernier coup.",
            "",
            "TAILLE DE LA GRILLE :",
            "Vous pouvez modifier la taille de la grille",
            "de votre puissance 4 : 7*6 (classique), 8*7 ou 9*8.",
            "",
            "MODES :",
            "- Jouer contre l'IA : Niveau facile, moyen ou difficile.",
            "- 1v1 : Jouer avec un ami en manches de plusieurs matchs.",
        ]

        y_txt = cadre.y + 115
        max_y_txt = cadre.bottom - 130
        for ligne in lignes:
            if y_txt > max_y_txt:
                break
            txt = self.police_regles.render(ligne, True, self.theme["texte"])
            self.ecran.blit(txt, (cadre.x + 30, y_txt))
            y_txt += 30

        btn_retour = pygame.Rect(0, 0, 240, 60)
        btn_retour.center = (cadre.centerx, cadre.bottom - 70)
        self._dessiner_bouton(btn_retour, "RETOUR", ROUGE_ALERT, (255, 255, 255), rayon=12)
        return btn_retour

    # =========================
    # SELECTION PAYS + OPTIONS
    # =========================
    def changer_pays(self, joueur_idx, direction):
        autre = (joueur_idx + 1) % 2
        interdit = self.pays_selectionnes[autre]
        nouveau = (self.pays_selectionnes[joueur_idx] + direction) % len(PAYS_DISPONIBLES)
        while nouveau == interdit:
            nouveau = (nouveau + direction) % len(PAYS_DISPONIBLES)
        self.pays_selectionnes[joueur_idx] = nouveau

    def afficher_selection_pays(self):
        self.ecran.fill(self.theme["fond"])
        titre = self.police_bouton.render("Paramètres de la partie", True, self.theme["texte"])
        self.ecran.blit(titre, titre.get_rect(center=(self.screen_w // 2, 50)))

        # Taille de grille
        box_grille = pygame.Rect(0, 0, min(900, self.screen_w - 200), 95)
        box_grille.center = (self.screen_w // 2, 140)
        pygame.draw.rect(self.ecran, self.theme["panel"], box_grille, border_radius=16)
        pygame.draw.rect(self.ecran, self.theme["panel_bord"], box_grille, 2, border_radius=16)

        txt_grille = self.police_petite.render("Taille de la grille :", True, self.theme["texte"])
        self.ecran.blit(txt_grille, (box_grille.x + 20, box_grille.y + 12))

        btn_grilles = []
        start_x = box_grille.x + 260
        for i, (c, l) in enumerate(GRILLES_DISPONIBLES):
            btn = pygame.Rect(start_x + i * 150, box_grille.y + 45, 135, 38)
            actif = (self.colonnes, self.lignes) == (c, l)
            couleur = COULEUR_BOUTON if actif else ((110, 110, 110) if self.mode_sombre else (210, 210, 210))
            txtc = (255, 255, 255) if actif else self.theme["texte"]
            self._dessiner_bouton(btn, f"{c}x{l}", couleur, txtc, rayon=10)
            btn_grilles.append(((c, l), btn))

        # Manches (1v1)
        btn_moins = btn_plus = None
        if not self.mode_ia:
            box_manches = pygame.Rect(0, 0, min(900, self.screen_w - 200), 95)
            box_manches.center = (self.screen_w // 2, 255)
            pygame.draw.rect(self.ecran, self.theme["panel"], box_manches, border_radius=16)
            pygame.draw.rect(self.ecran, self.theme["panel_bord"], box_manches, 2, border_radius=16)

            label = self.police_petite.render(f"Manches de {self.score_cible} matchs", True, self.theme["texte"])
            self.ecran.blit(label, label.get_rect(center=(box_manches.centerx, box_manches.y + 30)))

            btn_moins = pygame.Rect(box_manches.centerx - 130, box_manches.y + 55, 95, 32)
            btn_plus = pygame.Rect(box_manches.centerx + 35, box_manches.y + 55, 95, 32)
            self._dessiner_bouton(btn_moins, "-", COULEUR_BOUTON, (255, 255, 255), rayon=10)
            self._dessiner_bouton(btn_plus, "+", COULEUR_BOUTON, (255, 255, 255), rayon=10)

        # Choix pays (décalé à droite)
        base_y = 355 if not self.mode_ia else 295
        x_label = 120
        x_bloc = self.screen_w // 2 + 120
        bloc_w, bloc_h = 240, 110

        for i in range(2):
            y = base_y + i * 190
            nom = f"Joueur {i+1}"
            if self.mode_ia and i == 1:
                niv = ["Facile", "Moyen", "Difficile"][self.niveau_ia - 1]
                nom = f"Ordinateur : {niv}"
            txt_j = self.police_bouton.render(nom, True, self.theme["texte"])
            self.ecran.blit(txt_j, (x_label, y + 20))

            cadre_rect = pygame.Rect(x_bloc, y, bloc_w, bloc_h)
            pygame.draw.rect(self.ecran, self.theme["panel"], cadre_rect, border_radius=12)
            pygame.draw.rect(self.ecran, self.theme["panel_bord"], cadre_rect, 2, border_radius=12)

            pays = PAYS_DISPONIBLES[self.pays_selectionnes[i]]
            drapeau = pays.charger_drapeau(self.drapeau_px)
            self.ecran.blit(drapeau, drapeau.get_rect(center=cadre_rect.center))

            btn_g = pygame.Rect(cadre_rect.x - 75, y + 25, 60, 60)
            btn_d = pygame.Rect(cadre_rect.right + 15, y + 25, 60, 60)

            pygame.draw.rect(self.ecran, COULEUR_BOUTON, btn_g, border_radius=12)
            pygame.draw.rect(self.ecran, self.theme["panel_bord"], btn_g, 2, border_radius=12)
            pygame.draw.rect(self.ecran, COULEUR_BOUTON, btn_d, border_radius=12)
            pygame.draw.rect(self.ecran, self.theme["panel_bord"], btn_d, 2, border_radius=12)

            self.ecran.blit(self.police_bouton.render("<", True, (255, 255, 255)), self.police_bouton.render("<", True, (255,255,255)).get_rect(center=btn_g.center))
            self.ecran.blit(self.police_bouton.render(">", True, (255, 255, 255)), self.police_bouton.render(">", True, (255,255,255)).get_rect(center=btn_d.center))

        # Boutons bas : Retour + Démarrer centrés
        btn_retour_menu = pygame.Rect(0, 0, 260, 65)
        btn_demarrer = pygame.Rect(0, 0, 260, 65)
        spacing = 40
        total_w = btn_retour_menu.width + spacing + btn_demarrer.width
        start_x = (self.screen_w - total_w) // 2
        y_btn = self.screen_h - 95

        btn_retour_menu.topleft = (start_x, y_btn)
        btn_demarrer.topleft = (start_x + btn_retour_menu.width + spacing, y_btn)

        self._dessiner_bouton(btn_retour_menu, "Retour au menu", ROUGE_ALERT, (255, 255, 255), rayon=14)
        self._dessiner_bouton(btn_demarrer, "Démarrer", COULEUR_BOUTON, (255, 255, 255), rayon=14)

        # Rects flèches
        arrow_rects = []
        for i in range(2):
            y = base_y + i * 190
            cadre_rect = pygame.Rect(x_bloc, y, bloc_w, bloc_h)
            btn_g = pygame.Rect(cadre_rect.x - 75, y + 25, 60, 60)
            btn_d = pygame.Rect(cadre_rect.right + 15, y + 25, 60, 60)
            arrow_rects.append((btn_g, btn_d))

        return btn_demarrer, btn_retour_menu, btn_moins, btn_plus, btn_grilles, arrow_rects

    # =========================
    # PAUSE
    # =========================
    def afficher_pause(self):
        s = pygame.Surface((self.screen_w, self.screen_h))
        s.set_alpha(180)
        s.fill((0, 0, 0))
        self.ecran.blit(s, (0, 0))

        rect_menu = pygame.Rect(0, 0, 440, 320)
        rect_menu.center = (self.screen_w // 2, self.screen_h // 2)
        pygame.draw.rect(self.ecran, self.theme["panel"], rect_menu, border_radius=20)
        pygame.draw.rect(self.ecran, self.theme["panel_bord"], rect_menu, 3, border_radius=20)

        txt_pause = self.police.render("PAUSE", True, self.theme["texte"])
        self.ecran.blit(txt_pause, txt_pause.get_rect(center=(rect_menu.centerx, rect_menu.y + 75)))

        btn_reprendre = pygame.Rect(0, 0, 280, 60)
        btn_reprendre.center = (rect_menu.centerx, rect_menu.y + 165)
        self._dessiner_bouton(btn_reprendre, "Reprendre", COULEUR_BOUTON, (255, 255, 255), rayon=12)

        btn_quitter = pygame.Rect(0, 0, 280, 60)
        btn_quitter.center = (rect_menu.centerx, rect_menu.y + 240)
        self._dessiner_bouton(btn_quitter, "Menu Principal", ROUGE_ALERT, (255, 255, 255), rayon=12)

        return btn_reprendre, btn_quitter

    # =========================
    # FIN MATCH 1v1
    # =========================
    def afficher_ecran_victoire_match(self):
        s = pygame.Surface((self.screen_w, self.screen_h))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        self.ecran.blit(s, (0, 0))

        rect_win = pygame.Rect(0, 0, 660, 440)
        rect_win.center = (self.screen_w // 2, self.screen_h // 2)
        pygame.draw.rect(self.ecran, self.theme["panel"], rect_win, border_radius=20)
        pygame.draw.rect(self.ecran, OR_VICTOIRE, rect_win, 8, border_radius=20)

        txt_felicitation = self.police.render("FÉLICITATIONS !", True, self.theme["texte"])
        self.ecran.blit(txt_felicitation, txt_felicitation.get_rect(center=(rect_win.centerx, rect_win.y + 90)))

        nom_gagnant = self.joueurs[self.tour_index].pays.nom
        txt_vainqueur = self.police_bouton.render(f"Vainqueur : {nom_gagnant}", True, OR_VICTOIRE)
        self.ecran.blit(txt_vainqueur, txt_vainqueur.get_rect(center=(rect_win.centerx, rect_win.y + 210)))

        btn_action = pygame.Rect(0, 0, 340, 70)
        btn_action.center = (rect_win.centerx, rect_win.y + 330)
        self._dessiner_bouton(btn_action, "RETOUR MENU", ROUGE_ALERT, (255, 255, 255), rayon=12)

        return btn_action

    # =========================
    # CLICS
    # =========================
    def gerer_clic_souris(self, pos):
        if self.etat_jeu == "SELECTION_PAYS":
            btn_demarrer, btn_retour, btn_moins, btn_plus, btn_grilles, arrow_rects = self.afficher_selection_pays()

            if btn_retour.collidepoint(pos):
                self.etat_jeu = "MENU"
                return

            for (c, l), btn in btn_grilles:
                if btn.collidepoint(pos):
                    self.appliquer_taille_grille(c, l)
                    return

            if btn_moins and btn_moins.collidepoint(pos):
                self.score_cible = max(1, self.score_cible - 1)
                return
            if btn_plus and btn_plus.collidepoint(pos):
                self.score_cible = min(5, self.score_cible + 1)
                return

            for i, (btn_g, btn_d) in enumerate(arrow_rects):
                if btn_g.collidepoint(pos):
                    self.changer_pays(i, -1)
                    return
                if btn_d.collidepoint(pos):
                    self.changer_pays(i, +1)
                    return

            if btn_demarrer.collidepoint(pos):
                self.demarrer_jeu()
                return

        elif self.etat_jeu == "REGLES":
            btn_retour = self.afficher_regles()
            if btn_retour.collidepoint(pos):
                self.etat_jeu = "MENU"

        elif self.etat_jeu == "CREDITS":
            btn_retour = self.afficher_credits()
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

            btn_pause = pygame.Rect(self.screen_w - 160, 20, 140, 50)
            if btn_pause.collidepoint(pos):
                self.etat_jeu = "PAUSE"
                return

            if not self.jeu_termine and not self.anim_en_cours and not self.match_termine:
                btn_missclick_j1 = pygame.Rect(40, self.screen_h - 70, 420, 50)
                if btn_missclick_j1.collidepoint(pos):
                    self.action_missclick(0)
                    return

                if not self.mode_ia:
                    btn_missclick_j2 = pygame.Rect(self.screen_w - 460, self.screen_h - 70, 420, 50)
                    if btn_missclick_j2.collidepoint(pos):
                        self.action_missclick(1)
                        return

            if self.jeu_termine:
                self.reinitialiser_jeu()

    # =========================
    # START / RESET
    # =========================
    def demarrer_jeu(self):
        p1 = JoueurHumain(1, PAYS_DISPONIBLES[self.pays_selectionnes[0]], self.drapeau_px)
        if self.mode_ia:
            p2 = JoueurOrdinateur(2, PAYS_DISPONIBLES[self.pays_selectionnes[1]], self.niveau_ia, self.drapeau_px)
        else:
            p2 = JoueurHumain(2, PAYS_DISPONIBLES[self.pays_selectionnes[1]], self.drapeau_px)

        self.joueurs = [p1, p2]
        self.etat_jeu = "JEU"
        self.plateau = Plateau(self.lignes, self.colonnes)
        self.tour_index = 0
        self.jeu_termine = False
        self.match_termine = False
        self.anim_en_cours = False
        self.temps_restant = TEMPS_PAR_TOUR

        self.missclick_dispo = [True, True]
        self.historique_coups = []
        self._recalc_layout_and_assets()

    def reinitialiser_jeu(self):
        self.plateau.reinitialiser()
        self.jeu_termine = False
        self.tour_index = (self.scores[0] + self.scores[1]) % 2
        self.anim_en_cours = False
        self.temps_restant = TEMPS_PAR_TOUR
        self.missclick_dispo = [True, True]
        self.historique_coups = []

    # =========================
    # MISSCLICK
    # =========================
    def action_missclick(self, joueur_idx):
        if not self.missclick_dispo[joueur_idx] or not self.historique_coups:
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
            return

        if not self.mode_ia:
            dernier_coup = self.historique_coups[-1]
            if dernier_coup[2] == joueur_idx:
                move = self.historique_coups.pop()
                self.plateau.retirer_pion(move[0], move[1])
                self.missclick_dispo[joueur_idx] = False
                self.tour_index = joueur_idx
                self.temps_restant = TEMPS_PAR_TOUR

    # =========================
    # ANIMATION / COUPS
    # =========================
    def debuter_coup(self, col):
        if not self.plateau.est_colonne_valide(col) or self.anim_en_cours:
            return
        ligne = self.plateau.obtenir_prochaine_ligne_libre(col)
        if ligne == -1:
            return

        self.anim_en_cours = True
        self.anim_col = col
        self.anim_ligne_cible = ligne
        self.anim_y_actuel = self.grid_origin_y - self.cell_px
        self.anim_y_cible = self.grid_origin_y + ligne * self.cell_px

    def mettre_a_jour_animation(self):
        if not self.anim_en_cours:
            return

        self.anim_y_actuel += int(VITESSE_CHUTE * max(0.6, self.scale))
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

    # =========================
    # DESSIN JEU
    # =========================
    def dessiner_plateau_et_animation(self, mouse_x=None):
        self.ecran.fill(self.theme["fond"])

        # ✅ Score avec noms : "Algérie 2 - 1 Maroc"
        nom1 = self.joueurs[0].pays.nom if self.joueurs else "J1"
        nom2 = self.joueurs[1].pays.nom if self.joueurs else "J2"
        txt_scores = self.police_petite.render(f"{nom1} {self.scores[0]} - {self.scores[1]} {nom2}", True, self.theme["texte"])
        self.ecran.blit(txt_scores, (30, 20))

        # ✅ Objectif : "Objectif : X victoires"
        if not self.mode_ia:
            txt_obj = self.police_petite.render(f"Objectif : {self.score_cible} victoires", True, self.theme["texte"])
            self.ecran.blit(txt_obj, (30, 55))

        # Chrono 1v1
        if not self.mode_ia and not self.jeu_termine:
            couleur_chrono = self.theme["texte"] if self.temps_restant > 5 else ROUGE_ALERT
            txt_chrono = self.police_chrono.render(f"00:{self.temps_restant:02d}", True, couleur_chrono)
            self.ecran.blit(txt_chrono, txt_chrono.get_rect(center=(self.screen_w // 2, 50)))

        btn_pause = pygame.Rect(self.screen_w - 160, 20, 140, 50)
        self._dessiner_bouton(btn_pause, "PAUSE", BLEU_INFO, (255, 255, 255), rayon=10)

        # Annuler
        if not self.jeu_termine and not self.match_termine:
            btn_j1 = pygame.Rect(40, self.screen_h - 70, 420, 50)
            couleur_j1 = VIOLET_MISSCLICK if self.missclick_dispo[0] else self.theme["gris_desactive"]
            actif = self.missclick_dispo[0]
            if self.mode_ia and len(self.historique_coups) < 2:
                actif = False
            if not self.mode_ia and (not self.historique_coups or self.historique_coups[-1][2] != 0):
                actif = False
            if not actif:
                couleur_j1 = self.theme["gris_desactive"]
            self._dessiner_bouton(btn_j1, "Annuler mon dernier coup", couleur_j1, (255, 255, 255), rayon=10)

            if not self.mode_ia:
                btn_j2 = pygame.Rect(self.screen_w - 460, self.screen_h - 70, 420, 50)
                couleur_j2 = VIOLET_MISSCLICK if self.missclick_dispo[1] else self.theme["gris_desactive"]
                actif2 = self.missclick_dispo[1]
                if not self.historique_coups or self.historique_coups[-1][2] != 1:
                    actif2 = False
                if not actif2:
                    couleur_j2 = self.theme["gris_desactive"]
                self._dessiner_bouton(btn_j2, "Annuler mon dernier coup", couleur_j2, (255, 255, 255), rayon=10)

        # pions fixes
        for c in range(self.colonnes):
            for r in range(self.lignes):
                val = self.plateau.grille[r][c]
                if val != 0:
                    drapeau = self.joueurs[val - 1].obtenir_drapeau()
                    x = self.grid_origin_x + c * self.cell_px + int(MARGE_DRAPEAU * self.scale)
                    y = self.grid_origin_y + r * self.cell_px + int(MARGE_DRAPEAU * self.scale)
                    self.ecran.blit(drapeau, (x, y))

        # pion animé
        if self.anim_en_cours:
            drapeau_anim = self.joueurs[self.tour_index].obtenir_drapeau()
            x = self.grid_origin_x + self.anim_col * self.cell_px + int(MARGE_DRAPEAU * self.scale)
            y = int(self.anim_y_actuel) + int(MARGE_DRAPEAU * self.scale)
            self.ecran.blit(drapeau_anim, (x, y))

        # grille
        self.ecran.blit(self.surface_grille_bleue, (self.grid_origin_x, self.grid_origin_y))

        # hover
        if (
            not self.jeu_termine
            and not self.anim_en_cours
            and mouse_x is not None
            and self.joueurs
            and not self.joueurs[self.tour_index].est_ia()
            and self.etat_jeu != "PAUSE"
            and not self.match_termine
        ):
            drapeau = self.joueurs[self.tour_index].obtenir_drapeau()
            pos_y = self.grid_origin_y - self.drapeau_px
            pos_x = mouse_x - (self.drapeau_px // 2)
            limite_gauche = self.grid_origin_x + int(MARGE_DRAPEAU * self.scale)
            limite_droite = self.grid_origin_x + self.grid_w_px - self.drapeau_px - int(MARGE_DRAPEAU * self.scale)
            pos_x = max(limite_gauche, min(limite_droite, pos_x))
            self.ecran.blit(drapeau, (pos_x, pos_y))

        # victoire manche
        if self.jeu_termine and not self.match_termine:
            bandeau = pygame.Surface((self.screen_w, 110))
            bandeau.set_alpha(230)
            bandeau.fill(OR_VICTOIRE)
            self.ecran.blit(bandeau, (0, self.screen_h // 2 - 55))

            if self.mode_ia:
                msg = "L'IA REMPORTE LA MANCHE !" if self.joueurs[self.tour_index].est_ia() else "VOUS REMPORTEZ LA MANCHE !"
            else:
                msg = f"MANCHE POUR {self.joueurs[self.tour_index].pays.nom.upper()} !"

            txt_main = self.police_bouton.render(msg, True, (0, 0, 0))
            txt_sub = self.police_petite.render("CLIQUEZ POUR CONTINUER...", True, (0, 0, 0))
            self.ecran.blit(txt_main, txt_main.get_rect(center=(self.screen_w // 2, self.screen_h // 2 - 15)))
            self.ecran.blit(txt_sub, txt_sub.get_rect(center=(self.screen_w // 2, self.screen_h // 2 + 35)))

        if self.match_termine and not self.mode_ia:
            self.afficher_ecran_victoire_match()

    # =========================
    # BOUCLE PRINCIPALE
    # =========================
    def boucle_principale(self):
        mouse_x = self.screen_w // 2

        while True:
            # IA / Chrono
            if self.etat_jeu == "JEU" and not self.jeu_termine and not self.anim_en_cours and self.joueurs:
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
                                valides = [c for c in range(self.colonnes) if self.plateau.est_colonne_valide(c)]
                                if valides:
                                    self.debuter_coup(random.choice(valides))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    mouse_x = event.pos[0]

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.etat_jeu == "MENU":
                        btn_1v1, btn_fac, btn_moy, btn_dur, btn_regles, btn_credits, btn_theme, btn_quitter = self.afficher_menu()

                        if btn_1v1.collidepoint(event.pos):
                            self.mode_ia = False
                            self.score_cible = MANCHES_PAR_DEFAUT
                            self.etat_jeu = "SELECTION_PAYS"

                        elif btn_fac.collidepoint(event.pos):
                            self.mode_ia = True
                            self.niveau_ia = 1
                            self.etat_jeu = "SELECTION_PAYS"

                        elif btn_moy.collidepoint(event.pos):
                            self.mode_ia = True
                            self.niveau_ia = 2
                            self.etat_jeu = "SELECTION_PAYS"

                        elif btn_dur.collidepoint(event.pos):
                            self.mode_ia = True
                            self.niveau_ia = 3
                            self.etat_jeu = "SELECTION_PAYS"

                        elif btn_regles.collidepoint(event.pos):
                            self.etat_jeu = "REGLES"

                        elif btn_credits.collidepoint(event.pos):
                            self.etat_jeu = "CREDITS"

                        elif btn_theme.collidepoint(event.pos):
                            self.toggle_theme()

                        elif btn_quitter.collidepoint(event.pos):
                            pygame.quit()
                            sys.exit()

                    elif self.etat_jeu == "JEU":
                        if self.match_termine:
                            self.gerer_clic_souris(event.pos)
                            continue

                        btn_pause = pygame.Rect(self.screen_w - 160, 20, 140, 50)
                        btn_miss_p1 = pygame.Rect(40, self.screen_h - 70, 420, 50)
                        btn_miss_p2 = pygame.Rect(self.screen_w - 460, self.screen_h - 70, 420, 50)

                        if btn_pause.collidepoint(event.pos) or btn_miss_p1.collidepoint(event.pos) or (not self.mode_ia and btn_miss_p2.collidepoint(event.pos)):
                            self.gerer_clic_souris(event.pos)
                            continue

                        if self.jeu_termine:
                            self.gerer_clic_souris(event.pos)
                        elif not self.anim_en_cours:
                            joueur_actuel = self.joueurs[self.tour_index]
                            if not joueur_actuel.est_ia():
                                rel_x = event.pos[0] - self.grid_origin_x
                                rel_y = event.pos[1] - self.grid_origin_y
                                if 0 <= rel_x < self.grid_w_px and 0 <= rel_y < self.grid_h_px:
                                    col = int(rel_x / self.cell_px)
                                    self.debuter_coup(col)

                    else:
                        self.gerer_clic_souris(event.pos)

            # Draw
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
            elif self.etat_jeu == "CREDITS":
                self.afficher_credits()

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    try:
        Jeu().boucle_principale()
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        pygame.quit()
        sys.exit()
