# Puissance 4 - Projet Python
## Le meilleure puissance 4 ever avec une multitude de drapeaux #nofitna




Puissance 4 - Édition CyTech 🚀
Bienvenue dans le jeu de Puissance 4 personnalisé avec sélection de drapeaux nationaux et votre logo CyTech !

Ce jeu est développé en Python avec la bibliothèque pygame.

📥 1. Prérequis
Pour exécuter ce jeu, vous devez avoir Python installé sur votre machine, ainsi que la bibliothèque pygame.

Installation de Pygame (si nécessaire)
Ouvrez votre console ou votre terminal et exécutez la commande suivante :

Bash

pip install pygame
📦 2. Structure des Fichiers
Pour que le jeu fonctionne correctement, tous les fichiers image (drapeaux et logo) doivent se trouver dans le même dossier que le fichier Python (.py) du jeu.

Votre dossier doit contenir :

jeu_puissance4.py (ou le nom de votre fichier Python)

CyTech.png (votre logo)

Tous les fichiers de drapeaux (drapeau_algérie.png, drapeau_maroc.png, etc.)

🕹️ 3. Comment Jouer (Exécution)
La méthode la plus fiable pour garantir que Pygame trouve toutes les images est d'exécuter le jeu directement depuis le répertoire où se trouvent tous les fichiers.

💻 Méthode recommandée (Via le Terminal / VS Code)
Ouvrez votre Terminal ou la console intégrée dans VS Code (Terminal > New Terminal).

Naviguez jusqu'au répertoire du projet en utilisant la commande cd (Change Directory).

Exemple si votre dossier est sur le Bureau :

Bash

cd ~/Desktop/MonDossierDeJeu
Lancez le jeu en utilisant Python :

Bash


# ⚠️ Note pour VS Code : 
Si vous lancez le fichier en utilisant le bouton "Run" ou le triangle vert, il se peut que le répertoire de travail actuel ne soit pas le bon, et que les images ne s'affichent pas (seules les cases colorées de secours apparaitront). L'exécution via la console (Terminal) comme décrit ci-dessus contourne ce problème et assure le bon chargement des ressources.

🖱️ Jeu et Fonctionnalités
Menu Démarrage : Cliquez sur JOUER pour accéder à la sélection des pays.

Sélection des Pays : Utilisez les flèches > et < pour choisir les drapeaux des deux joueurs. Cliquez sur Démarrer.

Pion Flottant : Le pion en haut de la grille suit la souris de manière fluide (sans sauter entre les colonnes) avant d'être déposé.

Déposer un Pion : Cliquez dans la colonne souhaitée pour faire tomber le pion.

🛠️ 4. Personnalisation
Ajouter des Pays : Vous pouvez ajouter d'autres pays en mettant leurs fichiers PNG dans le dossier du projet et en les listant dans la variable PAYS_DISPONIBLES du code.

Changer le Logo : Remplacez simplement CyTech.png par votre propre fichier image, en veillant à conserver le même nom (CyTech.png) ou à mettre à jour le nom dans le constructeur __init__ de la classe Jeu.
