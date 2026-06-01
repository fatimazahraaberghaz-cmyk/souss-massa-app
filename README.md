# 🌊 Souss-Massa · Dashboard Géospatial

> Application web géospatiale interactive pour la visualisation des prévisions météorologiques et du territoire de la région **Souss-Massa** (Maroc).  
> Développée dans le cadre du cours **GIS Programming 2025-2026** — EHTP.

---

## 🚀 Application déployée

🔗 **[Accéder à l'application →](https://souss-massa-app-cspyu3qpxs65wtom7ig2gu.streamlit.app)**  
*(Remplacer ce lien par l'URL Streamlit Cloud après déploiement)*

---

## 📋 Fonctionnalités

### 🗂️ Module de navigation administrative
- Sélection hiérarchique : **Région → Province → Commune**
- Filtrage spatial automatique par jointure géographique (GeoPandas `sjoin`)
- L'entité sélectionnée devient l'unité de référence pour tous les autres modules

### 🗺️ Module de visualisation cartographique
- Carte interactive **Folium** avec :
  - Fond de plan **OpenStreetMap**
  - **MNT OpenTopoMap** (tiles XYZ, SRTM 30m)
  - **WMS Terrestris SRTM** (Hillshade)
  - Contour stylisé de l'entité sélectionnée
  - Légende, titre et contrôle des couches
- Recadrage automatique sur l'emprise de l'entité

### 🌡️ Module de données climatiques prévisionnelles
- **API Open-Meteo** (gratuite, sans clé, 15 jours de prévision)
- Paramètres : **Température à 2m** (T_min / T_mean / T_max) et **Précipitations cumulées**
- Centroïde de l'entité utilisé pour la requête API

### 📈 Module de visualisation temporelle
- Courbe interactive (Plotly) pour la **température** (min / moy / max)
- Histogramme interactif pour les **précipitations**
- Tooltip au survol, axes labellisés (°C / mm)
- Tableau détaillé exportable

---

## 🗃️ Sources de données

| Donnée | Source | Format |
|--------|--------|--------|
| Découpage administratif Maroc | [GADM 4.1](https://gadm.org) | GeoJSON → Shapefile |
| MNT / Relief | [OpenTopoMap](https://opentopomap.org) + [Terrestris SRTM WMS](https://ows.terrestris.de) | Tiles XYZ / WMS |
| Prévisions météo | [Open-Meteo API](https://open-meteo.com) | JSON (REST) |
| Fond de plan | [OpenStreetMap](https://www.openstreetmap.org) | Tiles |

---

## 🛠️ Technologies utilisées

| Catégorie | Bibliothèque | Rôle |
|-----------|-------------|------|
| Interface web | `streamlit` | Application interactive |
| Traitement vecteur | `geopandas` | Shapefiles, filtrage spatial |
| Traitement raster | `rasterio` | Lecture GeoTIFF / extraction |
| Cartographie | `folium` + `streamlit-folium` | Carte interactive WMS/XYZ |
| Visualisation | `plotly` | Graphiques temporels |
| HTTP | `requests` | Appels API |
| Déploiement | **Streamlit Cloud** + **GitHub** | Hébergement public |

---

## 📁 Structure du projet

```
souss_massa_app/
│
├── app.py                  # Application principale Streamlit
├── prepare_data.py         # Script de téléchargement des shapefiles GADM
├── requirements.txt        # Dépendances Python
├── README.md               # Ce fichier
│
├── data/                   # Couches administratives (Shapefiles)
│   ├── regions.shp         # 12 régions du Maroc
│   ├── provinces.shp       # Provinces
│   └── communes.shp        # Communes
│
└── .streamlit/
    └── config.toml         # Thème et configuration Streamlit
```

---

## ⚙️ Installation locale

### 1. Cloner le dépôt
```bash
git clone https://github.com/votre-username/souss-massa-app.git
cd souss-massa-app
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Télécharger les données administratives
```bash
python prepare_data.py
```
> Ce script télécharge les couches GADM 4.1 (régions, provinces, communes du Maroc) et les sauvegarde dans `data/`.  
> Si vos propres shapefiles sont disponibles, copiez-les dans `data/` avec les noms : `regions.shp`, `provinces.shp`, `communes.shp`.

### 5. Lancer l'application
```bash
streamlit run app.py
```
Accéder à `http://localhost:8501`

---

## ☁️ Déploiement sur Streamlit Cloud

1. Pousser le projet sur un **dépôt GitHub public**
2. Aller sur [share.streamlit.io](https://share.streamlit.io)
3. Sélectionner le dépôt, la branche `main` et le fichier `app.py`
4. Cliquer sur **Deploy**
5. Renseigner l'URL générée dans ce README et dans `appli1_Nom-binome.txt`

> **Note** : Le script `prepare_data.py` doit être exécuté localement avant de pousser les données dans `data/`.  
> Les shapefiles doivent être inclus dans le dépôt GitHub (dossier `data/`).

---

## 👨‍💻 Auteurs

- **[Votre Nom]** — EHTP, GIS Programming 2025-2026

---

## 📄 Licence

Projet académique — EHTP 2025-2026.  
Données GADM : [licence GADM](https://gadm.org/license.html) — usage non-commercial.  
Données météo : Open-Meteo — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
