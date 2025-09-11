#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mini_imggen_numpy_lib.py
------------------------
Refactor du script `mini_imggen_numpy_ui.py` pour être une librairie Python
sans interface graphique.

Exports principaux:
- TextVocab: construction / encode / decode / save / load pour vocabulaire texte
- ARBigramText: modèle autoregressif simplifié partagé image+texte
- build_dataset, load_and_preprocess_image, image_to_tokens, tokens_to_image
- train_model / generate_image_from_model
- train_text_model / generate_text_from_model

Design notes:
- Toutes les fonctions acceptent un ``log_cb: Optional[Callable[[str], None]]``
  pour recevoir des messages de log (utile pour intégration dans une app).
- Les poids et vocabs se sauvent/chargent en NPZ/JSON compatibles avec l'ancien
  format pour la rétro-compatibilité.

Usage rapide:
>>> from mini_imggen_numpy_lib import train_model, generate_image_from_model
>>> train_model('images/', 'ckpt', epochs=3)
>>> generate_image_from_model('ckpt', 'chat tigré', 'out.png')

"""
from __future__ import annotations
import os
import re
import json
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Callable

import numpy as np
from PIL import Image

# -------------------------
# Utilitaires & tokenizers
# -------------------------

TOKEN_VOCAB_SIZE = 256  # espace de tokens 0..255 (pour images)

def set_seed(seed: int = 42) -> None:
    np.random.seed(seed)


def tokenize_text(s: str) -> List[str]:
    toks = re.split(r"[^\w]+", s.lower())
    return [t for t in toks if t]

# -------------------------
# Text vocab
# -------------------------

class TextVocab:
    """Simple vocab pour la partie texte.

    Format sur disque:
      - JSON contenant 'stoi' et 'itos'
    """
    def __init__(self):
        self.stoi: Dict[str, int] = {"<unk>": 0}
        self.itos: List[str] = ["<unk>"]

    def build(self, words: List[str], min_freq: int = 1) -> None:
        from collections import Counter
        c = Counter(words)
        for w, f in c.items():
            if f >= min_freq and w not in self.stoi:
                self.stoi[w] = len(self.itos)
                self.itos.append(w)

    def encode(self, words: List[str]) -> List[int]:
        return [self.stoi.get(w, 0) for w in words]

    def decode(self, ids: List[int]) -> List[str]:
        return [self.itos[i] if 0 <= i < len(self.itos) else "<unk>" for i in ids]

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"stoi": self.stoi, "itos": self.itos}, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(path: str) -> 'TextVocab':
        with open(path, 'r', encoding='utf-8') as f:
            d = json.load(f)
        tv = TextVocab()
        tv.stoi = {k: int(v) for k, v in d["stoi"].items()}
        tv.itos = list(d["itos"])
        return tv

# -------------------------
# Chargement / prétraitement image
# -------------------------


def load_and_preprocess_image(path: str, size: int = 32) -> np.ndarray:
    img = Image.open(path).convert('RGB')
    img = img.resize((size, size), Image.BICUBIC)
    arr = np.array(img, dtype=np.uint8)
    return arr


def image_to_tokens(img_arr: np.ndarray) -> np.ndarray:
    # aplatissement des canaux -> tokens 0..255
    return img_arr.flatten()


def tokens_to_image(tokens: np.ndarray, size: int = 32) -> np.ndarray:
    return tokens.reshape(size, size, 3)

# -------------------------
# Config & modèle AR simplifié (texte+image)
# -------------------------

@dataclass
class Config:
    d_model: int = 64
    hidden: int = 128


class ARBigramText:
    """Modèle autoregressif minimal partagé pour image+texte.

    Remarque: modèle toy — utile pour expérimentations pédagogiques et
    génération naïve conditionnée sur texte.
    """
    def __init__(self, vocab_size_text: int, cfg: Config):
        self.cfg = cfg
        d = cfg.d_model
        h = cfg.hidden
        self.E_tok = 0.02 * np.random.randn(TOKEN_VOCAB_SIZE, d).astype(np.float32)
        self.E_txt = 0.02 * np.random.randn(vocab_size_text, d).astype(np.float32)
        self.W1 = 0.02 * np.random.randn(2 * d, h).astype(np.float32)
        self.b1 = np.zeros((h,), dtype=np.float32)
        self.W2 = 0.02 * np.random.randn(h, TOKEN_VOCAB_SIZE).astype(np.float32)
        self.b2 = np.zeros((TOKEN_VOCAB_SIZE,), dtype=np.float32)
        self.zero_grads()

    def zero_grads(self) -> None:
        self.gE_tok = np.zeros_like(self.E_tok)
        self.gE_txt = np.zeros_like(self.E_txt)
        self.gW1 = np.zeros_like(self.W1)
        self.gb1 = np.zeros_like(self.b1)
        self.gW2 = np.zeros_like(self.W2)
        self.gb2 = np.zeros_like(self.b2)

    @staticmethod
    def relu(x):
        return np.maximum(0, x)

    @staticmethod
    def softmax(x):
        x = x - x.max(axis=1, keepdims=True)
        ex = np.exp(x)
        return ex / ex.sum(axis=1, keepdims=True)

    def text_embed(self, text_ids: np.ndarray) -> np.ndarray:
        if text_ids is None or text_ids.size == 0:
            return np.zeros((1, self.cfg.d_model), dtype=np.float32)
        emb = self.E_txt[text_ids]
        return emb.mean(axis=0, keepdims=True)

    def forward(self, prev_tokens: np.ndarray, text_ids: np.ndarray) -> Tuple[np.ndarray, dict]:
        N = prev_tokens.shape[0]
        emb_prev = self.E_tok[prev_tokens]
        emb_text = np.repeat(self.text_embed(text_ids), N, axis=0)
        x = np.concatenate([emb_prev, emb_text], axis=1)
        hpre = x @ self.W1 + self.b1
        h = self.relu(hpre)
        logits = h @ self.W2 + self.b2
        cache = {'x': x, 'hpre': hpre, 'h': h, 'emb_prev_idx': prev_tokens, 'emb_text_ids': text_ids}
        return logits, cache

    def loss_and_grads(self, prev_tokens: np.ndarray, targets: np.ndarray, text_ids: np.ndarray) -> Tuple[float, np.ndarray]:
        logits, cache = self.forward(prev_tokens, text_ids)
        probs = self.softmax(logits)
        N = targets.size
        loss = -np.log(probs[np.arange(N), targets] + 1e-12).mean()
        dlogits = probs
        dlogits[np.arange(N), targets] -= 1
        dlogits /= N
        self.gW2 += cache['h'].T @ dlogits
        self.gb2 += dlogits.sum(axis=0)
        dh = dlogits @ self.W2.T
        dhpre = dh * (cache['hpre'] > 0)
        self.gW1 += cache['x'].T @ dhpre
        self.gb1 += dhpre.sum(axis=0)
        dx = dhpre @ self.W1.T
        d_emb_prev = dx[:, :self.cfg.d_model]
        d_emb_text = dx[:, self.cfg.d_model:]
        np.add.at(self.gE_tok, cache['emb_prev_idx'], d_emb_prev)
        text_ids_arr = cache['emb_text_ids']
        if text_ids_arr is not None and text_ids_arr.size > 0:
            d_text_mean = d_emb_text.mean(axis=0, keepdims=True)
            for idx in text_ids_arr:
                self.gE_txt[idx] += d_text_mean[0]
        return loss, probs

    def sgd_step(self, lr: float = 1e-2) -> None:
        for p, g in [
            (self.E_tok, self.gE_tok), (self.E_txt, self.gE_txt),
            (self.W1, self.gW1), (self.b1, self.gb1),
            (self.W2, self.gW2), (self.b2, self.gb2)
        ]:
            p -= lr * g
        self.zero_grads()

    def predict_next(self, prev_token: int, text_ids: np.ndarray, temperature: float = 1.0) -> int:
        logits, _ = self.forward(np.array([prev_token], dtype=np.int32), text_ids)
        logits = logits / max(1e-6, temperature)
        probs = self.softmax(logits)[0]
        return int(np.random.choice(TOKEN_VOCAB_SIZE, p=probs))

    def init_token_from_text(self, text_ids: np.ndarray) -> int:
        d = self.cfg.d_model
        emb_text = self.text_embed(text_ids)
        x0 = np.concatenate([np.zeros((1, d), dtype=np.float32), emb_text], axis=1)
        h0 = self.relu(x0 @ self.W1 + self.b1)
        logits0 = h0 @ self.W2 + self.b2
        probs0 = self.softmax(logits0)[0]
        return int(np.argmax(probs0))

    def generate(self, text_ids: np.ndarray, length: int, mode: str = "quick",
                 prefix: Optional[List[int]] = None, temperature: float = 1.0) -> np.ndarray:
        seq: List[int] = []
        if prefix and len(prefix) > 0:
            seq.extend(prefix)
        else:
            if mode == "quick":
                seq.append(self.init_token_from_text(text_ids))
            else:
                seq.append(0)
        while len(seq) < length:
            nxt = self.predict_next(seq[-1], text_ids, temperature=temperature)
            seq.append(nxt)
        return np.array(seq, dtype=np.uint8)

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        np.savez_compressed(path,
                            E_tok=self.E_tok, E_txt=self.E_txt,
                            W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2,
                            d_model=self.cfg.d_model, hidden=self.cfg.hidden)

    @staticmethod
    def load(path: str) -> 'ARBigramText':
        d = np.load(path)
        cfg = Config(int(d['d_model']), int(d['hidden']))
        model = ARBigramText(vocab_size_text=d['E_txt'].shape[0], cfg=cfg)
        model.E_tok = d['E_tok']
        model.E_txt = d['E_txt']
        model.W1 = d['W1']
        model.b1 = d['b1']
        model.W2 = d['W2']
        model.b2 = d['b2']
        model.zero_grads()
        return model

# -------------------------
# Dataset images helpers
# -------------------------


def build_dataset(data_dir: str, size: int = 32) -> Tuple[List[np.ndarray], List[List[str]]]:
    imgs = []
    texts = []
    for fname in os.listdir(data_dir):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            continue
        path = os.path.join(data_dir, fname)
        try:
            arr = load_and_preprocess_image(path, size=size)
        except Exception:
            continue
        toks = image_to_tokens(arr)
        imgs.append(toks)
        name = os.path.splitext(fname)[0]
        words = tokenize_text(name)
        texts.append(words)
    return imgs, texts


def make_batches(img_tokens: List[np.ndarray], text_ids_list: List[np.ndarray], batch_size: int = 16):
    n = len(img_tokens)
    if n == 0:
        raise RuntimeError("Aucun exemple dans make_batches")
    while True:
        idxs = np.random.choice(n, size=batch_size)
        prev_list = []
        targ_list = []
        txt_ids_sample = None
        for i in idxs:
            seq = img_tokens[i]
            if seq.size < 2:
                continue
            pos = np.random.randint(1, seq.size)
            prev_list.append(seq[pos-1])
            targ_list.append(seq[pos])
            txt_ids_sample = text_ids_list[i]
        if not prev_list:
            continue
        prev = np.array(prev_list, dtype=np.int32)
        targ = np.array(targ_list, dtype=np.int32)
        yield prev, targ, txt_ids_sample

# -------------------------
# Entraînement / génération image
# -------------------------


def train_model(data_dir: str, out_dir: str, size: int = 32, d_model: int = 64, hidden: int = 128,
                batch_size: int = 32, epochs: int = 3, lr: float = 0.02, seed: int = 42,
                log_cb: Optional[Callable[[str], None]] = None) -> Tuple[str, str]:
    set_seed(seed)
    imgs, texts = build_dataset(data_dir, size=size)
    if not imgs:
        raise RuntimeError("Aucune image trouvée dans le dossier sélectionné.")
    vocab = TextVocab()
    vocab.build([w for doc in texts for w in doc], min_freq=1)
    text_ids_list = [np.array(vocab.encode(doc), dtype=np.int32) for doc in texts]
    model = ARBigramText(vocab_size_text=len(vocab.itos), cfg=Config(d_model=d_model, hidden=hidden))
    batches = make_batches(imgs, text_ids_list, batch_size=batch_size)
    steps_per_epoch = max(100, len(imgs))
    if log_cb:
        log_cb(f"[IMG] Dataset: {len(imgs)} images | Vocab texte: {len(vocab.itos)}")
    for epoch in range(1, epochs + 1):
        running = 0.0
        for step in range(steps_per_epoch):
            prev, targ, txt_ids = next(batches)
            loss, _ = model.loss_and_grads(prev, targ, txt_ids)
            model.sgd_step(lr=lr)
            running += loss
            if (step+1) % 50 == 0 and log_cb:
                log_cb(f"[IMG] Epoch {epoch} step {step+1}/{steps_per_epoch} avg_loss={(running/(step+1)):.4f}")
        if log_cb:
            log_cb(f"[IMG] Epoch {epoch}: loss={(running/steps_per_epoch):.4f}")
    os.makedirs(out_dir, exist_ok=True)
    model_path = os.path.join(out_dir, 'model_weights.npz')
    vocab_path = os.path.join(out_dir, 'vocab.json')
    model.save(model_path)
    vocab.save(vocab_path)
    if log_cb:
        log_cb(f"[IMG] Sauvé: {model_path}\n[IMG] Sauvé: {vocab_path}")
    return model_path, vocab_path


def generate_image_from_model(model_dir: str, prompt: str, out_path: str, size: int = 32, mode: str = 'quick',
                              prefix_path: Optional[str] = None, prefix_ratio: float = 0.1, temperature: float = 1.0) -> str:
    vocab = TextVocab.load(os.path.join(model_dir, 'vocab.json'))
    model = ARBigramText.load(os.path.join(model_dir, 'model_weights.npz'))
    words_all = tokenize_text(prompt)
    words_known = [w for w in words_all if w in vocab.stoi]
    if not words_known:
        words_known = ["<unk>"]
    text_ids = np.array(vocab.encode(words_known), dtype=np.int32)
    length = size * size
    prefix = None
    if prefix_path:
        arr = load_and_preprocess_image(prefix_path, size=size)
        toks = image_to_tokens(arr)
        k = max(1, int(len(toks) * prefix_ratio))
        prefix = toks[:k].tolist()
    seq = model.generate(text_ids, length=length, mode=mode, prefix=prefix, temperature=temperature)
    seq = np.array(seq, dtype=np.uint8)
    side = int(np.sqrt(len(seq)))
    img_flat = seq[:side * side].reshape((side, side))
    img_rgb = np.stack((img_flat,)*3, axis=-1).astype(np.uint8)
    Image.fromarray(img_rgb, mode='RGB').save(out_path)
    return out_path

# -------------------------
# Générateur texte
# -------------------------


def load_text_dataset(json_path: str) -> List[List[str]]:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    texts = data.get('texts', [])
    return [tokenize_text(s) for s in texts if isinstance(s, str) and s.strip()]


def make_text_batches(seqs: List[List[int]], batch_size: int = 16):
    data = [np.array(s, dtype=np.int32) for s in seqs if len(s) > 1]
    if not data:
        raise RuntimeError("Dataset texte trop petit ou mal formaté.")
    while True:
        prev, targ = [], []
        for _ in range(batch_size):
            seq = data[np.random.randint(len(data))]
            pos = np.random.randint(1, len(seq))
            prev.append(seq[pos-1])
            targ.append(seq[pos])
        yield np.array(prev, dtype=np.int32), np.array(targ, dtype=np.int32)


def train_text_model(dataset_json: str, out_dir: str, d_model: int = 64, hidden: int = 128,
                     batch_size: int = 32, epochs: int = 3, lr: float = 0.02,
                     log_cb: Optional[Callable[[str], None]] = None) -> Tuple[str, str]:
    texts = load_text_dataset(dataset_json)
    if not texts:
        raise RuntimeError("Aucun texte trouvé dans le JSON.")
    vocab = TextVocab()
    vocab.build([w for doc in texts for w in doc], min_freq=1)
    seqs = [vocab.encode(doc) for doc in texts]
    model = ARBigramText(vocab_size_text=len(vocab.itos), cfg=Config(d_model=d_model, hidden=hidden))
    batches = make_text_batches(seqs, batch_size=batch_size)
    steps_per_epoch = max(100, len(seqs))
    if log_cb:
        log_cb(f"[TEXT] Dataset: {len(seqs)} phrases | Vocab: {len(vocab.itos)} mots")
    for epoch in range(1, epochs+1):
        running = 0.0
        for step in range(steps_per_epoch):
            prev, targ = next(batches)
            loss, _ = model.loss_and_grads(prev, targ, np.array([], dtype=np.int32))
            model.sgd_step(lr=lr)
            running += loss
            if (step+1) % 100 == 0 and log_cb:
                log_cb(f"[TEXT] Epoch {epoch} step {step+1}/{steps_per_epoch} avg_loss={(running/(step+1)):.4f}")
        if log_cb:
            log_cb(f"[TEXT] Epoch {epoch}: loss={(running/steps_per_epoch):.4f}")
    os.makedirs(out_dir, exist_ok=True)
    model_path = os.path.join(out_dir, 'text_model.npz')
    vocab_path = os.path.join(out_dir, 'text_vocab.json')
    model.save(model_path)
    vocab.save(vocab_path)
    if log_cb:
        log_cb(f"[TEXT] Sauvé: {model_path}\n[TEXT] Sauvé: {vocab_path}")
    return model_path, vocab_path


def generate_text_from_model(model_dir: str, prompt: str, length: int = 30, temperature: float = 1.0) -> str:
    vocab = TextVocab.load(os.path.join(model_dir, 'text_vocab.json'))
    model = ARBigramText.load(os.path.join(model_dir, 'text_model.npz'))
    words = tokenize_text(prompt)
    if not words:
        words = ["<unk>"]
    ids = vocab.encode(words)
    start_id = ids[-1] if ids else 0
    seq = model.generate(np.array([start_id], dtype=np.int32), length=length, mode="quick", prefix=None, temperature=temperature)
    mapped_ids = [int(tok) % len(vocab.itos) for tok in seq.tolist()]
    return " ".join(vocab.decode(mapped_ids))

# -------------------------
# Exports
# -------------------------

__all__ = [
    'TOKEN_VOCAB_SIZE', 'set_seed', 'tokenize_text',
    'TextVocab', 'load_and_preprocess_image', 'image_to_tokens', 'tokens_to_image',
    'ARBigramText', 'Config', 'build_dataset', 'train_model', 'generate_image_from_model',
    'load_text_dataset', 'train_text_model', 'generate_text_from_model'
]

# -------------------------
# Exemple d'utilisation (commenté)
# -------------------------

if __name__ == '__main__':
    print('mini_imggen_numpy_lib: importez la librairie et appelez les fonctions depuis votre application.')
