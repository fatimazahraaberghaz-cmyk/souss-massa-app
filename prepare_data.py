"""
prepare_data.py
───────────────
Télécharge les couches administratives du Maroc (GADM 4.1)
et les sauvegarde dans le dossier data/ au format Shapefile.

Usage :
    python prepare_data.py

Nécessite : requests, geopandas, fiona
"""

import os
import requests
import geopandas as gpd
import json

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

GADM_URLS = {
    "regions":   "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_MAR_1.json",
    "provinces": "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_MAR_2.json",
    "communes":  "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_MAR_3.json",
}

def download_and_save(key, url):
    out_path = os.path.join(DATA_DIR, f"{key}.shp")
    if os.path.exists(out_path):
        print(f"  ✓ {key}.shp déjà présent — skip")
        return

    print(f"  ⬇  Téléchargement {key} …", end=" ", flush=True)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    print(f"OK ({len(resp.content)//1024} ko)")

    gdf = gpd.GeoDataFrame.from_features(resp.json()["features"], crs="EPSG:4326")
    gdf.to_file(out_path)
    print(f"  💾 Sauvegardé : {out_path}  ({len(gdf)} entités)")

if __name__ == "__main__":
    print("\n═══════════════════════════════════════")
    print("  Préparation des données administratives du Maroc")
    print("  Source : GADM 4.1 — https://gadm.org")
    print("═══════════════════════════════════════\n")

    for key, url in GADM_URLS.items():
        try:
            download_and_save(key, url)
        except Exception as e:
            print(f"  ✗ Erreur pour {key} : {e}")

    print("\n✅ Données prêtes dans le dossier data/\n")
