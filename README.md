# MyWiki

Ce dépôt contient divers fichiers permettant de valoriser les _dumps_ de Wikipédia disponibles à ce [lien](https://dumps.wikimedia.org/).

## Possibilités
Il y a des fonctions permettant 

- de récupérer tous les titres d'articles d'un fichier `.xml`
- de transformer le `.xml` en une base Sqlite
- d'afficher le tout avec un interface `tkinter` simple


## Contenu
- un notebook `MyWiki.ipynb` contenant un guide pour créer sa propre _GUI_ affichant les contenus textes de wikipédia (utilisation du galicien dans notre cas mais cela peut-être changé)
- un dossier `src` avec un script bash pour récupérer les dumps et les transformer en fichier texte
- dossier `docs` contenant le rapport rendu en cours (format `.pdf` et `.qmd`), on y trouve des informations sur l'infrastructure Wikipédia et une présentation sur la mise en pratique.
- les dossiers `output_csv`, `dumps`, `DB` et `text` qui sont vides mais sont nécessaires pour l'arborescence, ils doivent recevoir les dumps téléchargés depuis le site de Wikipédia, les outputs en csv et les textes (de WikiExtractor)
- le dossier `img` avec des images de la _GUI_ et des images utilisées dans le rapport de `docs` pour le rendu du `.qmd`
- ce `README.md` présentant succintement le rapport


## Requirements
- Python 3.9+ avec `pandas`, `tkinter`et `sqlite3`installés
- Bash (système Unix) avec `curl` installé
- `Wikipedia.Extractor` (installable via pip)
