# PetalPDF 🌸

PetalPDF est un assistant interactif puissant en ligne de commande (CLI) pour aspirer et télécharger automatiquement tous les fichiers PDF d'une page web ou d'un site entier. Doté d'une interface magnifique (ASCII art, couleurs, animations) et bilingue (Français/Anglais), il intègre des fonctionnalités de crawling professionnelles.

![Bannière](https://img.shields.io/badge/Python-3.6%2B-blue)
![Licence](https://img.shields.io/badge/License-MIT-green)

## Fonctionnalités ✨

- **Mode Assistant (Wizard)** : Plus besoin de retenir des lignes de commande complexes, le programme vous pose des questions claires.
- **Crawling de Site (Bot)** : PetalPDF peut se contenter d'une seule page, ou agir comme un robot en explorant toutes les pages liées du site pour y débusquer les PDF cachés (par blocs de 100 pages).
- **Mode Turbo (Multithreading) 🚀** : Téléchargez jusqu'à 10 fichiers simultanément pour diviser le temps de traitement par 10.
- **Renommage Intelligent 🧠** : PetalPDF lit de manière transparente les métadonnées internes du fichier PDF et le renomme proprement (nécessite la librairie `pypdf`). Fini les `doc_182A.pdf` illisibles !
- **Gestion des Sites Privés / Intranet 🔑** : Ajoutez vos "Cookies de session" pour télécharger des PDF cachés derrière un espace membre protégé par un mot de passe.
- **Filtres Avancés** :
  - **Taille** : Ignorez les fichiers trop lourds en fixant une limite en Mo.
  - **Mots-clés** : Ne téléchargez que les PDF dont le lien contient des mots spécifiques.
  - **Scan intelligent** : Le crawler ignore d'office les extensions inutiles (`.jpg`, `.mp4`, `.css`) pour gagner un temps précieux.
- **Système de Reprise (Anti-crash) 💾** : Vous avez appuyé sur `Ctrl+C` par erreur ou eu une coupure ? Pas de panique, PetalPDF sauvegarde l'état en temps réel et vous proposera de reprendre là où vous vous étiez arrêté.
- **Bilingue et Esthétique** : Support complet FR/EN, animations fluides, interface chaleureuse rose pétale.

## Installation 🛠️

1. Clonez ce dépôt GitHub sur votre machine :
   ```bash
   git clone https://github.com/ecarlatee/PetalPDF.git
   cd PetalPDF
   ```

2. Installez les librairies requises (via `pip`) :
   ```bash
   pip install -r requirements.txt
   ```
   *Note : Le fichier requirements installe `requests`, `beautifulsoup4` (pour le scan) et `pypdf` (pour le renommage intelligent).*

## Utilisation 🚀

Lancez simplement le script avec Python :
```bash
python petalpdf.py
```

Laissez-vous guider par l'interface ! PetalPDF vous demandera :
1. La langue (fr ou en).
2. L'URL de la page web source.
3. Le niveau d'exploration (page unique, tout le site, ou options avancées Pro).
4. Le nom du dossier dans lequel sauvegarder les PDF trouvés.

En fin de processus, s'il y a eu des coupures de serveurs, PetalPDF listera les échecs et vous proposera de les **réessayer automatiquement**.

## Avertissement
Assurez-vous de posséder les droits nécessaires (droit d'auteur, CGU du site) pour télécharger les fichiers sur les sites ciblés. L'utilisation d'outils automatisés peut être soumise à réglementation selon les hébergeurs.
