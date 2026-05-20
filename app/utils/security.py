"""Helpers de sécurité : hashage IP, validation light, etc.

Toutes les fonctions ici sont déterministes et sans état (pas d'appel BDD).
Elles peuvent être appelées depuis n'importe quel layer (route, service, test).
"""

from __future__ import annotations

import hashlib


def hash_ip(ip: str | None) -> str | None:
    """Hash une IP en SHA-256 pour stockage RGPD-friendly.

    Pourquoi hasher ?
    - On garde la possibilité de détecter du spam (même IP qui inscrit 50 emails)
    - Sans stocker l'IP en clair (qui est une donnée personnelle au sens RGPD).
    - Le hash est déterministe : même IP → même hash, donc on peut grouper.

    Args:
        ip: Adresse IP source (v4 ou v6). Peut être None si pas dispo.

    Returns:
        Hash hex 64 chars, ou None si l'IP est vide/None.

    Example:
        >>> hash_ip("192.168.1.1")
        '4b1f6e3e...'
        >>> hash_ip(None)
        None
    """
    # Cas limite : pas d'IP dispo (proxy mal configuré, test, etc.)
    if not ip:
        return None

    # SHA-256 → 256 bits → 64 caractères hex en sortie
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()
