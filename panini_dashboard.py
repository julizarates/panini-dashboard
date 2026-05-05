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

# ── REDASH ────────────────────────────────────────────────────────────────────
REDASH_BASE = "https://redash.rappi.com"
QUERIES = {
    "CO": {"id": 132892, "key": "JCVmRpIHwSh8nfweOTDF58dbRLCu91LhcELMc0Uy"},
    "AR": {"id": 132897, "key": "CnUgQQxJEOK3EUDZBjFyRdoLFyX7K2MyjzN8REi0"},
    "MX": {"id": 132988, "key": "PHEAUz7V0zuaHZx5r3uJ7nFfHi72bKmbRxOEo4a0"},
    "PE": {"id": 132989, "key": "z7q7Mi8d87JQRioGNgrnv1mp5AYchwdFj26UpTYT"},
    "BR": {"id": 132990, "key": "Sa4wt1B2jsiR0l7mjq5rX0v1Xh0cQzJZO5OmRiMQ"},
    "CL": {"id": 132991, "key": "tCQiE9BrGV1Y4iTZOD7OKV0ozAY8mIEPajHyNhes"},
}
FLAGS = {"AR":"🇦🇷","BR":"🇧🇷","CL":"🇨🇱","CO":"🇨🇴","MX":"🇲🇽","PE":"🇵🇪"}
COUNTRY_COLORS = {"CO":"#E8192C","AR":"#74AADB","MX":"#27AE60","BR":"#F39C12","PE":"#8E44AD","CL":"#E67E22"}

PRODUCTS = {
    14554:"Panini Sobres Figuritas Copa Mundial FIFA 2026",
    14661:"Gifting Álbum Muestra Obsequio Copa Mundial FIFA 2026",
    27246:"Display Sobres Copa Mundial",
    27248:"Sobre Copa Mundial Fifa 2026",
    27870:"Obsequio Album Pasta Blanda Copa Mundial",
    27245:"Album Pasta Blanda Copa Mundial",
    27247:"Album Pasta Dura Copa Mundial",
    90543:"Panini Caja 100 Sobres Mundial 2026",
    90544:"Panini Álbum Mundial 2026 Pasta Blanda",
    91919:"Panini Álbum Fifa World Cup 2026 Pasta Dura",
    91927:"Panini Sobre 7 Estampas Dida World Cup 2026",
    27137:"Álbum Copa Del Mundo FIFA 2026 Tapa Gold",
    26876:"Álbum Copa Del Mundo FIFA 2026 Tapa Dura",
    26839:"Álbum Copa Del Mundo FIFA 2026 Tapa Blanda",
    26828:"Pack Figuras Adhesivas Copa Del Mundo FIFA 2026",
    26806:"Sobre Figuras Adhesivas Copa Del Mundo FIFA 2026",
    44242:"Blister Cartela + Envelopes Figurinhas Copa Do Mundo 2026",
    44244:"Dispenser Envelopes Figurinhas Copa Do Mundo 2026",
    19394:"Panini Sobre Stickers Mundial Fifa 2026",
    19390:"Panini Album Mundial Fifa 2026",
    19392:"Panini Album Color Mundial Fifa 2026",
    19389:"Panini Album Gold Mundial Fifa 2026",
    19391:"Panini Album Silver Mundial Fifa 2026",
}

WAREHOUSES = {
    "AR":{11:"Las Heras",4:"Humboldt",7:"Baez",14:"San Martín",38:"La Plata",23:"Monserrat",6:"Lavalle",43:"Ramos",26:"Perón",50:"Morón",46:"Córdoba",45:"Villa Lynch",9:"Villa Martelli",3:"Monroe",42:"Vicente López",24:"Forest",48:"Nordelta",49:"Beccar",22:"San Juan",41:"Lomas de Zamora",18:"Mar del Plata",25:"Rivadavia",27:"Centenera",51:"Lanús",54:"Rosario",800:"Cerro las Rosas"},
    "BR":{3:"Santana",53:"Vila Clementino",59:"Vila Prudente",74:"Carrão",139:"Bonfinglioli",155:"Alphaville",161:"Santo André",6:"Santo Amaro",32:"Moema",36:"Santa Cecília",115:"Lapa",117:"Morumbi",158:"Cambui",386:"Jardins",8:"Aldeota",12:"Estoril",15:"Aflitos",30:"Santa Efigênia",37:"Vila Izabel",56:"PA Centro",87:"Alto do XV",127:"Castelo",141:"Recife Sul",49:"Nova Recreio",55:"Leblon",67:"Barra da Tijuca 3",121:"Barra da Tijuca 2",123:"Tijuca",148:"Ipanema",382:"Botafogo II",385:"Catete II",4:"Vila Mascote",5:"Aclimação",13:"Vila Olimpia",19:"Alto Do Ipiranga",29:"Bela Vista",91:"Brooklin II",119:"Vila Madalena",167:"Crossdock Castelo",389:"Santa Cecília Farma"},
    "CL":{19:"Roger de Flor",21:"Chile España",50:"Bustamante",149:"Reñaca",151:"Isabel La Católica",12:"Vitacura 3",44:"La Dehesa",58:"La Florida",135:"Consistorial",55:"Crossdock Balmoral"},
    "CO":{16:"Comuneros",18:"Niza",24:"Parque Bavaria",47:"Chapinero",61:"Américas",72:"Esperanza",73:"Modelia",4:"Las Colinas",49:"Villa Andalucía BAQ",63:"El Poblado Baq",66:"El Prado BAQ",108:"Bavaria SM",111:"Rodadero",21:"Manila",29:"La Mota",31:"La Playa",68:"Laureles",91:"Turbo San Pablo",2:"Parque del Perro",79:"San Vicente",90:"Limonar",93:"C Jardín CLO",103:"Armenia",104:"Pereira",800:"Manizales",25:"Envigado Alto",27:"Sabaneta",48:"La Frontera",52:"Tesoro",55:"Envigado Bajo",3:"Castellana",5:"Mar Del Norte",6:"Manga",7:"Bocagrande",105:"Alameda",112:"Valledupar",8:"Country",11:"Palermo",14:"Cedritos",17:"Colina",23:"Engativá Occidental",110:"Quinta Camacho",801:"Prado Veraniego",12:"Turbo Polo",19:"Iserra 100",50:"San Patricio",58:"Suba Turingia",67:"Barrancas",78:"Chilacos",9:"Chicó",28:"Granada Norte",33:"La Cabaña",51:"Usaquén",60:"Verbenal",70:"Titán",84:"Cañaveral",106:"Ibagué",107:"Cabecera",109:"Villavicencio",113:"El Rosal"},
    "MX":{105:"Avante",210:"San Mike",217:"Lindavista",353:"Granjas",443:"Toreo",804:"Narvarte",53:"Fidel",63:"Jardines de la Patria",71:"Paseo del Sol",263:"Tapatía",354:"Sauz",402:"Solares",403:"Zapopan",800:"Bugambilias",96:"Duraznos",206:"El Rosario",264:"San Ramon",392:"Bosque Real",409:"Portillo",801:"Bosques",49:"Altavista",52:"Leones",184:"San Pedro",400:"Calete",406:"Encinas",413:"República",417:"Valle Oriente",320:"Roma Norte",332:"Toriello Guerra",389:"Manitoba",445:"La Raza",143:"Interlomas",207:"Santa Fe",218:"Huicholes",310:"Las Águilas",446:"Atizapan",89:"Portales Norte",110:"Zedec",152:"Florida",336:"Campestre",376:"Cholula",378:"La Paz MX",379:"Lomas",380:"Angelópolis",396:"Constituyentes",397:"Arcos",247:"Carso",327:"Frida",434:"Parque Lira",129:"Ángel de Independencia",253:"Ajusco",265:"Tlalpan",268:"Fuentes del Pedregal",270:"San Ángel",430:"Turbo Oasis"},
    "PE":{7:"Bellavista Callao",24:"Juan Valer",42:"Alfredo Mendiola",63:"Lince",65:"Benavides",1:"La Paz PE",5:"Rosa Toro",6:"Jorge Chávez",9:"Tahiti",3:"Primavera",8:"Punta Hermosa",12:"Petit Thouars",14:"Angamos",56:"Machu Picchu",4:"Sucre",17:"Cataratas",18:"San Luis",62:"Sevilla",66:"Alfonso Ugarte",19:"Caminos del Inca",20:"Almirante Miguel Grau",2:"Los Jilgueros",21:"Cross Docking Belisario",40:"MFC Las Torres",800:"Santa Anita"},
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

[data-testid="stAppViewContainer"] { background: #F2F3F7 !important; }
[data-testid="stSidebar"]           { background: #FFFFFF !important; border-right: 1px solid #E5E7EB; }
[data-testid="stHeader"]            { background: #F2F3F7 !important; border-bottom: 1px solid #E5E7EB; }
.block-container                    { padding-top: 1.2rem !important; max-width: 1400px; }

/* Sidebar */
[data-testid="stSidebar"] .stSelectbox label { font-size: 0.7rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 1px; color: #9CA3AF !important; }
[data-testid="stSidebar"] h2 { font-size: 0.85rem !important; font-weight: 700 !important; color: #111827 !important; text-transform: uppercase; letter-spacing: 1px; }

/* Header bar */
.top-bar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px;
}
.brand { display: flex; align-items: center; gap: 10px; }
.brand-name { font-size: 1.3rem; font-weight: 900; color: #111827; letter-spacing: -0.5px; }
.brand-name span { color: #E8192C; }
.brand-tag {
    background: #FEF2F2; color: #E8192C;
    border: 1px solid #FECACA;
    border-radius: 20px; padding: 3px 12px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.5px;
}
.sync-dot { width: 8px; height: 8px; background: #22C55E; border-radius: 50%; display: inline-block; margin-right: 6px; }
.sync-label { font-size: 0.78rem; color: #6B7280; font-weight: 500; }

/* KPI Cards - TurboOps style */
.kpi-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 20px 22px;
    border: 1px solid #E5E7EB;
    border-top: 4px solid;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 4px;
}
.kpi-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; color: #9CA3AF; margin-bottom: 8px; }
.kpi-value { font-size: 2.4rem; font-weight: 900; color: #111827; line-height: 1; margin-bottom: 6px; }
.kpi-sub   { font-size: 0.75rem; color: #9CA3AF; }

/* Country summary cards */
.country-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 16px 18px;
    border: 1px solid #E5E7EB;
    border-left: 5px solid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    margin-bottom: 10px;
}
.country-card-title { font-size: 0.85rem; font-weight: 700; color: #111827; margin-bottom: 10px; }
.cc-stat { display: inline-block; margin-right: 18px; }
.cc-stat-val { font-size: 1.4rem; font-weight: 800; color: #111827; }
.cc-stat-lbl { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; color: #9CA3AF; display: block; }
.prog-bar-bg { background: #F3F4F6; border-radius: 4px; height: 6px; margin-top: 10px; }
.prog-bar-fill { height: 6px; border-radius: 4px; background: #22C55E; }

/* Pills */
.pill-fin { background: #DCFCE7; color: #16A34A; border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 700; }
.pill-pen { background: #FEF2F2; color: #E8192C;  border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 700; }
.pill-oth { background: #F3F4F6; color: #6B7280;  border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 700; }

/* Section headers */
.section-title { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #9CA3AF; margin: 18px 0 10px; }

/* Table styling */
[data-testid="stDataFrame"] { border-radius: 12px !important; border: 1px solid #E5E7EB !important; box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important; }
[data-testid="stDataFrame"] th { background: #F9FAFB !important; color: #6B7280 !important; font-size: 0.7rem !important; text-transform: uppercase; letter-spacing: 1px; font-weight: 600 !important; }

/* Refresh button */
[data-testid="stButton"] > button {
    background: #FFFFFF !important; color: #374151 !important;
    border: 1px solid #D1D5DB !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 0.8rem !important;
    padding: 6px 16px !important;
}
[data-testid="stButton"] > button:hover { border-color: #E8192C !important; color: #E8192C !important; }

div[data-testid="metric-container"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── FETCH ─────────────────────────────────────────────────────────────────────
def fetch_country(country, config):
    headers = {"Authorization": f"Key {config['key']}", "Content-Type": "application/json"}
    post_url = f"{REDASH_BASE}/api/queries/{config['id']}/results"
    try:
        r = requests.post(post_url, headers=headers, json={}, timeout=60)
        r.raise_for_status()
        data = r.json()
        if "query_result" in data:
            rows = data["query_result"]["data"]["rows"]
            df = pd.DataFrame(rows)
            if not df.empty: df["country"] = country
            return country, df, None
        if "job" in data:
            job_id = data["job"]["id"]
            for _ in range(30):
                time.sleep(1)
                jr = requests.get(f"{REDASH_BASE}/api/jobs/{job_id}", headers=headers, timeout=15).json()
                job = jr.get("job", {})
                if job.get("status") == 3:
                    result_id = job["query_result_id"]
                    rr = requests.get(f"{REDASH_BASE}/api/query_results/{result_id}.json", headers=headers, timeout=15)
                    rows = rr.json()["query_result"]["data"]["rows"]
                    df = pd.DataFrame(rows)
                    if not df.empty: df["country"] = country
                    return country, df, None
                if job.get("status") == 4:
                    return country, pd.DataFrame(), job.get("error", "Job failed")
            return country, pd.DataFrame(), "Timeout"
        return country, pd.DataFrame(), f"Respuesta inesperada: {str(data)[:150]}"
    except Exception as e:
        return country, pd.DataFrame(), str(e)

@st.cache_data(ttl=300)
def load_all():
    results, errors = {}, {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(fetch_country, c, cfg): c for c, cfg in QUERIES.items()}
        for f in concurrent.futures.as_completed(futures):
            country, df, err = f.result()
            if err: errors[country] = err
            else:   results[country] = df
    dfs = [df for df in results.values() if not df.empty]
    combined = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    return combined, errors

# ── TOP BAR ───────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%H:%M")
col_brand, col_right = st.columns([3, 1])
with col_brand:
    st.markdown(f"""
    <div class="top-bar">
      <div class="brand">
        <div class="brand-name">⚽ Panini<span>Ops</span></div>
        <span class="brand-tag">PRE-MUNDIAL 2026</span>
        <span class="brand-tag" style="background:#F0FFF4;color:#16A34A;border-color:#BBF7D0">CYCLIC COUNTS</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
with col_right:
    col_dot, col_btn = st.columns([2, 1])
    with col_dot:
        st.markdown(f'<div style="text-align:right;padding-top:8px"><span class="sync-dot"></span><span class="sync-label">Actualizado {now_str}</span></div>', unsafe_allow_html=True)
    with col_btn:
        if st.button("↺ Refrescar"):
            st.cache_data.clear()
            st.rerun()

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("Consultando Redash..."):
    df_all, errors = load_all()

for country, err in errors.items():
    st.warning(f"{FLAGS.get(country,country)} **{country}** — {err}")

if df_all.empty:
    st.info("Sin datos disponibles. Verifica las queries en Redash.")
    st.stop()

# ── NORMALIZE ─────────────────────────────────────────────────────────────────
df_all.columns = [c.lower() for c in df_all.columns]
def safe_int(v):
    try: return int(float(v))
    except: return None

df_all["store_reference_id"] = df_all["store_reference_id"].apply(safe_int)
df_all["warehouse_id"]        = df_all["warehouse_id"].apply(safe_int)
df_all["difference"]          = pd.to_numeric(df_all.get("difference",   0), errors="coerce").fillna(0)
df_all["total_missions"]      = pd.to_numeric(df_all.get("total_missions",0), errors="coerce").fillna(0)
df_all["total_quantity"]      = pd.to_numeric(df_all.get("total_quantity",0), errors="coerce").fillna(0)
df_all["vivo_stock"]          = pd.to_numeric(df_all.get("vivo_stock",   0), errors="coerce").fillna(0)
df_all["product_name"]   = df_all["store_reference_id"].apply(lambda x: PRODUCTS.get(x, f"ID {x}"))
df_all["warehouse_name"] = df_all.apply(lambda r: WAREHOUSES.get(r["country"],{}).get(r["warehouse_id"], f"WH {r['warehouse_id']}"), axis=1)
df_all["flag"]           = df_all["country"].map(FLAGS).fillna("🌐")
df_all["status_name"]    = df_all.get("status_name", pd.Series(["—"]*len(df_all)))

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filtros")
    sel_country   = st.selectbox("🌎 País",     ["Todos"] + sorted(df_all["country"].unique().tolist()))
    sel_status    = st.selectbox("📋 Estado",   ["Todos","FINALIZED","PENDING","OTHER"])
    sel_product   = st.selectbox("📦 Producto", ["Todos"] + sorted(df_all["product_name"].unique().tolist()))
    sel_warehouse = st.selectbox("🏪 Bodega",   ["Todos"] + sorted(df_all["warehouse_name"].unique().tolist()))
    st.markdown("---")
    st.caption(f"Cache 5 min · {datetime.now().strftime('%H:%M:%S')}")

df_f = df_all.copy()
if sel_country   != "Todos": df_f = df_f[df_f["country"]       == sel_country]
if sel_status    != "Todos": df_f = df_f[df_f["status_name"]   == sel_status]
if sel_product   != "Todos": df_f = df_f[df_f["product_name"]  == sel_product]
if sel_warehouse != "Todos": df_f = df_f[df_f["warehouse_name"]== sel_warehouse]

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
total      = len(df_f)
finalized  = int((df_f["status_name"]=="FINALIZED").sum())
pending    = int((df_f["status_name"]=="PENDING").sum())
units_gap  = int(df_f["difference"].sum())
pct_done   = round(finalized / total * 100, 1) if total else 0

st.markdown('<div class="section-title">Resumen del día</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)

def kpi_html(label, value, sub, color):
    return f"""<div class="kpi-card" style="border-top-color:{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""

with c1: st.markdown(kpi_html("Países activos",   df_f["country"].nunique(),           "con misiones hoy",     "#74AADB"), unsafe_allow_html=True)
with c2: st.markdown(kpi_html("Total misiones",   total,                               "del día",              "#6366F1"), unsafe_allow_html=True)
with c3: st.markdown(kpi_html("Finalizadas ✅",   finalized,                           f"{pct_done}% completo","#22C55E"), unsafe_allow_html=True)
with c4: st.markdown(kpi_html("Pendientes ⏳",    pending,                             "sin realizar",         "#E8192C"), unsafe_allow_html=True)
with c5: st.markdown(kpi_html("Units Gap 📦",     f"{units_gap:,}",                   "unidades con diferencia","#F59E0B"), unsafe_allow_html=True)

# ── COUNTRY CARDS ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Por país</div>', unsafe_allow_html=True)

countries_active = sorted(df_f["country"].unique().tolist())
cols_per_row = 3
rows = [countries_active[i:i+cols_per_row] for i in range(0, len(countries_active), cols_per_row)]

for row in rows:
    cols = st.columns(cols_per_row)
    for i, country in enumerate(row):
        df_c   = df_f[df_f["country"] == country]
        total_c = len(df_c)
        fin_c   = int((df_c["status_name"]=="FINALIZED").sum())
        pen_c   = int((df_c["status_name"]=="PENDING").sum())
        gap_c   = int(df_c["difference"].sum())
        pct_c   = round(fin_c/total_c*100,1) if total_c else 0
        color   = COUNTRY_COLORS.get(country, "#6B7280")
        flag    = FLAGS.get(country,"🌐")
        with cols[i]:
            st.markdown(f"""
            <div class="country-card" style="border-left-color:{color}">
                <div class="country-card-title">{flag} {country}</div>
                <div>
                    <div class="cc-stat"><span class="cc-stat-val">{total_c}</span><span class="cc-stat-lbl">Total</span></div>
                    <div class="cc-stat"><span class="cc-stat-val" style="color:#16A34A">{fin_c}</span><span class="cc-stat-lbl">Finalizadas</span></div>
                    <div class="cc-stat"><span class="cc-stat-val" style="color:#E8192C">{pen_c}</span><span class="cc-stat-lbl">Pendientes</span></div>
                    <div class="cc-stat"><span class="cc-stat-val" style="color:#F59E0B">{gap_c:,}</span><span class="cc-stat-lbl">Units Gap</span></div>
                </div>
                <div class="prog-bar-bg"><div class="prog-bar-fill" style="width:{pct_c}%;background:{color}"></div></div>
                <div style="text-align:right;font-size:0.68rem;color:#9CA3AF;margin-top:4px">{pct_c}% completado</div>
            </div>
            """, unsafe_allow_html=True)

# ── DETAIL TABLE ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Detalle por misión</div>', unsafe_allow_html=True)

col_map = {
    "flag":"🌎","country":"País","warehouse_name":"Bodega","warehouse_id":"WH ID",
    "product_name":"Producto","store_reference_id":"Sync ID","picker_name":"Picker",
    "status_name":"Estado","total_missions":"Misiones","total_quantity":"Cantidad",
    "vivo_stock":"Stock Vivo","difference":"Diferencia",
}
started_col = "started_at_local" if "started_at_local" in df_f.columns else "started_at"
col_map[started_col] = "Inicio"

show_cols = [c for c in col_map if c in df_f.columns]
df_show   = df_f[show_cols].rename(columns=col_map).copy()

def style_row(row):
    styles = [""] * len(row)
    cols   = list(row.index)
    if "Estado" in cols:
        i = cols.index("Estado")
        if row["Estado"] == "FINALIZED": styles[i] = "color:#16A34A;font-weight:700"
        elif row["Estado"] == "PENDING": styles[i] = "color:#E8192C;font-weight:700"
    if "Diferencia" in cols:
        i = cols.index("Diferencia")
        try:
            v = float(row["Diferencia"])
            if   v > 50: styles[i] = "color:#E8192C;font-weight:700"
            elif v > 0:  styles[i] = "color:#F59E0B;font-weight:600"
            elif v < 0:  styles[i] = "color:#6366F1"
            else:        styles[i] = "color:#9CA3AF"
        except: pass
    return styles

styled = df_show.style.apply(style_row, axis=1)
st.dataframe(styled, use_container_width=True, height=480, hide_index=True)

st.caption(f"⚽ Panini · Pre-Mundial 2026 · {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} · Cache 5 min")
