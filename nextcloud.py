"""
Connexion à Nextcloud (ici Nuage Relief) via un lien de partage PUBLIC (dossier partagé).

Nextcloud expose chaque partage public via WebDAV à l'URL :
    https://<nextcloud-host>/public.php/webdav/

en utilisant le TOKEN du lien de partage comme identifiant (mot de passe vide,
ou mot de passe du partage si protégé).

Un lien de partage ressemble à :
    https://cloud.example.com/s/AbCdEfGhIjKlMnO

-> host  = cloud.example.com
-> token = AbCdEfGhIjKlMnO
"""

import re
from urllib.parse import urlparse
import requests

WEBDAV_NS = {"d": "DAV:"}
# Liste à mettre à jour si de nouveaux matériaux sont ajoutés dans le partage Nextcloud


def parse_share_url(share_url: str):
    """Extrait (host, token) d'une URL de partage Nextcloud, ex: https://cloud.x.com/s/TOKEN"""
    parsed = urlparse(share_url.strip())
    host = f"{parsed.scheme}://{parsed.netloc}"
    match = re.search(r"/s/([^/?]+)", parsed.path)
    if not match:
        raise ValueError(
            "URL de partage invalide : token introuvable (attendu .../s/<token>)"
        )
    token = match.group(1)
    return host, token


def _webdav_url(host: str, path: str = "") -> str:
    path = path.strip("/")
    base = f"{host}/public.php/webdav"
    return f"{base}/{path}" if path else base


def download_file(share_url: str, path: str, password: str = "") -> bytes:
    """Télécharge un fichier via WebDAV (path relatif au partage) et retourne son contenu binaire."""
    host, token = parse_share_url(share_url)
    url = _webdav_url(host, path)
    resp = requests.get(url, auth=(token, password or ""), timeout=60)
    resp.raise_for_status()
    return resp.content
