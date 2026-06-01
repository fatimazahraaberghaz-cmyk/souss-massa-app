"""
Application Géospatiale Web - Région Souss-Massa
GIS Programming 2025-2026
Développée avec GeoPandas, Rasterio, Folium & Streamlit
"""

import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import numpy as np

# ─────────────────────────────────────────────
# Configuration de la page
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Souss-Massa · Météo & Territoire",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS personnalisé
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0a2342 0%, #1a3a5c 60%, #0d4f6e 100%);
    color: #e8f4f8;
  }
  section[data-testid="stSidebar"] * { color: #e8f4f8 !important; }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stRadio label { color: #a8d8ea !important; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; }
  section[data-testid="stSidebar"] select,
  section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(168,216,234,0.3) !important;
    border-radius: 8px !important;
    color: #fff !important;
  }

  /* Header Banner */
  .hero-banner {
    background: linear-gradient(135deg, #0a2342 0%, #1a5276 50%, #117a65 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    box-shadow: 0 8px 32px rgba(10,35,66,0.3);
  }
  .hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #fff;
    margin: 0;
    line-height: 1.2;
  }
  .hero-sub {
    color: #a8d8ea;
    font-size: 0.9rem;
    margin-top: 0.3rem;
    font-weight: 300;
  }

  /* Metric cards */
  .metric-card {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border-left: 4px solid #0369a1;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 8px rgba(3,105,161,0.1);
  }
  .metric-card .value { font-size: 1.6rem; font-weight: 500; color: #0c4a6e; }
  .metric-card .label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: #0369a1; }

  /* Section titles */
  .section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: #0a2342;
    border-bottom: 2px solid #0369a1;
    padding-bottom: 0.4rem;
    margin: 1.2rem 0 0.8rem;
  }

  /* Info box */
  .info-box {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #0c4a6e;
  }

  /* Footer */
  .footer { text-align: center; color: #94a3b8; font-size: 0.75rem; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Chargement des données administratives
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Chargement des données administratives…")
def load_admin_data():
    """
    Charge les shapefiles administratifs.
    Priorité : data/ local → fallback GeoJSON GitHub OCHA/GADM.
    """
    paths = {
        "regions":   "data/regions.shp",
        "provinces": "data/provinces.shp",
        "communes":  "data/communes.shp",
    }

    gdfs = {}
    for key, path in paths.items():
        if os.path.exists(path):
            gdfs[key] = gpd.read_file(path)
        else:
            gdfs[key] = None

    # ── Fallback : GeoJSON public GADM niveau 1/2 pour le Maroc ──────────
    # (utilisé uniquement si les shapefiles locaux sont absents)
    if gdfs["regions"] is None:
        try:
            url_r = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
            # Utiliser GADM simplifié
            url_gadm1 = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_MAR_1.json"
            url_gadm2 = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_MAR_2.json"
            url_gadm3 = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_MAR_3.json"

            resp1 = requests.get(url_gadm1, timeout=20)
            resp2 = requests.get(url_gadm2, timeout=20)
            resp3 = requests.get(url_gadm3, timeout=20)

            if resp1.status_code == 200:
                gdfs["regions"] = gpd.GeoDataFrame.from_features(
                    resp1.json()["features"], crs="EPSG:4326"
                )
            if resp2.status_code == 200:
                gdfs["provinces"] = gpd.GeoDataFrame.from_features(
                    resp2.json()["features"], crs="EPSG:4326"
                )
            if resp3.status_code == 200:
                gdfs["communes"] = gpd.GeoDataFrame.from_features(
                    resp3.json()["features"], crs="EPSG:4326"
                )
        except Exception as e:
            st.warning(f"Impossible de charger les données GADM distantes : {e}")

    return gdfs


@st.cache_data(show_spinner=False)
def get_column_name(gdf, candidates):
    """Retourne le premier nom de colonne valide dans candidates."""
    if gdf is None:
        return None
    for c in candidates:
        if c in gdf.columns:
            return c
    return gdf.columns[0] if len(gdf.columns) > 0 else None


def get_souss_massa(gdf_regions):
    """Filtre et retourne la géométrie Souss-Massa."""
    if gdf_regions is None:
        return None
    col = get_column_name(gdf_regions, ["NAME_1", "NOM_REGION", "REGION", "name", "NAME"])
    if col is None:
        return None
    mask = gdf_regions[col].str.contains("Souss|Massa|souss|massa", case=False, na=False)
    result = gdf_regions[mask]
    return result if len(result) > 0 else gdf_regions  # fallback : toutes régions


def get_provinces_of_region(gdf_provinces, region_geom):
    """Provinces qui intersectent la région Souss-Massa."""
    if gdf_provinces is None or region_geom is None or len(region_geom) == 0:
        return None
    try:
        return gpd.sjoin(
            gdf_provinces,
            region_geom[["geometry"]],
            how="inner",
            predicate="intersects"
        ).drop_duplicates(subset=gdf_provinces.index.name or gdf_provinces.columns[0])
    except Exception:
        return gdf_provinces


def get_communes_of_province(gdf_communes, province_geom):
    """Communes appartenant à une province donnée."""
    if gdf_communes is None or province_geom is None or len(province_geom) == 0:
        return None
    try:
        return gpd.sjoin(
            gdf_communes,
            province_geom[["geometry"]],
            how="inner",
            predicate="intersects"
        ).drop_duplicates()
    except Exception:
        return gdf_communes


# ─────────────────────────────────────────────
# API Météo — Open-Meteo
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Récupération des prévisions météo…")
def fetch_weather(lat: float, lon: float, days: int = 15):
    """
    Interroge l'API Open-Meteo pour obtenir les prévisions à 15 jours.
    Retourne un DataFrame avec : date, temperature_2m_max, temperature_2m_min,
                                  temperature_2m_mean, precipitation_sum
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
        ],
        "timezone": "Africa/Casablanca",
        "forecast_days": days,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        daily = data.get("daily", {})
        df = pd.DataFrame({
            "date": pd.to_datetime(daily.get("time", [])),
            "T_max": daily.get("temperature_2m_max", []),
            "T_min": daily.get("temperature_2m_min", []),
            "T_mean": daily.get("temperature_2m_mean", []),
            "Précipitations": daily.get("precipitation_sum", []),
        })
        df["date_label"] = df["date"].dt.strftime("%d/%m/%Y")
        return df
    except Exception as e:
        st.error(f"Erreur API Open-Meteo : {e}")
        return pd.DataFrame()


# ─────────────────────────────────────────────
# Carte Folium
# ─────────────────────────────────────────────
def build_map(geometry_gdf, label: str, level: str) -> folium.Map:
    """
    Construit une carte Folium centrée sur l'entité sélectionnée.
    Inclut : OSM, OpenTopoMap (MNT), contour de l'entité, légende.
    """
    bounds = geometry_gdf.total_bounds  # [minx, miny, maxx, maxy]
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8 if level == "région" else (9 if level == "province" else 11),
        tiles=None,
        control_scale=True,
    )

    # ── Fond de plan OSM ──────────────────────────────────────────────────
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="OpenStreetMap",
        overlay=False,
        control=True,
    ).add_to(m)

    # ── MNT OpenTopoMap ───────────────────────────────────────────────────
    folium.TileLayer(
        tiles="https://tile.opentopomap.org/{z}/{x}/{y}.png",
        name="MNT — OpenTopoMap",
        attr='Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)',
        overlay=True,
        control=True,
        opacity=0.7,
    ).add_to(m)

    # ── WMS Terrestris SRTM ───────────────────────────────────────────────
    folium.WmsTileLayer(
        url="https://ows.terrestris.de/osm/service",
        name="MNT SRTM — Terrestris",
        layers="SRTM30-Hillshade",
        fmt="image/png",
        transparent=True,
        overlay=True,
        control=True,
        opacity=0.5,
        attr="© Terrestris / SRTM",
    ).add_to(m)

    # ── Contour de l'entité ───────────────────────────────────────────────
    style = {
        "fillColor": "transparent",
        "color": "#e63946",
        "weight": 3,
        "dashArray": "6 3",
    }
    highlight = {
        "fillColor": "rgba(230,57,70,0.1)",
        "color": "#c1121f",
        "weight": 4,
    }

    folium.GeoJson(
        data=geometry_gdf.__geo_interface__,
        name=label,
        style_function=lambda _: style,
        highlight_function=lambda _: highlight,
        tooltip=folium.GeoJsonTooltip(
            fields=[c for c in geometry_gdf.columns if c != "geometry"][:3],
            labels=True,
            sticky=False,
        ),
    ).add_to(m)

    # ── Fit bounds ────────────────────────────────────────────────────────
    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    # ── Légende HTML ──────────────────────────────────────────────────────
    legend_html = f"""
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:rgba(255,255,255,0.92);padding:10px 14px;
                border-radius:10px;border:1px solid #ccc;font-size:12px;
                box-shadow:2px 2px 8px rgba(0,0,0,0.2);min-width:160px;">
      <b style="font-size:13px;">Légende</b><br><br>
      <span style="display:inline-block;width:28px;height:3px;
            background:#e63946;border-top:3px dashed #e63946;
            vertical-align:middle;margin-right:6px;"></span>
      Contour : {label}<br>
      <span style="display:inline-block;width:28px;height:10px;
            background:linear-gradient(to right,#3a6186,#89253e);
            vertical-align:middle;margin-right:6px;margin-top:4px;
            border-radius:2px;"></span>
      MNT / Relief (SRTM)
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    # ── Titre ─────────────────────────────────────────────────────────────
    title_html = f"""
    <div style="position:fixed;top:12px;left:50%;transform:translateX(-50%);
                z-index:1000;background:rgba(10,35,66,0.85);color:#fff;
                padding:8px 20px;border-radius:8px;font-size:14px;
                font-family:'DM Sans',sans-serif;letter-spacing:0.04em;
                pointer-events:none;white-space:nowrap;">
      📍 {level.title()} — {label}
    </div>"""
    m.get_root().html.add_child(folium.Element(title_html))

    folium.LayerControl(collapsed=False).add_to(m)
    return m


# ─────────────────────────────────────────────
# Graphiques climatiques
# ─────────────────────────────────────────────
def plot_temperature(df: pd.DataFrame, entity_name: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date_label"], y=df["T_max"],
        name="T° max", mode="lines+markers",
        line=dict(color="#e63946", width=2),
        marker=dict(size=6),
        hovertemplate="%{x}<br>Max : %{y:.1f} °C<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date_label"], y=df["T_mean"],
        name="T° moyenne", mode="lines+markers",
        line=dict(color="#457b9d", width=2.5, dash="dot"),
        marker=dict(size=6),
        hovertemplate="%{x}<br>Moy : %{y:.1f} °C<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date_label"], y=df["T_min"],
        name="T° min", mode="lines+markers",
        line=dict(color="#1d3557", width=2),
        marker=dict(size=6),
        hovertemplate="%{x}<br>Min : %{y:.1f} °C<extra></extra>",
        fill="tonexty",
        fillcolor="rgba(69,123,157,0.08)",
    ))
    fig.update_layout(
        title=dict(
            text=f"Prévision de Température — {entity_name}",
            font=dict(family="Playfair Display, serif", size=18, color="#0a2342"),
        ),
        xaxis=dict(title="Date", tickangle=-35, showgrid=True, gridcolor="#e2e8f0"),
        yaxis=dict(title="Température (°C)", showgrid=True, gridcolor="#e2e8f0"),
        legend=dict(orientation="h", y=-0.25),
        hovermode="x unified",
        plot_bgcolor="#f8fafc",
        paper_bgcolor="#ffffff",
        margin=dict(t=60, b=80),
        height=380,
    )
    return fig


def plot_precipitation(df: pd.DataFrame, entity_name: str) -> go.Figure:
    colors = ["#0369a1" if v > 5 else "#7dd3fc" for v in df["Précipitations"].fillna(0)]
    fig = go.Figure(go.Bar(
        x=df["date_label"],
        y=df["Précipitations"].fillna(0),
        name="Précipitations",
        marker_color=colors,
        hovertemplate="%{x}<br>Précipitations : %{y:.1f} mm<extra></extra>",
    ))
    fig.update_layout(
        title=dict(
            text=f"Prévision des Précipitations — {entity_name}",
            font=dict(family="Playfair Display, serif", size=18, color="#0a2342"),
        ),
        xaxis=dict(title="Date", tickangle=-35, showgrid=False),
        yaxis=dict(title="Précipitations (mm)", showgrid=True, gridcolor="#e2e8f0"),
        plot_bgcolor="#f8fafc",
        paper_bgcolor="#ffffff",
        margin=dict(t=60, b=80),
        height=380,
        bargap=0.3,
    )
    return fig


# ─────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────
def main():
    # Bannière hero
    st.markdown("""
    <div class="hero-banner">
      <div style="font-size:3rem;">🌊</div>
      <div>
        <p class="hero-title">Souss-Massa · Dashboard Géospatial</p>
        <p class="hero-sub">Prévisions météorologiques & exploration du territoire — GIS Programming 2025-2026</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chargement des données ─────────────────────────────────────────────
    gdfs = load_admin_data()
    gdf_regions   = gdfs.get("regions")
    gdf_provinces = gdfs.get("provinces")
    gdf_communes  = gdfs.get("communes")

    # Filtrage Souss-Massa
    sm_region = get_souss_massa(gdf_regions)

    # ── SIDEBAR ────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🗺️ Navigation administrative")
        st.markdown("---")

        # Niveau sélectionné
        active_level = st.radio(
            "Niveau géographique",
            options=["Région", "Province", "Commune"],
            index=0,
            horizontal=False,
        )

        # Région (figée sur Souss-Massa)
        st.markdown("**Région**")
        st.info("📍 Souss-Massa")

        selected_province = None
        selected_commune  = None
        prov_gdf_filtered = None
        com_gdf_filtered  = None

        # Provinces
        if active_level in ["Province", "Commune"]:
            prov_col = get_column_name(gdf_provinces, ["NAME_2", "NOM_PROVINCE", "PROVINCE", "name", "NAME"])
            if gdf_provinces is not None:
                prov_in_sm = get_provinces_of_region(gdf_provinces, sm_region)
                if prov_in_sm is not None and prov_col:
                    prov_list = sorted(prov_in_sm[prov_col].dropna().unique().tolist())
                    if prov_list:
                        selected_province = st.selectbox("Province", prov_list)
                        prov_gdf_filtered = prov_in_sm[prov_in_sm[prov_col] == selected_province]
                    else:
                        st.warning("Aucune province trouvée pour cette région.")
                else:
                    st.warning("Couche provinces non disponible.")

        # Communes
        if active_level == "Commune" and prov_gdf_filtered is not None:
            com_col = get_column_name(gdf_communes, ["NAME_3", "NOM_COMMUNE", "COMMUNE", "name", "NAME"])
            if gdf_communes is not None:
                com_in_prov = get_communes_of_province(gdf_communes, prov_gdf_filtered)
                if com_in_prov is not None and com_col:
                    com_list = sorted(com_in_prov[com_col].dropna().unique().tolist())
                    if com_list:
                        selected_commune = st.selectbox("Commune", com_list)
                        com_gdf_filtered = com_in_prov[com_in_prov[com_col] == selected_commune]
                else:
                    st.warning("Aucune commune trouvée pour cette province.")

        st.markdown("---")
        st.markdown("### 🌡️ Paramètre climatique")
        param = st.radio(
            "Afficher",
            options=["Température (T2m)", "Précipitations"],
            index=0,
        )

        st.markdown("---")
        st.caption("Sources : Open-Meteo API · OpenTopoMap · GADM · Terrestris WMS")

    # ── Détermination de l'entité active ──────────────────────────────────
    if active_level == "Région" or sm_region is None or len(sm_region) == 0:
        active_gdf   = sm_region if sm_region is not None and len(sm_region) > 0 else gdf_regions
        active_label = "Souss-Massa"
        active_level_str = "région"
    elif active_level == "Province" and prov_gdf_filtered is not None and len(prov_gdf_filtered) > 0:
        active_gdf   = prov_gdf_filtered
        active_label = selected_province or "Province"
        active_level_str = "province"
    elif active_level == "Commune" and com_gdf_filtered is not None and len(com_gdf_filtered) > 0:
        active_gdf   = com_gdf_filtered
        active_label = selected_commune or "Commune"
        active_level_str = "commune"
    else:
        active_gdf   = sm_region if sm_region is not None and len(sm_region) > 0 else gdf_regions
        active_label = "Souss-Massa"
        active_level_str = "région"

    # Centroïde pour API météo
    if active_gdf is not None and len(active_gdf) > 0:
        centroid = active_gdf.geometry.union_all().centroid
        lat_center = centroid.y
        lon_center = centroid.x
    else:
        lat_center, lon_center = 30.42, -8.65  # fallback Agadir

    # ── Colonnes principales ───────────────────────────────────────────────
    col_map, col_weather = st.columns([3, 2], gap="large")

    # ════════════════════════════════════════════
    # COLONNE GAUCHE — Carte
    # ════════════════════════════════════════════
    with col_map:
        st.markdown(f'<p class="section-title">🗺️ Carte — {active_label}</p>', unsafe_allow_html=True)

        if active_gdf is not None and len(active_gdf) > 0:
            folium_map = build_map(active_gdf, active_label, active_level_str)
            map_data = st_folium(
                folium_map,
                width="100%",
                height=520,
                returned_objects=["last_active_drawing"],
                key=f"map_{active_label}_{active_level_str}",
            )
        else:
            st.markdown("""
            <div class="info-box">
              ⚠️ Les couches administratives ne sont pas disponibles localement.<br>
              Placez vos shapefiles dans le dossier <code>data/</code> ou vérifiez la connexion aux sources distantes.
            </div>
            """, unsafe_allow_html=True)

        # Métriques géographiques
        if active_gdf is not None and len(active_gdf) > 0:
            bounds = active_gdf.total_bounds
            area_approx = abs((bounds[2]-bounds[0]) * (bounds[3]-bounds[1])) * 111.32**2
            st.markdown('<p class="section-title">📐 Informations spatiales</p>', unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"""<div class="metric-card">
                  <div class="label">Latitude centre</div>
                  <div class="value">{lat_center:.3f}°</div></div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card">
                  <div class="label">Longitude centre</div>
                  <div class="value">{lon_center:.3f}°</div></div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""<div class="metric-card">
                  <div class="label">Surface approx.</div>
                  <div class="value">{area_approx:,.0f} km²</div></div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # COLONNE DROITE — Météo
    # ════════════════════════════════════════════
    with col_weather:
        st.markdown(f'<p class="section-title">🌤️ Prévisions 15 jours — {active_label}</p>', unsafe_allow_html=True)

        df_weather = fetch_weather(lat_center, lon_center, days=15)

        if not df_weather.empty:
            # KPIs résumés
            today_row = df_weather.iloc[0]
            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown(f"""<div class="metric-card">
                  <div class="label">T° aujourd'hui</div>
                  <div class="value">{today_row['T_mean']:.1f} °C</div></div>""", unsafe_allow_html=True)
            with k2:
                st.markdown(f"""<div class="metric-card">
                  <div class="label">Max 15 jours</div>
                  <div class="value">{df_weather['T_max'].max():.1f} °C</div></div>""", unsafe_allow_html=True)
            with k3:
                pluie_totale = df_weather["Précipitations"].sum()
                st.markdown(f"""<div class="metric-card">
                  <div class="label">Pluie totale</div>
                  <div class="value">{pluie_totale:.1f} mm</div></div>""", unsafe_allow_html=True)

            # Graphique
            st.markdown("<br>", unsafe_allow_html=True)
            if "Température" in param:
                fig = plot_temperature(df_weather, active_label)
            else:
                fig = plot_precipitation(df_weather, active_label)

            st.plotly_chart(fig, use_container_width=True)

            # Tableau récapitulatif
            with st.expander("📊 Tableau des prévisions détaillées"):
                display_df = df_weather[["date_label", "T_min", "T_mean", "T_max", "Précipitations"]].copy()
                display_df.columns = ["Date", "T° min (°C)", "T° moy (°C)", "T° max (°C)", "Précip. (mm)"]
                st.dataframe(display_df, use_container_width=True, hide_index=True)

        else:
            st.markdown("""
            <div class="info-box">
              ⚠️ Données météo indisponibles. Vérifiez votre connexion Internet.
            </div>
            """, unsafe_allow_html=True)

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="footer">
      Application développée dans le cadre du cours <strong>GIS Programming 2025-2026</strong> · EHTP<br>
      Données : Open-Meteo API · OpenTopoMap · GADM · Terrestris WMS · © OpenStreetMap contributors
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
