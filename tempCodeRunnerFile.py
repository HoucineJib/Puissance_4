import pygame
import sys
import math

# --- 1. Paramètres Globaux ---
LIGNES = 6
COLONNES = 7
TAILLE_CASE = 100

# Paramètres des drapeaux
MARGE_DRAPEAU = 6
TAILLE_DRAPEAU = TAILLE_CASE - MARGE_DRAPEAU * 2
RAYON_PION = int(TAILLE_CASE / 2 - 8)

# Marges
MARGE_X = 50
MARGE_Y = 50
ESPACE_ENTETE = 100

# Dimensions
LARGEUR_GRILLE = COLONNES * TAILLE_CASE
HAUTEUR_GRILLE = LIGNES * TAILLE_CASE
LARGEUR_ECRAN = LARGEUR_GRILLE + (MARGE_X * 2)
HAUTEUR_ECRAN = MARGE_Y + ESPACE_ENTETE + HAUTEUR_GRILLE + MARGE_Y
TAILLE_FENETRE = (LARGEUR_ECRAN, HAUTEUR_ECRAN)

# Couleurs
BLEU_GRILLE_MODERNE = (30, 96, 150)
COULEUR_FOND = (180, 180, 180)
NOIR = (44, 62, 80)
BLANC = (255, 255, 255)
COULEUR_BOUTON = (39, 174, 96)
COULEUR_BOUTON_HOVER = (46, 204, 113)

# Paramètres d'affichage
POLICE_TAILLE = 60
FPS = 60
VITESSE_CHUTE = 25

# --- 2. Classes pour les pays ---
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

# Liste des pays disponibles
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

# --- 3. Classes du jeu ---
class Joueur:
    def __init__(self, numero_pion, pays):
        self.numero_pion = numero_pion
        self.pays = pays
        self._drapeau_image = pays.charger_drapeau()

    def obtenir_drapeau(self):
        return self._drapeau_image

    def obtenir_message_victoire(self):
        return f"{self.pays.nom} a Gagné !!"

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
                if all(self.grille[r][c+i] == pion for i in range(4)):
                    return True
        for c in range(self.colonnes):
            for r in range(self.lignes - 3):
                if all(self.grille[r+i][c] == pion for i in range(4)):
                    return True
        for c in range(self.colonnes - 3):
            for r in range(3, self.lignes):
                if all(self.grille[r-i][c+i] == pion for i in range(4)):
                    return True
        for c in range(self.colonnes - 3):
            for r in range(self.lignes - 3):
                if all(self.grille[r+i][c+i] == pion for i in range(4)):
                    return True
        return False

class Jeu:
    def __init__(self):
        pygame.init()
        self.plateau = Plateau(LIGNES, COLONNES)
        self.pays_selectionnes = [0, 1]
        self.joueurs = [
            Joueur(1, PAYS_DISPONIBLES[self.pays_selectionnes[0]]),
            Joueur(2, PAYS_DISPONIBLES[self.pays_selectionnes[1]])
        ]

        self.ecran = pygame.display.set_mode(TAILLE_FENETRE)
        pygame.display.set_caption("Puissance 4 - Sélection de Pays")

        self.clock = pygame.time.Clock()
        self.police = pygame.font.SysFont("Arial", POLICE_TAILLE, bold=True)
        self.police_bouton = pygame.font.SysFont("Arial", 40, bold=True)

        self.etat_jeu = "MENU"
        self.jeu_termine = False
        self.tour_index = 0

        self.anim_en_cours = False
        self.anim_col = 0
        self.anim_ligne_cible = 0
        self.anim_y_actuel = 0
        self.anim_y_cible = 0

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
        titre_rect = titre_surf.get_rect(center=(LARGEUR_ECRAN/2, HAUTEUR_ECRAN/3))
        self.ecran.blit(titre_surf, titre_rect)

        mouse_pos = pygame.mouse.get_pos()
        bouton_rect = pygame.Rect(0, 0, 250, 80)
        bouton_rect.center = (LARGEUR_ECRAN/2, HAUTEUR_ECRAN/2 + 50)

        couleur_btn = COULEUR_BOUTON_HOVER if bouton_rect.collidepoint(mouse_pos) else COULEUR_BOUTON

        pygame.draw.rect(self.ecran, couleur_btn, bouton_rect, border_radius=15)
        pygame.draw.rect(self.ecran, NOIR, bouton_rect, width=3, border_radius=15)

        texte_bouton = self.police_bouton.render("JOUER", True, BLANC)
        self.ecran.blit(texte_bouton, texte_bouton.get_rect(center=bouton_rect.center))

        return bouton_rect

    def afficher_selection_pays(self):
        self.ecran.fill(COULEUR_FOND)
        titre = self.police.render("Sélectionnez les pays", True, NOIR)
        self.ecran.blit(titre, (LARGEUR_ECRAN//2 - titre.get_width()//2, 30))

        for i in range(2):
            y_pos = 150 + i * 200
            joueur_text = self.police_bouton.render(f"Joueur {i+1}:", True, NOIR)
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
        if self.etat_jeu == "MENU":
            if self.afficher_menu().collidepoint(pos):
                self.etat_jeu = "SELECTION_PAYS"
        elif self.etat_jeu == "SELECTION_PAYS":
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

    def demarrer_jeu(self):
        self.joueurs = [
            Joueur(1, PAYS_DISPONIBLES[self.pays_selectionnes[0]]),
            Joueur(2, PAYS_DISPONIBLES[self.pays_selectionnes[1]])
        ]
        self.etat_jeu = "JEU"
        self.plateau = Plateau(LIGNES, COLONNES)
        self.tour_index = 0
        self.jeu_termine = False
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

    def dessiner_plateau_et_animation(self, mouse_x=None):
        self.ecran.fill(COULEUR_FOND)
        debut_grille_y = MARGE_Y + ESPACE_ENTETE

        # 1. Dessiner les pions fixes
        for c in range(COLONNES):
            for r in range(LIGNES):
                pion_val = self.plateau.grille[r][c]
                if pion_val != 0:
                    joueur = self.joueurs[pion_val - 1]
                    drapeau = joueur.obtenir_drapeau()
                    pos_x = MARGE_X + c * TAILLE_CASE + MARGE_DRAPEAU
                    pos_y = debut_grille_y + r * TAILLE_CASE + MARGE_DRAPEAU
                    self.ecran.blit(drapeau, (pos_x, pos_y))

        # 2. Dessiner le pion qui tombe
        if self.anim_en_cours:
            joueur_anim = self.joueurs[self.tour_index]
            drapeau_anim = joueur_anim.obtenir_drapeau()
            pos_x_anim = MARGE_X + self.anim_col * TAILLE_CASE + MARGE_DRAPEAU
            pos_y_anim = int(self.anim_y_actuel) + MARGE_DRAPEAU
            self.ecran.blit(drapeau_anim, (pos_x_anim, pos_y_anim))

        # 3. Dessiner la grille par-dessus
        self.ecran.blit(self.surface_grille_bleue, (MARGE_X, debut_grille_y))

        # 4. MODIFICATION ICI : Dessiner le pion "Hover" de manière fluide
        if not self.jeu_termine and not self.anim_en_cours and mouse_x is not None:
            joueur_actuel = self.joueurs[self.tour_index]
            drapeau = joueur_actuel.obtenir_drapeau()
            
            # Position Y fixe en haut
            pos_y = MARGE_Y + ESPACE_ENTETE - TAILLE_DRAPEAU
            
            # Position X fluide : suit la souris mais reste dans les limites
            # Centrer le drapeau sur la souris
            pos_x = mouse_x - (TAILLE_DRAPEAU // 2)
            
            # Limites gauche et droite pour ne pas sortir du plateau visuellement
            limite_gauche = MARGE_X + MARGE_DRAPEAU
            limite_droite = MARGE_X + LARGEUR_GRILLE - TAILLE_DRAPEAU - MARGE_DRAPEAU
            
            # Appliquer les limites (clamp)
            if pos_x < limite_gauche:
                pos_x = limite_gauche
            elif pos_x > limite_droite:
                pos_x = limite_droite
                
            self.ecran.blit(drapeau, (pos_x, pos_y))

        # Afficher le message de victoire
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

    def boucle_principale(self):
        mouse_x = LARGEUR_ECRAN // 2

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    mouse_x = event.pos[0]

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.etat_jeu != "JEU":
                        self.gerer_clic_souris(event.pos)
                    else:
                        if not self.jeu_termine and not self.anim_en_cours:
                            # Logique : le clic détermine toujours la colonne mathématique
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