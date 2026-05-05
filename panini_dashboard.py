import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
import time

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Panini · Cyclic Counts · Pre-Mundial",
    page_icon="⚽",
    layout="wide",
)

# ── REDASH QUERIES ────────────────────────────────────────────────────────────
REDASH_BASE = "https://redash.rappi.com"
QUERIES = {
    "CO": {"id": 132892, "key": "JCVmRpIHwSh8nfweOTDF58dbRLCu91LhcELMc0Uy"},
    "AR": {"id": 132897, "key": "CnUgQQxJEOK3EUDZBjFyRdoLFyX7K2MyjzN8REi0"},
    "MX": {"id": 132988, "key": "PHEAUz7V0zuaHZx5r3uJ7nFfHi72bKmbRxOEo4a0"},
    "PE": {"id": 132989, "key": "z7q7Mi8d87JQRioGNgrnv1mp5AYchwdFj26UpTYT"},
    "BR": {"id": 132990, "key": "Sa4wt1B2jsiR0l7mjq5rX0v1Xh0cQzJZO5OmRiMQ"},
    "CL": {"id": 132991, "key": "tCQiE9BrGV1Y4iTZOD7OKV0ozAY8mIEPajHyNhes"},
}

FLAGS = {"AR": "🇦🇷", "BR": "🇧🇷", "CL": "🇨🇱", "CO": "🇨🇴", "MX": "🇲🇽", "PE": "🇵🇪"}

# ── PRODUCT MAPPING ───────────────────────────────────────────────────────────
PRODUCTS = {
    14554: "Panini Sobres de Figuritas Copa Mundial FIFA 2026",
    14661: "Gifting Panini Álbum Muestra Obsequio Copa Mundial FIFA 2026",
    27246: "Display Sobres Copa Mundial",
    27248: "Sobre Copa Mundial Fifa 2026",
    27870: "Obsequio Album Pasta Blanda Copa Mundial",
    27245: "Album Pasta Blanda Copa Mundial",
    27247: "Album Pasta Dura Copa Mundial",
    90543: "Panini Caja con 100 Sobres Mundial 2026",
    90544: "Panini Álbum Mundial 2026 Pasta Blanda",
    91919: "Panini Álbum Fifa World Cup 2026 Pasta Dura",
    91927: "Panini Sobre con 7 Estampas Dida World Cup 2026",
    27137: "Álbum Oficial Copa Del Mundo FIFA 2026 Tapa Gold",
    26876: "Álbum Oficial Copa Del Mundo FIFA 2026 Tapa Dura",
    26839: "Álbum Oficial Copa Del Mundo FIFA 2026 Tapa Blanda",
    26828: "Pack Con Figuras Adhesivas Copa Del Mundo FIFA 2026",
    26806: "Sobre Con Figuras Adhesivas Copa Del Mundo FIFA 2026",
    44242: "Blister Cartela + Envelopes De Figurinhas Copa Do Mundo 2026",
    44244: "Dispenser Com Envelopes De Figurinhas Copa Do Mundo 2026",
    19394: "Panini Sobre Stickers Mundial Fifa 2026",
    19390: "Panini Album Mundial Fifa 2026",
    19392: "Panini Album Color Mundial Fifa 2026",
    19389: "Panini Album Gold Mundial Fifa 2026",
    19391: "Panini Album Silver Mundial Fifa 2026",
}

# ── WAREHOUSE MAPPING ─────────────────────────────────────────────────────────
WAREHOUSES = {
    "AR": {
        11:"Las Heras", 4:"Humboldt", 7:"Baez", 14:"San Martín", 38:"La Plata",
        23:"Monserrat", 6:"Lavalle", 43:"Ramos", 26:"Perón", 50:"Morón",
        46:"Córdoba", 45:"Villa Lynch", 9:"Villa Martelli", 3:"Monroe",
        42:"Vicente López", 24:"Forest", 48:"Nordelta", 49:"Beccar",
        22:"San Juan", 41:"Lomas de Zamora", 18:"Mar del Plata", 25:"Rivadavia",
        27:"Centenera", 51:"Lanús", 54:"Rosario", 800:"Cerro las Rosas",
    },
    "BR": {
        3:"Santana", 53:"Vila Clementino", 59:"Vila Prudente", 74:"Carrão",
        139:"Bonfinglioli", 155:"Alphaville", 161:"Santo André", 6:"Santo Amaro",
        32:"Moema", 36:"Santa Cecília", 115:"Lapa", 117:"Morumbi", 158:"Cambui",
        386:"Jardins", 8:"Aldeota", 12:"Estoril", 15:"Aflitos", 30:"Santa Efigênia",
        37:"Vila Izabel", 56:"PA Centro", 87:"Alto do XV", 127:"Castelo",
        141:"Recife Sul", 49:"Nova Recreio", 55:"Leblon", 67:"Barra da Tijuca 3",
        121:"Barra da Tijuca 2", 123:"Tijuca", 148:"Ipanema", 382:"Botafogo II",
        385:"Catete II", 4:"Vila Mascote", 5:"Aclimação", 13:"Vila Olimpia",
        19:"Alto Do Ipiranga", 29:"Bela Vista", 91:"Brooklin II", 119:"Vila Madalena",
        167:"Crossdock Castelo", 389:"Santa Cecília Farma",
    },
    "CL": {
        19:"Roger de Flor", 21:"Chile España", 50:"Bustamante", 149:"Reñaca",
        151:"Isabel La Católica", 12:"Vitacura 3", 44:"La Dehesa", 58:"La Florida",
        135:"Consistorial", 55:"Crossdock Balmoral",
    },
    "CO": {
        16:"Comuneros", 18:"Niza", 24:"Parque Bavaria", 47:"Chapinero",
        61:"Américas", 72:"Esperanza", 73:"Modelia", 4:"Las Colinas",
        49:"Villa Andalucía BAQ", 63:"El Poblado Baq", 66:"El Prado BAQ",
        108:"Bavaria SM", 111:"Rodadero", 21:"Manila", 29:"La Mota",
        31:"La Playa", 68:"Laureles", 91:"Turbo San Pablo", 2:"Parque del Perro",
        79:"San Vicente", 90:"Limonar", 93:"C Jardín CLO", 103:"Armenia",
        104:"Pereira", 800:"Manizales", 25:"Envigado Alto", 27:"Sabaneta",
        48:"La Frontera", 52:"Tesoro", 55:"Envigado Bajo", 3:"Castellana",
        5:"Mar Del Norte", 6:"Manga", 7:"Bocagrande", 105:"Alameda",
        112:"Valledupar", 8:"Country", 11:"Palermo", 14:"Cedritos",
        17:"Colina", 23:"Engativá Occidental", 110:"Quinta Camacho",
        801:"Prado Veraniego", 12:"Turbo Polo", 19:"Iserra 100",
        50:"San Patricio", 58:"Suba Turingia", 67:"Barrancas", 78:"Chilacos",
        9:"Chicó", 28:"Granada Norte", 33:"La Cabaña", 51:"Usaquén",
        60:"Verbenal", 70:"Titán", 84:"Cañaveral", 106:"Ibagué",
        107:"Cabecera", 109:"Villavicencio", 113:"El Rosal",
    },
    "MX": {
        105:"Avante", 210:"San Mike", 217:"Lindavista", 353:"Granjas",
        443:"Toreo", 804:"Narvarte", 53:"Fidel", 63:"Jardines de la Patria",
        71:"Paseo del Sol", 263:"Tapatía", 354:"Sauz", 402:"Solares",
        403:"Zapopan", 800:"Bugambilias", 96:"Duraznos", 206:"El Rosario",
        264:"San Ramon", 392:"Bosque Real", 409:"Portillo", 801:"Bosques",
        49:"Altavista", 52:"Leones", 184:"San Pedro", 400:"Calete",
        406:"Encinas", 413:"República", 417:"Valle Oriente", 320:"Roma Norte",
        332:"Toriello Guerra", 389:"Manitoba", 445:"La Raza", 143:"Interlomas",
        207:"Santa Fe", 218:"Huicholes", 310:"Las Águilas", 446:"Atizapan",
        89:"Portales Norte", 110:"Zedec", 152:"Florida", 336:"Campestre",
        376:"Cholula", 378:"La Paz MX", 379:"Lomas", 380:"Angelópolis",
        396:"Constituyentes", 397:"Arcos", 247:"Carso", 327:"Frida",
        434:"Parque Lira", 129:"Ángel de Independencia", 253:"Ajusco",
        265:"Tlalpan", 268:"Fuentes del Pedregal", 270:"San Ángel", 430:"Turbo Oasis",
    },
    "PE": {
        7:"Bellavista Callao", 24:"Juan Valer", 42:"Alfredo Mendiola",
        63:"Lince", 65:"Benavides", 1:"La Paz PE", 5:"Rosa Toro",
        6:"Jorge Chávez", 9:"Tahiti", 3:"Primavera", 8:"Punta Hermosa",
        12:"Petit Thouars", 14:"Angamos", 56:"Machu Picchu", 4:"Sucre",
        17:"Cataratas", 18:"San Luis", 62:"Sevilla", 66:"Alfonso Ugarte",
        19:"Caminos del Inca", 20:"Almirante Miguel Grau", 2:"Los Jilgueros",
        21:"Cross Docking Belisario", 40:"MFC Las Torres", 800:"Santa Anita",
    },
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #F5F6FA !important; }
[data-testid="stSidebar"]           { background: #FFFFFF !important; border-right: 1px solid #E2E6EF; }
[data-testid="stHeader"]            { background: #F5F6FA !important; }
.block-container                    { padding-top: 0.5rem !important; }
h1, h2, h3                          { color: #1A1A2E !important; }

.panini-header {
    background: linear-gradient(135deg, #E8192C 0%, #c0121f 50%, #8b0000 100%);
    border-radius: 16px;
    padding: 24px 36px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(232,25,44,0.2);
    border-left: 6px solid #F5C518;
}
.panini-header h1 {
    font-size: 1.9rem; font-weight: 900; color: white !important;
    letter-spacing: 2px; margin: 0; text-transform: uppercase;
}
.panini-header p { color: rgba(255,255,255,0.85); margin: 5px 0 0; font-size: 0.82rem; }

div[data-testid="metric-container"] {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 14px 18px;
    border: 1px solid #E2E6EF;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-top: 3px solid #E8192C;
}
div[data-testid="stMetricLabel"] > div { color: #888 !important; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; }
div[data-testid="stMetricValue"]       { color: #1A1A2E !important; font-size: 1.9rem; font-weight: 800; }
div[data-testid="stMetricDelta"]       { color: #00A86B !important; }

[data-testid="stDataFrame"] { background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E6EF; }

[data-testid="stButton"] > button {
    background: #E8192C !important; color: white !important;
    border: none !important; border-radius: 8px !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] h2 { color: #E8192C !important; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%A %d %B %Y · %H:%M")
st.markdown(f"""
<div class="panini-header">
    <h1>⚽ Panini · Cyclic Counts · Pre-Mundial 2026</h1>
    <p>Monitor de misiones del día &nbsp;·&nbsp; {now_str}</p>
</div>
""", unsafe_allow_html=True)

# ── FETCH ─────────────────────────────────────────────────────────────────────
def fetch_country(country, config):
    headers = {"Authorization": f"Key {config['key']}", "Content-Type": "application/json"}

    # Step 1: POST to trigger execution and get job/result
    post_url = f"{REDASH_BASE}/api/queries/{config['id']}/results"
    try:
        r = requests.post(post_url, headers=headers, json={}, timeout=60)
        r.raise_for_status()
        data = r.json()

        # If we got query_result directly
        if "query_result" in data:
            rows = data["query_result"]["data"]["rows"]
            df = pd.DataFrame(rows)
            if not df.empty:
                df["country"] = country
            return country, df, None

        # If we got a job, poll until done
        if "job" in data:
            job_id = data["job"]["id"]
            for _ in range(30):  # max ~30s
                time.sleep(1)
                jr = requests.get(f"{REDASH_BASE}/api/jobs/{job_id}", headers=headers, timeout=15).json()
                job = jr.get("job", {})
                if job.get("status") == 3:  # success
                    result_id = job["query_result_id"]
                    rr = requests.get(f"{REDASH_BASE}/api/query_results/{result_id}.json", headers=headers, timeout=15)
                    rows = rr.json()["query_result"]["data"]["rows"]
                    df = pd.DataFrame(rows)
                    if not df.empty:
                        df["country"] = country
                    return country, df, None
                if job.get("status") == 4:  # error
                    return country, pd.DataFrame(), job.get("error", "Job failed")
            return country, pd.DataFrame(), "Timeout esperando resultado"

        return country, pd.DataFrame(), f"Respuesta inesperada: {str(data)[:200]}"

    except Exception as e:
        return country, pd.DataFrame(), str(e)

@st.cache_data(ttl=300)
def load_all():
    results, errors = {}, {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(fetch_country, c, cfg): c for c, cfg in QUERIES.items()}
        for f in concurrent.futures.as_completed(futures):
            country, df, err = f.result()
            if err:
                errors[country] = err
            else:
                results[country] = df
    dfs = [df for df in results.values() if not df.empty]
    combined = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    return combined, errors

# ── REFRESH BUTTON ────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([1, 6])
with col_btn:
    if st.button("🔄  Refrescar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_info:
    st.caption("Cache de 5 minutos. Presiona Refrescar para traer datos frescos ahora.")

with st.spinner("Consultando Redash en todos los países..."):
    df_all, errors = load_all()

for country, err in errors.items():
    st.warning(f"{FLAGS.get(country, country)} **{country}** — {err}")

if df_all.empty:
    st.info("Sin datos disponibles por el momento. Verifica las queries en Redash.")
    st.stop()

# ── NORMALIZE ─────────────────────────────────────────────────────────────────
df_all.columns = [c.lower() for c in df_all.columns]

def safe_int(val):
    try:    return int(float(val))
    except: return None

df_all["store_reference_id"] = df_all["store_reference_id"].apply(safe_int)
df_all["warehouse_id"]        = df_all["warehouse_id"].apply(safe_int)
df_all["difference"]          = pd.to_numeric(df_all.get("difference", 0), errors="coerce").fillna(0)
df_all["total_missions"]      = pd.to_numeric(df_all.get("total_missions", 0), errors="coerce").fillna(0)
df_all["total_quantity"]      = pd.to_numeric(df_all.get("total_quantity", 0), errors="coerce").fillna(0)
df_all["vivo_stock"]          = pd.to_numeric(df_all.get("vivo_stock", 0), errors="coerce").fillna(0)

df_all["product_name"]    = df_all["store_reference_id"].apply(lambda x: PRODUCTS.get(x, f"ID {x}"))
df_all["warehouse_name"]  = df_all.apply(
    lambda r: WAREHOUSES.get(r["country"], {}).get(r["warehouse_id"], f"WH {r['warehouse_id']}"), axis=1
)
df_all["flag"] = df_all["country"].map(FLAGS).fillna("🌐")
df_all["status_name"] = df_all.get("status_name", pd.Series(["—"]*len(df_all)))

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔎 Filtros")

    countries_opts  = ["Todos"] + sorted(df_all["country"].unique().tolist())
    statuses_opts   = ["Todos", "FINALIZED", "PENDING", "OTHER"]
    products_opts   = ["Todos"] + sorted(df_all["product_name"].unique().tolist())
    warehouses_opts = ["Todos"] + sorted(df_all["warehouse_name"].unique().tolist())

    sel_country   = st.selectbox("🌎 País",     countries_opts)
    sel_status    = st.selectbox("📋 Estado",   statuses_opts)
    sel_product   = st.selectbox("📦 Producto", products_opts)
    sel_warehouse = st.selectbox("🏪 Bodega",   warehouses_opts)

    st.markdown("---")
    st.caption(f"Datos al: **{datetime.now().strftime('%H:%M:%S')}**")

# Apply filters
df_f = df_all.copy()
if sel_country   != "Todos": df_f = df_f[df_f["country"]        == sel_country]
if sel_status    != "Todos": df_f = df_f[df_f["status_name"]     == sel_status]
if sel_product   != "Todos": df_f = df_f[df_f["product_name"]    == sel_product]
if sel_warehouse != "Todos": df_f = df_f[df_f["warehouse_name"]  == sel_warehouse]

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown("### 📊 Resumen del día")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🌎 Países activos",    df_f["country"].nunique())
k2.metric("🏪 Productos",         df_f["store_reference_id"].nunique())
k3.metric("✅ Finalizadas",        int((df_f["status_name"] == "FINALIZED").sum()))
k4.metric("⏳ Pendientes",         int((df_f["status_name"] == "PENDING").sum()))
k5.metric("📦 Units Gap total",   f"{int(df_f['difference'].sum()):,}")

st.markdown("")

# ── RESUMEN POR PAÍS ──────────────────────────────────────────────────────────
st.markdown("### 🌎 Resumen por país")
summary = (
    df_f.groupby(["flag", "country"])
    .agg(
        Productos    =("store_reference_id", "nunique"),
        Bodegas      =("warehouse_id",       "nunique"),
        Total        =("status_name",        "count"),
        Finalizadas  =("status_name",        lambda x: (x == "FINALIZED").sum()),
        Pendientes   =("status_name",        lambda x: (x == "PENDING").sum()),
        Units_Gap    =("difference",         "sum"),
    )
    .reset_index()
)
summary["% Completo"] = (summary["Finalizadas"] / summary["Total"].replace(0, 1) * 100).round(1).astype(str) + "%"
summary["Units_Gap"]  = summary["Units_Gap"].apply(lambda x: f"{int(x):,}")
summary = summary.rename(columns={"flag": "", "country": "País"})
st.dataframe(summary, use_container_width=True, hide_index=True)

# ── DETALLE ───────────────────────────────────────────────────────────────────
st.markdown("### 📋 Detalle por misión")

col_map = {
    "flag":               "🌎",
    "country":            "País",
    "warehouse_name":     "Bodega",
    "warehouse_id":       "WH ID",
    "product_name":       "Producto",
    "store_reference_id": "Sync ID",
    "picker_name":        "Picker",
    "status_name":        "Estado",
    "total_missions":     "Misiones",
    "total_quantity":     "Cantidad contada",
    "vivo_stock":         "Stock Vivo",
    "difference":         "Diferencia",
}

# Pick started_at column (may be started_at_local or started_at)
started_col = "started_at_local" if "started_at_local" in df_f.columns else "started_at"
col_map[started_col] = "Inicio (local)"

show_cols = [c for c in col_map if c in df_f.columns]
df_show   = df_f[show_cols].rename(columns=col_map).copy()

# Style
def style_row(row):
    styles = [""] * len(row)
    cols = list(row.index)
    if "Estado" in cols:
        i = cols.index("Estado")
        if row["Estado"] == "FINALIZED":
            styles[i] = "color: #00C48C; font-weight: bold"
        elif row["Estado"] == "PENDING":
            styles[i] = "color: #FF7A30; font-weight: bold"
    if "Diferencia" in cols:
        i = cols.index("Diferencia")
        v = row["Diferencia"]
        try:
            v = float(v)
            if   v > 50: styles[i] = "color: #E8192C; font-weight: bold"
            elif v > 0:  styles[i] = "color: #FF7A30"
            elif v < 0:  styles[i] = "color: #4A9EFF"
            else:        styles[i] = "color: #8899AA"
        except: pass
    return styles

styled = df_show.style.apply(style_row, axis=1)
st.dataframe(styled, use_container_width=True, height=520)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    f"⚽ Panini · Pre-Mundial 2026 · "
    f"Última carga: {datetime.now().strftime('%H:%M:%S')} · "
    f"Cache 5 min · Fuente: Redash por país"
)
