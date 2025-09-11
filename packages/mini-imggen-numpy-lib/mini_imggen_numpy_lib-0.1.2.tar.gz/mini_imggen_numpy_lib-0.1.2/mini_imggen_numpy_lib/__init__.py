# mini_imggen_numpy_lib/__init__.py

"""
mini_imggen_numpy_lib
--------------------
Librairie Python pour génération d'images et texte avec Numpy, sans interface graphique.

Exports principaux:
- TextVocab
- ARBigramText, Config
- Fonctions images: build_dataset, load_and_preprocess_image, image_to_tokens, tokens_to_image, train_model, generate_image_from_model
- Fonctions texte: load_text_dataset, train_text_model, generate_text_from_model
"""

# Import des utilitaires et classes depuis le module principal
from .mini_imggen_numpy_lib import (
    TOKEN_VOCAB_SIZE,
    set_seed,
    tokenize_text,
    TextVocab,
    load_and_preprocess_image,
    image_to_tokens,
    tokens_to_image,
    ARBigramText,
    Config,
    build_dataset,
    train_model,
    generate_image_from_model,
    load_text_dataset,
    train_text_model,
    generate_text_from_model
)

# Définition des symboles exportés pour l'import *
__all__ = [
    'TOKEN_VOCAB_SIZE', 'set_seed', 'tokenize_text',
    'TextVocab', 'load_and_preprocess_image', 'image_to_tokens', 'tokens_to_image',
    'ARBigramText', 'Config', 'build_dataset', 'train_model', 'generate_image_from_model',
    'load_text_dataset', 'train_text_model', 'generate_text_from_model'
]