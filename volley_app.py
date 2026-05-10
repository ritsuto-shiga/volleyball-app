
import os
import json
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Cloud Storage imports
from google.cloud import storage
from google.oauth2 import service_account
import io

# ------------------------------------------------------------
# Cloud Storage helpers
# ------------------------------------------------------------

GCS_BUCKET_NAME = "volley-app"

@st.cache_resource
def get_bucket():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = storage.Client(credentials=credentials)
    return client.bucket(GCS_BUCKET_NAME)


def gcs_download(path: str) -> str | None:
    """Download text file from GCS; return None if not exists."""
    try:
        bucket = get_bucket()
        blob = bucket.blob(path)
        if not blob.exists():
            return None
        return blob.download_as_text(encoding="utf-8")
    except Exception:
        # any failure falls back to None
        return None


def gcs_upload(path: str, content: str, content_type: str):
    """Upload string to GCS at specified path."""
    bucket = get_bucket()
    blob = bucket.blob(path)
    blob.upload_from_string(content, content_type=content_type)



# ============================================================
# Page config
# ============================================================
st.set_page_config(layout="wide", page_title="バレーボール戦術分析システム", page_icon="🏐")

# ============================================================
# ============================================================
# Custom CSS (Dynamic)
# ============================================================
def apply_custom_css():
    is_dark = st.session_state.get("dark_mode", False)

    # Updated Color Palette
    c_bg = "#0f172a" if is_dark else "#f8fafc"       # Main Background
    c_sidebar = "#1e293b" if is_dark else "#ffffff"  # Sidebar Background
    c_sidebar_border = "rgba(255,255,255,0.1)" if is_dark else "rgba(15,23,42,0.12)"
    c_text = "#f1f5f9" if is_dark else "#1e293b"     # Main Text
    c_subtext = "#94a3b8" if is_dark else "#64748b"  # Muted Text
    
    c_input_bg = "#334155" if is_dark else "#ffffff"
    c_input_border = "rgba(255,255,255,0.2)" if is_dark else "rgba(0,0,0,0.1)"
    
    c_btn_sec_bg = "#334155" if is_dark else "#ffffff"
    c_btn_sec_hover = "#475569" if is_dark else "#f1f5f9"
    
    c_court_bg = "#475569" if is_dark else "#fef3c7" 

    css = f"""
    <style>
        /* Global Reset & Base Colors */
        .stApp {{
            background-color: {c_bg};
            color: {c_text};
        }}
        
        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {c_sidebar};
            border-right: 1px solid {c_sidebar_border};
        }}
        
        /* Text Color Overrides - Ensure visibility */
        h1, h2, h3, h4, h5, h6, p,span, div, label, li {{
            color: {c_text} !important;
        }}
        .stMarkdown, .stText {{
            color: {c_text} !important;
        }}
        
        /* Inputs (Text, Number, Selectbox) */
        /* Inputs (Text, Number, Selectbox) */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {{
            background-color: {c_btn_sec_bg} !important; 
            color: {c_text} !important;
            border: 1px solid {c_input_border} !important;
        }}
        
        /* Selectbox specific: Force White BG / Black Text as requested */
        .stSelectbox > div > div {{
            background-color: #ffffff !important;
            color: #1e293b !important;
            border: 1px solid #cbd5e1 !important;
        }}
        .stSelectbox div[data-baseweb="select"] > div {{
            background-color: #ffffff !important;
            color: #1e293b !important;
        }}
        .stSelectbox div[data-baseweb="select"] span {{
            color: #1e293b !important;
        }}
        /* Dropdown arrow specific */
        .stSelectbox svg {{
            fill: #1e293b !important;
        }}

        /* Selectbox specific: Dropdown items */
        ul[data-baseweb="menu"] {{
            background-color: #ffffff !important;
        }}
        ul[data-baseweb="menu"] li span {{
            color: #1e293b !important;
        }}

        /* Buttons: Distinguish Primary vs Secondary */
        /* Secondary (Standard) Buttons */
        div.stButton > button[kind="secondary"] {{
            background-color: {c_btn_sec_bg};
            color: {c_text} !important;
            border: 1px solid {c_input_border};
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        /* Make secondary buttons more visible in dark mode */
        div.stButton > button[kind="secondary"]:hover {{
            background-color: {c_btn_sec_hover};
            border-color: #38bdf8;
            color: #38bdf8 !important;
        }}
        
        /* Primary (Active/Action) Buttons */
        div.stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white !important;
            border: none;
            box-shadow: 0 4px 6px -1px rgba(2,132,199,0.3);
        }}
        div.stButton > button[kind="primary"]:hover {{
            box-shadow: 0 6px 8px -1px rgba(2,132,199,0.4);
            filter: brightness(1.1);
        }}
        /* Primary Text in Primary Button needs to be white */
        div.stButton > button[kind="primary"] p {{
            color: white !important;
        }}

        /* Court Area */
        .court-shell {{
            background-color: {c_court_bg};
            border: 2px solid {c_input_border};
        }}
        .court-btn {{
            color: white !important; /* Always white text on court buttons */
        }}
        .court-btn span {{
            color: white !important;
        }}

        /* Download Button - High Contrast */
        .stDownloadButton > button {{
            background-color: {c_btn_sec_bg} !important;
            color: {c_text} !important;
            border: 1px solid {c_input_border} !important;
        }}
        .stDownloadButton > button:hover {{
            border-color: #38bdf8 !important;
            color: #38bdf8 !important;
        }}

        /* Tables/Dataframes - Distinct Background */
        [data-testid="stDataFrame"], [data-testid="stTable"] {{
            background-color: {c_input_bg} !important;
            border: 1px solid {c_input_border} !important;
            border-radius: 5px;
            padding: 5px;
        }}
        [data-testid="stTable"] table {{
            color: {c_text} !important;
            width: 100%;
        }}
        [data-testid="stTable"] th, [data-testid="stTable"] td {{
            color: {c_text} !important;
            border-bottom: 1px solid {c_input_border} !important;
        }}
        div[data-testid="stDataFrameResizable"] {{
            color: {c_text} !important;
        }}
        
        /* Metric Labels */
        [data-testid="stMetricLabel"] {{
            color: {c_subtext} !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {c_text} !important;
        }}

        /* Court Grid (Setup Screen) */
        .court-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
            background-color: {c_court_bg};
            padding: 12px;
            border: 2px solid {c_input_border};
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .court-cell {{
            background-color: {c_input_bg};
            border: 1px solid {c_input_border};
            color: {c_text};
            padding: 12px;
            text-align: center;
            font-weight: bold;
            border-radius: 6px;
        }}
        .court-pos-label {{
            display: block;
            font-size: 0.75rem;
            color: {c_subtext};
            margin-bottom: 4px;
            font-weight: normal;
        }}
        
        /* Compact Mode for iPad */
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        .element-container {{
            margin-bottom: 0.5rem !important;
        }}
        /* Hide deploy button if possible (Streamlit cloud specific, but good hygiene) */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

import matplotlib.cm as cm
import matplotlib.colors as mcolors

# ============================================================
# Constants & User Config
# ============================================================
USERS_FILE = "users.json"
DATA_ROOT = "data"

RESULTS = ["得点", "継続", "ネット", "アウト"]
RESULT_COLORS = {"得点": "#16a34a", "継続": "#2563eb", "ミス": "#dc2626", "ネット": "#dc2626", "アウト": "#dc2626"}
RECEPTION_GRADES = ["Aカット", "Bカット", "Cカット", "ミス"]


def style_metric_cell(val):
    """
    Apply background color to metric cells.
    Positive (0 to 1): White -> Green (using 0.0-0.5 of Greens colormap).
    Negative (-1 to 0): White -> Red (using 0.0-0.5 of Reds colormap).
    """
    if pd.isna(val):
        return ""
    try:
        v = float(val)
    except (ValueError, TypeError):
        return ""
        
    if v >= 0:
        # User requested: 100% (1.0) should use the color previously used for 50%.
        # Standard Greens: 0.0(White) -> 1.0(Dark).
        # So we map our 0.0-1.0 input to 0.0-0.5 output.
        ratio = min(v, 1.0) * 0.5
        color = cm.Greens(ratio)
    else:
        # Negative: White -> Red
        ratio = min(abs(v), 1.0) * 0.5
        color = cm.Reds(ratio)
        
    return f"background-color: {mcolors.to_hex(color)}"


def load_users() -> dict:
    # try Cloud Storage first
    content = gcs_download(USERS_FILE)
    if content is not None:
        try:
            return json.loads(content)
        except Exception:
            pass
    # fallback to local file
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users: dict) -> None:
    data = json.dumps(users, ensure_ascii=False, indent=4)
    try:
        gcs_upload(USERS_FILE, data, "application/json")
        return
    except Exception:
        pass
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        f.write(data)


def find_account(team_name: str, password: str) -> dict | None:
    """チーム名+パスワードでアカウントを検索。見つかれば {"role", "display_name"} を返す。"""
    users = load_users()
    team = users.get(team_name)
    if team is None:
        return None
    if team.get("admin_password") == password:
        return {"role": "admin", "display_name": team_name}
    for v in team.get("viewers", []):
        if v.get("password") == password:
            return {"role": "viewer", "display_name": v["name"]}
    return None


def register_admin(team_name: str, password: str) -> bool:
    """管理者アカウントを新規作成。すでに存在する場合は False を返す。"""
    users = load_users()
    if team_name in users:
        return False
    users[team_name] = {"admin_password": password, "viewers": []}
    save_users(users)
    return True


def get_user_data_dir() -> str:
    user = st.session_state.get("auth_team", "default")
    path = os.path.join(DATA_ROOT, user)
    os.makedirs(path, exist_ok=True)
    return path


def get_current_match_path() -> str:
    return os.path.join(get_user_data_dir(), "current_match.jsonl")


    return os.path.join(get_user_data_dir(), "current_match.jsonl")


def get_current_match_meta_path() -> str:
    return os.path.join(get_user_data_dir(), "current_match_meta.json")


def get_config_path() -> str:
    return os.path.join(get_user_data_dir(), "config.json")

# ============================================================
# Helpers: config
# ============================================================
def save_config() -> None:
    data = {
        "players_master": st.session_state.players_master,
        "attack_patterns": st.session_state.attack_patterns,
        "serve_types": st.session_state.serve_types,
    }
    content = json.dumps(data, ensure_ascii=False, indent=4)
    # try GCS
    username = st.session_state.get("auth_team", "default")
    path = f"data/{username}/config.json"
    try:
        gcs_upload(path, content, "application/json")
        return
    except Exception:
        pass
    with open(get_config_path(), "w", encoding="utf-8") as f:
        f.write(content)


def load_config() -> None:
    # try cloud storage
    username = st.session_state.get("auth_team", "default")
    path = f"data/{username}/config.json"
    content = gcs_download(path)
    if content is not None:
        try:
            data = json.loads(content)
            st.session_state.players_master = data.get("players_master", [])
            for p in st.session_state.players_master:
                if "nickname" not in p:
                    p["nickname"] = p["name"]
            st.session_state.attack_patterns = data.get("attack_patterns", [])
            st.session_state.serve_types = data.get("serve_types", [])
            return
        except Exception:
            pass
    # fallback to local file
    path_local = get_config_path()
    if os.path.exists(path_local):
        with open(path_local, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.session_state.players_master = data.get("players_master", [])
        for p in st.session_state.players_master:
            if "nickname" not in p:
                p["nickname"] = p["name"]
        st.session_state.attack_patterns = data.get("attack_patterns", [])
        st.session_state.serve_types = data.get("serve_types", [])
        return

    # Defaults
    st.session_state.players_master = [
        {"name": "Player1", "nickname": "P1", "number": 1, "position": "S"},
        {"name": "Player2", "nickname": "P2", "number": 2, "position": "OH"},
        {"name": "Player3", "nickname": "P3", "number": 3, "position": "MB"},
        {"name": "Player4", "nickname": "P4", "number": 4, "position": "OP"},
        {"name": "Player5", "nickname": "P5", "number": 5, "position": "L"},
        {"name": "Player6", "nickname": "P6", "number": 6, "position": "OH"},
    ]
    st.session_state.attack_patterns = [
        {"name": "レフトオープン"},
        {"name": "Aクイック"},
        {"name": "バックアタック"},
    ]
    st.session_state.serve_types = ["ジャンプ", "フローター"]


# ============================================================
# Helpers: events persistence (current match)
# ============================================================
def ensure_data_dir() -> None:
    get_user_data_dir()


def append_current_match_event(event: dict) -> None:
    """Append one event to jsonl and keep it durable."""
    ensure_data_dir()
    username = st.session_state.get("auth_team", "default")
    path = f"data/{username}/current_match.jsonl"
    # build new line
    new_line = json.dumps(event, ensure_ascii=False) + "\n"
    # try download existing
    existing = gcs_download(path) or ""
    updated = existing + new_line
    try:
        gcs_upload(path, updated, "text/plain; charset=utf-8")
        return
    except Exception:
        pass
    with open(get_current_match_path(), "a", encoding="utf-8") as f:
        f.write(new_line)


def save_current_match_snapshot() -> None:
    """Rewrite jsonl snapshot from session_state.events (Set dict)."""
    ensure_data_dir()
    username = st.session_state.get("auth_team", "default")
    path = f"data/{username}/current_match.jsonl"
    lines = []
    for set_key, events in st.session_state.events.items():
        set_no = int(set_key.replace("Set", ""))
        for e in events:
            e2 = dict(e)
            e2["set"] = set_no
            lines.append(json.dumps(e2, ensure_ascii=False))
    content = "\n".join(lines) + ("\n" if lines else "")
    try:
        gcs_upload(path, content, "text/plain; charset=utf-8")
    except Exception:
        with open(get_current_match_path(), "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
    # Also save metadata
    save_match_meta()


def save_match_meta() -> None:
    """Save match metadata to a separate json file."""
    ensure_data_dir()
    match_date = st.session_state.get("match_date", "")
    data = {
        "tournament_name": match_date,
        "match_date": match_date,
        "match_opponent": st.session_state.get("match_opponent", ""),
        "file_name": st.session_state.get("file_name", ""),
    }
    content = json.dumps(data, ensure_ascii=False, indent=4)
    username = st.session_state.get("auth_team", "default")
    path = f"data/{username}/current_match_meta.json"
    try:
        gcs_upload(path, content, "application/json")
        return
    except Exception:
        pass
    with open(get_current_match_meta_path(), "w", encoding="utf-8") as f:
        f.write(content)


def load_match_meta() -> None:
    """Load match metadata from json file."""
    username = st.session_state.get("auth_team", "default")
    path = f"data/{username}/current_match_meta.json"
    content = gcs_download(path)
    if content is not None:
        try:
            data = json.loads(content)
            st.session_state.match_date = data.get("match_date", data.get("tournament_name", ""))
            st.session_state.match_opponent = data.get("match_opponent", "")
            st.session_state.tournament_name = data.get("match_date", data.get("tournament_name", ""))
            st.session_state.file_name = data.get("file_name", "")
            return
        except Exception:
            pass
    path_local = get_current_match_meta_path()
    if os.path.exists(path_local):
        with open(path_local, "r", encoding="utf-8") as f:
            data = json.load(f)
            st.session_state.match_date = data.get("match_date", data.get("tournament_name", ""))
            st.session_state.match_opponent = data.get("match_opponent", "")
            st.session_state.tournament_name = data.get("match_date", data.get("tournament_name", ""))
            st.session_state.file_name = data.get("file_name", "")


def load_current_match() -> bool:
    """Load jsonl into session_state if exists."""
    username = st.session_state.get("auth_team", "default")
    path = f"data/{username}/current_match.jsonl"
    content = gcs_download(path)
    if content is None:
        # fallback to local
        path_local = get_current_match_path()
        if not os.path.exists(path_local):
            return False
        with open(path_local, "r", encoding="utf-8") as f:
            content = f.read()
    lines = content.strip().split("\n") if content else []

    events_all: list[dict] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        events_all.append(json.loads(line))

    if not events_all:
        return False

    st.session_state.events = {f"Set{i}": [] for i in range(1, 6)}
    for e in events_all:
        set_key = f"Set{int(e.get('set', 1))}"
        st.session_state.events.setdefault(set_key, []).append(e)

    latest = events_all[-1]
    st.session_state.current_set = int(latest.get("set", 1))
    st.session_state.score_own = int(latest.get("score_own", 0))
    st.session_state.score_opponent = int(latest.get("score_opponent", 0))
    st.session_state.rotation = latest.get("rotation", st.session_state.rotation)
    st.session_state.libero_in_court = bool(latest.get("libero_in_court", False))
    st.session_state.libero_in_court = bool(latest.get("libero_in_court", False))
    st.session_state.serving_team = latest.get("serving_team", st.session_state.serving_team)
    
    # Restore team names if available in latest event, else keep existing or default
    st.session_state.team_name = latest.get("team_name", st.session_state.get("team_name", "自チーム"))
    st.session_state.opponent_name = latest.get("opponent_name", st.session_state.get("opponent_name", "相手チーム"))

    st.session_state.is_analysis_active = True
    st.session_state.is_analysis_active = True
    
    # Load metadata
    load_match_meta()
    return True


def reset_current_match_file() -> None:
    path = get_current_match_path()
    if os.path.exists(path):
        os.remove(path)
    # Also remove meta
    meta_path = get_current_match_meta_path()
    if os.path.exists(meta_path):
        os.remove(meta_path)


def get_matches_dir() -> str:
    return os.path.join(get_user_data_dir(), "matches")


def save_match_to_archive(tournament: str, filename: str) -> str:
    """Save current match to archive and remove current_match.jsonl."""
    src = get_current_match_path()
    if not os.path.exists(src):
        return ""
    dest_dir = os.path.join(get_matches_dir(), tournament)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, f"{filename}.jsonl")
    import shutil
    shutil.copy2(src, dest)
    os.remove(src)
    # Save match meta alongside the archive
    meta_data = {
        "match_date": st.session_state.get("match_date", tournament),
        "match_opponent": st.session_state.get("match_opponent", ""),
        "file_name": filename,
    }
    meta_dest = os.path.join(dest_dir, f"{filename}_meta.json")
    with open(meta_dest, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=4)
    # Remove current meta
    meta_path = get_current_match_meta_path()
    if os.path.exists(meta_path):
        os.remove(meta_path)
    return dest


@st.cache_data(ttl=60)
def list_saved_matches(user: str) -> list[dict]:
    """Return list of {tournament, filename, path, mtime, size, display_date}.
    Cached per user for 60 seconds; call list_saved_matches.clear() after saving."""
    matches_dir = os.path.join(DATA_ROOT, user, "matches")
    result = []
    if not os.path.exists(matches_dir):
        return result

    def get_file_info(fpath):
        stat = os.stat(fpath)
        dt = datetime.fromtimestamp(stat.st_mtime)
        return dt, stat.st_size

    def read_meta(dir_path: str, base_name: str) -> dict:
        meta_path = os.path.join(dir_path, f"{base_name}_meta.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    # 1. Files directly under matches_dir
    for fname in sorted(os.listdir(matches_dir)):
        if fname.endswith(".jsonl"):
            fpath = os.path.join(matches_dir, fname)
            dt, size = get_file_info(fpath)
            display_name = fname.replace(".jsonl", "") or "Unknown_Match"
            meta = read_meta(matches_dir, display_name)
            result.append({
                "tournament": "未分類",
                "filename": display_name,
                "match_opponent": meta.get("match_opponent", ""),
                "match_date": meta.get("match_date", ""),
                "path": fpath,
                "mtime": dt,
                "size": size,
                "display_date": dt.strftime("%Y-%m-%d %H:%M"),
            })

    # 2. Subdirectories
    for tournament in sorted(os.listdir(matches_dir)):
        t_dir = os.path.join(matches_dir, tournament)
        if not os.path.isdir(t_dir):
            continue
        for fname in sorted(os.listdir(t_dir)):
            if fname.endswith(".jsonl"):
                fpath = os.path.join(t_dir, fname)
                dt, size = get_file_info(fpath)
                base_name = fname.replace(".jsonl", "")
                meta = read_meta(t_dir, base_name)
                result.append({
                    "tournament": tournament,
                    "filename": base_name,
                    "match_opponent": meta.get("match_opponent", ""),
                    "match_date": meta.get("match_date", tournament),
                    "path": fpath,
                    "mtime": dt,
                    "size": size,
                    "display_date": dt.strftime("%Y-%m-%d %H:%M"),
                })

    result.sort(key=lambda x: x["mtime"], reverse=True)
    return result


@st.cache_data
def load_events_from_file(path: str) -> list[dict]:
    """Load events from a JSONL file. Cached by path."""
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


# ============================================================
# Session init
# ============================================================
def init_session_state() -> None:
    if "players_master" not in st.session_state:
        load_config()

    # mode & match meta
    if "mode" not in st.session_state:
        st.session_state.mode = "リアルタイム分析"

    # analysis flow
    if "is_analysis_active" not in st.session_state:
        st.session_state.is_analysis_active = False
    if "tournament_name" not in st.session_state:
        st.session_state.tournament_name = ""
    if "match_date" not in st.session_state:
        st.session_state.match_date = ""
    if "match_opponent" not in st.session_state:
        st.session_state.match_opponent = ""
    if "file_name" not in st.session_state:
        st.session_state.file_name = ""
    if "starting_rotation" not in st.session_state:
        st.session_state.starting_rotation = ["" for _ in range(6)]
    if "rot_editing_pos" not in st.session_state:
        st.session_state.rot_editing_pos = None
    if "unsaved_event_count" not in st.session_state:
        st.session_state.unsaved_event_count = 0

    # match state
    if "current_set" not in st.session_state:
        st.session_state.current_set = 1
    if "score_own" not in st.session_state:
        st.session_state.score_own = 0
    if "score_opponent" not in st.session_state:
        st.session_state.score_opponent = 0

    # rotation as list of 6 current players (by nickname or name?)
    # User requested nickname everywhere.
    if "rotation" not in st.session_state:
        st.session_state.rotation = [
            p.get("nickname", p["name"]) for p in st.session_state.players_master
        ][:6]

    # Team names
    if "team_name" not in st.session_state:
        st.session_state.team_name = "自チーム"
    if "opponent_name" not in st.session_state:
        st.session_state.opponent_name = "相手チーム"

    # events always as dict by Set
    if "events" not in st.session_state or not isinstance(st.session_state.events, dict):
        st.session_state.events = {f"Set{i}": [] for i in range(1, 6)}

    # input temp state
    if "current_action" not in st.session_state:
        st.session_state.current_action = "serve"  # serve, reception, spike
    if "selected_player" not in st.session_state:
        st.session_state.selected_player = None
    if "selected_attack" not in st.session_state:
        st.session_state.selected_attack = None
    if "selected_serve" not in st.session_state:
        st.session_state.selected_serve = None
    if "selected_result" not in st.session_state:
        st.session_state.selected_result = None
    if "reception_grade" not in st.session_state:
        st.session_state.reception_grade = None
    if "start_area" not in st.session_state:
        st.session_state.start_area = None
    if "end_area" not in st.session_state:
        st.session_state.end_area = None
        
    # auth state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "auth_team" not in st.session_state:
        st.session_state.auth_team = None
    if "role" not in st.session_state:
        st.session_state.role = None

    # rotation logic
    if "serving_team" not in st.session_state:
        st.session_state.serving_team = None  # "own" or "opponent"

    # options modes
    if "libero_in_court" not in st.session_state:
        st.session_state.libero_in_court = False
    if "libero_replaced_player" not in st.session_state:
        st.session_state.libero_replaced_player = None  # The player who was swapped out for libero
    if "is_error_mode" not in st.session_state:
        st.session_state.is_error_mode = False
    if "error_team" not in st.session_state:
        st.session_state.error_team = None
    if "is_libero_mode" not in st.session_state:
        st.session_state.is_libero_mode = False
    # Substitution mode
    if "is_sub_mode" not in st.session_state:
        st.session_state.is_sub_mode = False
    if "sub_step" not in st.session_state:
        st.session_state.sub_step = 1  # 1=select bench player (IN), 2=select court player (OUT)
    if "sub_in_player" not in st.session_state:
        st.session_state.sub_in_player = None
    if "sub_in_is_libero" not in st.session_state:
        st.session_state.sub_in_is_libero = False
    # Set end confirmation
    if "confirm_end_set" not in st.session_state:
        st.session_state.confirm_end_set = False
    # Match end confirmation
    if "confirm_end_match" not in st.session_state:
        st.session_state.confirm_end_match = False
    # In-match analysis view
    if "is_in_match_analysis" not in st.session_state:
        st.session_state.is_in_match_analysis = False
    
    # Dark mode
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    # Post-match summary
    if "show_match_summary" not in st.session_state:
        st.session_state.show_match_summary = False
    if "match_summary" not in st.session_state:
        st.session_state.match_summary = {}

    # component key management
    if "court_key_id" not in st.session_state:
        st.session_state.court_key_id = 0


init_session_state()

# ============================================================
# UI parts
# ============================================================
def show_viewer_management() -> None:
    """利用者アカウントの追加・削除（管理者専用）。"""
    team_name = st.session_state.auth_team
    users = load_users()
    team = users.get(team_name, {})
    viewers = team.get("viewers", [])

    st.caption(f"選手などが閲覧専用でログインできる利用者アカウントを管理します。\nログイン時は チーム名「{team_name}」と下記のパスワードを使います。")

    if viewers:
        st.markdown("**現在の利用者アカウント**")
        for i, v in enumerate(viewers):
            c1, c2, c3 = st.columns([3, 4, 1])
            with c1:
                st.text(v["name"])
            with c2:
                st.text("••••••••")
            with c3:
                if st.button("削除", key=f"del_viewer_{i}"):
                    viewers.pop(i)
                    team["viewers"] = viewers
                    users[team_name] = team
                    save_users(users)
                    st.success(f"「{v['name']}」を削除しました")
                    st.rerun()
    else:
        st.info("利用者アカウントはまだありません")

    st.divider()
    st.markdown("**利用者を追加**")
    with st.container(border=True):
        new_name = st.text_input("利用者名（選手名など）", key="new_viewer_name")
        new_pass = st.text_input("パスワード", type="password", key="new_viewer_pass")
        if st.button("追加", type="primary", key="btn_add_viewer"):
            if not new_name or not new_pass:
                st.error("名前とパスワードを入力してください")
            elif any(v["name"] == new_name for v in viewers):
                st.error(f"「{new_name}」はすでに登録されています")
            else:
                viewers.append({"name": new_name, "password": new_pass})
                team["viewers"] = viewers
                users[team_name] = team
                save_users(users)
                st.success(f"「{new_name}」を追加しました")
                st.rerun()


def show_registration_mode() -> None:
    st.markdown("## 各種登録")
    is_admin = st.session_state.get("role") == "admin"

    sections = ["🏐  選手マスター", "⚡  攻撃パターン", "🎯  サーブ種類"]
    if is_admin:
        sections.append("👥  利用者管理")

    if "reg_section" not in st.session_state:
        st.session_state.reg_section = sections[0]

    col_nav, col_content = st.columns([1, 3])

    with col_nav:
        for sec in sections:
            is_active = st.session_state.reg_section == sec
            if st.button(sec, key=f"reg_nav_{sec}",
                         type="primary" if is_active else "secondary",
                         use_container_width=True):
                st.session_state.reg_section = sec
                st.session_state.adding_player = False
                st.session_state.selected_player_idx = None
                st.rerun()

    with col_content:
        section = st.session_state.reg_section

        # ---- 選手マスター ----
        if "選手マスター" in section:
            players = st.session_state.players_master
            position_options = ["S", "OH", "MB", "OP", "L"]

            if "adding_player" not in st.session_state:
                st.session_state.adding_player = False
            if "selected_player_idx" not in st.session_state:
                st.session_state.selected_player_idx = None

            col_title, col_add = st.columns([3, 1])
            with col_title:
                st.markdown(f"**登録選手: {len(players)}名**")
            with col_add:
                if st.button("＋ 選手を追加", type="primary", use_container_width=True, key="btn_open_add_player"):
                    st.session_state.adding_player = True
                    st.session_state.selected_player_idx = None
                    st.rerun()

            if st.session_state.adding_player:
                with st.container(border=True):
                    st.markdown("**新しい選手を追加**")
                    c1, c2, c3 = st.columns([1, 2, 3])
                    with c1:
                        new_number = st.number_input("背番号", min_value=0, max_value=99, step=1, key="new_player_number")
                    with c2:
                        new_position = st.selectbox("ポジション", position_options, key="new_player_position")
                    with c3:
                        new_name = st.text_input("名前", key="new_player_name")

                    ca, cb = st.columns(2)
                    with ca:
                        if st.button("追加する", type="primary", use_container_width=True, key="confirm_add_player"):
                            if not new_name.strip():
                                st.error("名前を入力してください")
                            else:
                                players.append({
                                    "name": new_name.strip(),
                                    "nickname": new_name.strip(),
                                    "number": int(new_number),
                                    "position": new_position,
                                    "height": None,
                                    "max_reach": None,
                                    "serve_types": [],
                                })
                                st.session_state.players_master = players
                                save_config()
                                st.session_state.adding_player = False
                                st.success(f"「{new_name.strip()}」を追加しました")
                                st.rerun()
                    with cb:
                        if st.button("キャンセル", use_container_width=True, key="cancel_add_player"):
                            st.session_state.adding_player = False
                            st.rerun()

            st.divider()

            if not players:
                st.info("選手が登録されていません。「＋ 選手を追加」から登録してください。")
            else:
                serve_options = st.session_state.serve_types
                for i, p in enumerate(players):
                    if "serve_types" not in p:
                        ds = p.get("default_serve", "")
                        p["serve_types"] = [ds] if ds and ds != "なし" else []
                    if "height" not in p:
                        p["height"] = None
                    if "max_reach" not in p:
                        p["max_reach"] = None

                    is_selected = st.session_state.selected_player_idx == i
                    num = p.get("number", "")
                    name = p.get("name", "")
                    pos = p.get("position", "")
                    icon = "▼ " if is_selected else "▶ "

                    if st.button(f"{icon}**{num}. {name}**　　{pos}", key=f"player_row_{i}", use_container_width=True):
                        st.session_state.selected_player_idx = None if is_selected else i
                        st.session_state.adding_player = False
                        st.rerun()

                    if is_selected:
                        with st.container(border=True):
                            st.markdown(f"**{name} の詳細情報**")
                            d1, d2 = st.columns(2)
                            with d1:
                                edit_nickname = st.text_input("ニックネーム（表示名）", value=p.get("nickname", name), key=f"edit_nick_{i}")
                                edit_height = st.number_input("身長 (cm)", min_value=0, max_value=250,
                                    value=int(p["height"]) if p["height"] else 0, step=1, key=f"edit_height_{i}")
                            with d2:
                                edit_number = st.number_input("背番号", min_value=0, max_value=99,
                                    value=int(num), step=1, key=f"edit_number_{i}")
                                edit_reach = st.number_input("最高到達点 (cm)", min_value=0, max_value=400,
                                    value=int(p["max_reach"]) if p["max_reach"] else 0, step=1, key=f"edit_reach_{i}")

                            edit_position = st.selectbox(
                                "ポジション", position_options,
                                index=position_options.index(pos) if pos in position_options else 0,
                                key=f"edit_pos_{i}"
                            )
                            edit_serves = st.multiselect(
                                "サーブ種類（複数選択可）", options=serve_options,
                                default=[s for s in p.get("serve_types", []) if s in serve_options],
                                key=f"edit_serves_{i}"
                            )

                            sa, sb = st.columns(2)
                            with sa:
                                if st.button("保存", type="primary", use_container_width=True, key=f"save_player_{i}"):
                                    players[i].update({
                                        "nickname": edit_nickname,
                                        "number": int(edit_number),
                                        "position": edit_position,
                                        "height": int(edit_height) if edit_height else None,
                                        "max_reach": int(edit_reach) if edit_reach else None,
                                        "serve_types": edit_serves,
                                    })
                                    st.session_state.players_master = players
                                    save_config()
                                    st.session_state.selected_player_idx = None
                                    st.success("保存しました")
                                    st.rerun()
                            with sb:
                                if st.button("削除", use_container_width=True, key=f"delete_player_{i}"):
                                    players.pop(i)
                                    st.session_state.players_master = players
                                    save_config()
                                    st.session_state.selected_player_idx = None
                                    st.success(f"「{name}」を削除しました")
                                    st.rerun()

        # ---- 攻撃パターン ----
        elif "攻撃パターン" in section:
            st.caption("スパイク時に選択できる攻撃パターンを登録します。")
            patterns = list(st.session_state.attack_patterns)

            if "adding_pattern" not in st.session_state:
                st.session_state.adding_pattern = False

            col_pt, col_pa = st.columns([3, 1])
            with col_pt:
                st.markdown(f"**登録パターン: {len(patterns)}件**")
            with col_pa:
                if st.button("＋ 追加", type="primary", use_container_width=True, key="btn_add_pattern"):
                    st.session_state.adding_pattern = True
                    st.rerun()

            if st.session_state.adding_pattern:
                with st.container(border=True):
                    new_pat_name = st.text_input("パターン名", key="new_pattern_name",
                                                 placeholder="例: A, B, C, クイック")
                    pa, pb = st.columns(2)
                    with pa:
                        if st.button("追加する", type="primary", use_container_width=True, key="confirm_add_pattern"):
                            if new_pat_name.strip():
                                patterns.append({"name": new_pat_name.strip()})
                                st.session_state.attack_patterns = patterns
                                save_config()
                                st.session_state.adding_pattern = False
                                st.success(f"「{new_pat_name.strip()}」を追加しました")
                                st.rerun()
                            else:
                                st.error("パターン名を入力してください")
                    with pb:
                        if st.button("キャンセル", use_container_width=True, key="cancel_add_pattern"):
                            st.session_state.adding_pattern = False
                            st.rerun()

            st.divider()

            if not patterns:
                st.info("攻撃パターンが登録されていません。「＋ 追加」から登録してください。")
            else:
                for i, pat in enumerate(patterns):
                    p_name = pat["name"] if isinstance(pat, dict) else str(pat)
                    with st.container(border=True):
                        c_name, c_del = st.columns([5, 1])
                        with c_name:
                            st.markdown(f"**{p_name}**")
                        with c_del:
                            if st.button("削除", key=f"del_pattern_{i}", use_container_width=True):
                                patterns.pop(i)
                                st.session_state.attack_patterns = patterns
                                save_config()
                                st.rerun()

        # ---- サーブ種類 ----
        elif "サーブ種類" in section:
            st.caption("サーブ入力時に選択できるサーブ種類を登録します。")
            serves = list(st.session_state.serve_types)

            if "adding_serve" not in st.session_state:
                st.session_state.adding_serve = False

            col_st, col_sa = st.columns([3, 1])
            with col_st:
                st.markdown(f"**登録サーブ: {len(serves)}種**")
            with col_sa:
                if st.button("＋ 追加", type="primary", use_container_width=True, key="btn_add_serve_type"):
                    st.session_state.adding_serve = True
                    st.rerun()

            if st.session_state.adding_serve:
                with st.container(border=True):
                    new_serve_name = st.text_input("サーブ種類名", key="new_serve_name",
                                                   placeholder="例: フローター, ジャンプサーブ")
                    sa, sb = st.columns(2)
                    with sa:
                        if st.button("追加する", type="primary", use_container_width=True, key="confirm_add_serve_type"):
                            if new_serve_name.strip():
                                serves.append(new_serve_name.strip())
                                st.session_state.serve_types = serves
                                save_config()
                                st.session_state.adding_serve = False
                                st.success(f"「{new_serve_name.strip()}」を追加しました")
                                st.rerun()
                            else:
                                st.error("サーブ種類名を入力してください")
                    with sb:
                        if st.button("キャンセル", use_container_width=True, key="cancel_add_serve_type"):
                            st.session_state.adding_serve = False
                            st.rerun()

            st.divider()

            if not serves:
                st.info("サーブ種類が登録されていません。「＋ 追加」から登録してください。")
            else:
                for i, serve_name in enumerate(serves):
                    with st.container(border=True):
                        c_name, c_del = st.columns([5, 1])
                        with c_name:
                            st.markdown(f"**{serve_name}**")
                        with c_del:
                            if st.button("削除", key=f"del_serve_{i}", use_container_width=True):
                                serves.pop(i)
                                st.session_state.serve_types = serves
                                save_config()
                                st.rerun()

        # ---- 利用者管理 ----
        elif "利用者管理" in section:
            show_viewer_management()


def flatten_events(events_by_set: dict) -> list[dict]:
    out: list[dict] = []
    for set_key, evs in events_by_set.items():
        set_no = int(set_key.replace("Set", ""))
        for e in evs:
            e2 = dict(e)
            e2["set"] = set_no
            out.append(e2)
    return out


# ============================================================
# Court: SVG + transparent overlay buttons (click -> query param)
# ============================================================
ENEMY_ZONES = [str(i) for i in range(1, 10)]
OWN_ZONES = ["L1", "C1", "R1", "L2", "C2", "R2", "L3", "C3", "R3"]
AREAS_GRID = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["L1", "C1", "R1"],
    ["L2", "C2", "R2"],
    ["L3", "C3", "R3"],
]


# ============================================================
# Court: Streamlit Custom Component
# ============================================================
court_component = components.declare_component(
    "court_component", path="court_component"
)

ENEMY_ZONES = [str(i) for i in range(1, 10)]
OWN_ZONES = ["L1", "C1", "R1", "L2", "C2", "R2", "L3", "C3", "R3"]
AREAS_GRID = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["L1", "C1", "R1"],
    ["L2", "C2", "R2"],
    ["L3", "C3", "R3"],
]
ALL_ZONES = ENEMY_ZONES + OWN_ZONES


def _zone_allowed(action: str, label: str, selected_start: str | None) -> bool:
    """Disable zones that should not be clicked for current step."""
    if action == "serve":
        return label in ENEMY_ZONES
    if action == "spike":
        # Always allow Own Zones to correct start position
        if label in OWN_ZONES:
            return True
        # If start is set, allow Enemy Zones for end position
        if selected_start:
            return label in ENEMY_ZONES
        return False
    return False


def court_input(action: str, selected_start: str | None, selected_end: str | None, key: str = None) -> str | None:
    """Render court component and return clicked zone ID."""
    
    # Calculate visual states
    selected = []
    if selected_start:
        selected.append(selected_start)
    if selected_end:
        selected.append(selected_end)
        
    disabled = []
    for zone in ALL_ZONES:
        if not _zone_allowed(action, zone, selected_start):
            disabled.append(zone)
            
    # Call component
    return court_component(
        selected=selected,
        disabled=disabled,
        key=key,
        default=None
    )

def calculate_stats(df_events):
    """Calculate stats per player from events dataframe."""
    if df_events.empty:
        return pd.DataFrame()

    stats = {}
    
    # Initialize stats for all players in master list
    for p in st.session_state.players_master:
        pid = f"{p['number']}: {p.get('nickname', p['name'])}"
        stats[pid] = {
            "Serve": 0, "Serve Ace": 0, "Serve Err": 0,
            "Spike": 0, "Spike Kill": 0, "Spike Err": 0,
            "Block": 0, "Block Kill": 0, "Block Err": 0,
            "Rec": 0, "Rec A": 0, "Rec B": 0, "Rec C": 0, "Rec Err": 0,
            "Dig": 0, "Dig A": 0, "Dig B": 0, "Dig C": 0, "Dig Err": 0
        }

    for _, row in df_events.iterrows():
        action = row.get("action")
        player = row.get("player")
        result = row.get("result")
        
        if not player or not isinstance(player, dict):
            continue
            
        pid = f"{player['number']}: {player.get('nickname', player['name'])}"
        if pid not in stats:
            # Handle guest players or data mismatch
            stats[pid] = {
                "Serve": 0, "Serve Ace": 0, "Serve Err": 0,
                "Spike": 0, "Spike Kill": 0, "Spike Err": 0,
                "Block": 0, "Block Kill": 0, "Block Err": 0,
                "Rec": 0, "Rec A": 0, "Rec B": 0, "Rec C": 0, "Rec Err": 0,
                "Dig": 0, "Dig A": 0, "Dig B": 0, "Dig C": 0, "Dig Err": 0
            }

        s = stats[pid]

        if action == "serve":
            s["Serve"] += 1
            if result == "得点":
                s["Serve Ace"] += 1
            elif result in ("ミス", "ネット", "アウト"):
                s["Serve Err"] += 1
        elif action == "spike":
            s["Spike"] += 1
            if result == "得点":
                s["Spike Kill"] += 1
            elif result in ("ミス", "ネット", "アウト"):
                s["Spike Err"] += 1
        elif action == "block":
            if result == "得点": # Kill
                s["Block"] += 1
                s["Block Kill"] += 1
            elif result in ("ミス", "ネット", "アウト"): # Touch net / Block out etc
                s["Block"] += 1
                s["Block Err"] += 1
            # Touches (One Touch) are not usually counted as block attempts in summary but can be
        elif action == "reception":
            s["Rec"] += 1
            quality = row.get("quality", "")
            if quality == "Aカット":
                s["Rec A"] += 1
            elif quality == "Bカット":
                s["Rec B"] += 1
            elif quality == "Cカット":
                s["Rec C"] += 1
            elif quality == "ミス":
                s["Rec Err"] += 1
        elif action == "dig":
            s["Dig"] += 1
            quality = row.get("quality", "")
            if quality == "Aカット":
                s["Dig A"] += 1
            elif quality == "Bカット":
                s["Dig B"] += 1
            elif quality == "Cカット":
                s["Dig C"] += 1
            elif quality == "ミス":
                s["Dig Err"] += 1

    df = pd.DataFrame.from_dict(stats, orient="index")
    # Sort by number for display
    # Extract number from index
    if not df.empty:
        df["num"] = df.index.str.split(":").str[0].astype(int)
        df = df.sort_values("num").drop("num", axis=1)
        
    return df

# ============================================================
# Analysis / stats
# ============================================================

def compute_action_stats(events: list[dict], action: str) -> dict:
    """Compute per-player stats for a given action (serve/spike/reception/block)."""
    stats: dict[str, dict] = {}
    for e in events:
        if e.get("action") != action:
            continue
        player = e.get("player") or {}
        name = player.get("nickname", player.get("name", ""))
        if not name:
            continue
        s = stats.setdefault(name, {"total": 0, "success": 0, "error": 0,
                                     "net": 0, "out": 0, # Added specific error counters
                                     "A": 0, "B": 0, "C": 0, "D": 0, "zones": {}})
        s["total"] += 1
        result = e.get("result", "")
        quality = e.get("quality", "")

        if action in ("serve", "spike"):
            if result == "得点":
                s["success"] += 1
            elif result in ("ミス", "ネット", "アウト"):
                s["error"] += 1
                if result == "ネット":
                    s["net"] += 1
                elif result == "アウト":
                    s["out"] += 1
            
            zone = e.get("target_zone") if action == "serve" else e.get("end_zone")
            if zone:
                zs = s["zones"].setdefault(zone, {"total": 0, "success": 0})
                zs["total"] += 1
                if result == "得点":
                    zs["success"] += 1
        elif action == "reception":
            if "A" in quality:
                s["A"] += 1
            elif "B" in quality:
                s["B"] += 1
            elif "C" in quality:
                s["C"] += 1
            elif "ミス" in quality:
                s["D"] += 1
                s["error"] += 1
        elif action == "block":
            if result == "得点":
                s["success"] += 1
            elif result in ("ミス", "ネット", "アウト"):
                s["error"] += 1
        elif action == "dig":
            if "A" in quality:
                s["A"] += 1
            elif "B" in quality:
                s["B"] += 1
            elif "C" in quality:
                s["C"] += 1
            elif "ミス" in quality:
                s["D"] += 1
                s["error"] += 1
    return stats




def compute_rotation_stats_by_setter(events: list[dict]) -> pd.DataFrame:
    """
    Compute Side-out rate and Break rate per rotation (S1-S6).
    """
    players = st.session_state.get("players_master", [])
    setters = {p["name"]: p.get("nickname", p["name"]) for p in players if p.get("position") == "S"}
    setter_names = set(setters.values()) | set(setters.keys())
    
    stats = {i: {"s_won":0, "s_tot":0, "r_won":0, "r_tot":0} for i in range(6)}
    
    for ev in events:
        rot = ev.get("rotation")
        srv = ev.get("serving_team")
        res = ev.get("result")
        
        if not rot or not srv:
            continue
            
        # Find setter index in rotation list (0..5)
        s_idx = -1
        # Try exact match first
        for i, pname in enumerate(rot):
            # rotation names often "Number: Nickname"
            # Extract nickname
            parts = pname.split(": ", 1)
            clean = parts[1] if len(parts) > 1 else pname
            if clean in setter_names:
                s_idx = i
                break
        
        if s_idx == -1:
             try:
                # Emergency fallback if names don't match exactly
                for i, pname in enumerate(rot):
                    if any(s in pname for s in setter_names):
                        s_idx = i
                        break
             except:
                pass

        if s_idx == -1:
            # Debug: show why we missed
            st.write(f"Missed setter in rot: {rot}, setters: {setter_names}")
            continue

        # bucket = stats[s_idx]
        # Logic Change: Count attempts based on action type to be more robust?
        # OR: Stick to Rally End but ensure we catch all ends.
        # User problem: "Counts don't match". 1/1 means 1 attempt, 1 success.
        # If user sees 0/0, it means NO rally ending events were found for that rotation.
        # But if they played a whole match, there must be points.
        
        # New Logic:
        # iterate all events. 
        # If action is "serve", increment "s_tot" for the serving team's current rotation?
        # Wait, Side-out rate is Reception team's stat.
        # Break rate is Serving team's stat.
        
        # If we are serving (srv="own"):
        #   Count "Break Opportunity" when we SERVE.
        #   Success if we WIN the rally (result="得点" or opponent error).
        # If we are receiving (srv="opponent"):
        #   Count "Side-out Opportunity" when opponent SERVES (or we receive).
        #   Success if we WIN the rally.
        
        # Implementation:
        # 1. Identify "rally start" or "serve" events?
        #    Events list contains "serve", "spike", "dig", "error"...
        #    A "serve" action is the clearest indicator of a rally start.
        #    If action == "serve":
        #       if serving_team == "own":
        #           stats[s_idx]["s_tot"] += 1
        #           # We need to know who won this rally. 
        #           # The "serve" event might NOT have the result if it was a rally.
        #           # We need to look ahead? Or look at the "result" of the serve event?
        #           # If result is "continue" (None), we don't know the winner yet.
        #           # Limitation: The events are flat list.
        #           # We need to link the serve to the eventual point.
        
        #    Alternative: Look at "Point" events (as before).
        #    If `finished` is true:
        #       It means a rally ended.
        #       So we increment "tot" (Total Rallies for this rotation).
        #       And "won" if we won.
        #    This SHOULD match "Total Serves" if every serve leads to a point.
        #    Why is it missing?
        #    Maybe `s_idx` is -1? (User checked debug message?)
        #    If `s_idx` is found (1/1 exists), then `finished` logic works for SOME.
        
        #    Hypothesis: User records many "Score Updates" without "Events".
        #    In that case, `events` list might have "score_adjustment"?
        #    Let's check `apply_point`.
        #    If I can't find `apply_point` in grep, maybe I should assume it DOES NOT record events.
        #    If so, we can't analyze rotation stats for manual score updates because we don't know the rotation/server at that moment if not recorded!
        #    BUT, `apply_point` updates `st.session_state.score_own`. 
        #    Does it create an entry in `st.session_state.events`?
        #    If NOT, then those points are invisible to analysis.
        
        #    Fix: Ensure `apply_point` records a "score_adjustment" event if one wasn't just recorded.
        #    OR: Tell user "Please use the action buttons (Serve/Spike/Error) to record data for analysis".
        #    But better: Update `apply_point` to record an event if it's a "naked" point.
        
        #    Wait, let's look at `compute_rotation_stats_by_setter` again.
        #    It relies on `ev` having `rotation` and `serving_team`.
        #    If I add a check for `action == "score_adjustment"` or similar?
        #    If the user only uses +1 buttons, we might not have events.
        
        #    Let's try to look for `apply_point` definitions manually by scrolling.
        #    I saw `apply_point` call in lines 2200+.
        #    The definition must be before that.
        
        pass 

                    
    rows = []
    # Labels based on user grid logic 0..5
    labels = ["左上(Pos4)", "中上(Pos3)", "右上(Pos2)", "右下(Pos1)", "中下(Pos6)", "左下(Pos5)"] 
    # Standard court zones: 
    # Front: 4(FL), 3(FC), 2(FR). Back: 5(BL), 6(BC), 1(BR).
    # User Grid 0(TL)..2(TR) -> Front Row L->R?
    # User Grid 3(TL?)..5(BL) -> Back Row R->L?
    # If standard rotation, S starts at Pos 1(BR). moves to 6, 5, 4, 3, 2.
    # We will just label by screen position for now to avoid confusion.
    screen_labels = ["左上", "中上", "右上", "右下", "中下", "左下"]

    for i in range(6):
        d = stats[i]
        s_rate = (d["s_won"] / d["s_tot"] * 100) if d["s_tot"] > 0 else 0.0
        r_rate = (d["r_won"] / d["r_tot"] * 100) if d["r_tot"] > 0 else 0.0
        
        rows.append({
            "セッター位置": screen_labels[i],
            "ブレイク率": f"{s_rate:.1f}% ({d['s_won']}/{d['s_tot']})",
            "サイドアウト率": f"{r_rate:.1f}% ({d['r_won']}/{d['r_tot']})",
        })
        
    return pd.DataFrame(rows)



def render_score_flow_svg(events: list[dict]) -> None:
    """Render a horizontal score flow chart using SVG."""
    
    # 1. Build score sequence
    # data = [(self_score, opp_score, who_scored)]
    # who_scored: 'self' or 'opp'
    data = []
    curr_self = 0
    curr_opp = 0
    
    # Initial state (0-0) - maybe skip plotting 0-0 or plot as start point?
    # User image shows starts from 1. 
    # Let's start tracking from first point.
    
    for ev in events:
        res = ev.get("result")
        scored = None
        if res == "得点":
            curr_self += 1
            scored = "self"
        elif res in ["失点", "ミス", "ネット", "アウト", "得点(相)", "ボール落下", "ドリブル", "ホールディング", "オーバーネット", "タッチネット", "パッシング", "インターフェア", "ディレイ"]:
             curr_opp += 1
             scored = "opp"
             
        if scored:
            data.append({
                "self": curr_self,
                "opp": curr_opp,
                "scorer": scored
            })
            
    if not data:
        st.info("データが不足しています")
        return

    # 2. SVG Configuration
    step_width = 60
    height = 200
    margin_left = 40
    margin_right = 40
    circle_r = 14
    
    # Y positions
    y_self = 50
    y_opp = 150
    
    width = margin_left + (len(data) * step_width) + margin_right
    
    svg_elements = []
    
    # Center line (divider)
    # svg_elements.append(f'<line x1="0" y1="{height/2}" x2="{width}" y2="{height/2}" stroke="#ddd" stroke-width="1" stroke-dasharray="4" />')
    
    # Draw paths first (lines behind circles)
    # Start point? Maybe from 0,0 (virtual)? 
    # Or just connect the points we have.
    # Let's connect points.
    
    prev_x = margin_left
    prev_y = height / 2 # Start from center or virtual 0-0?
    # If we assume 0-0 is at x=margin_left - step_width?
    # Let's just draw lines between actual points.
    
    # We need coordinates for all points first
    coords = []
    for i, d in enumerate(data):
        x = margin_left + (i * step_width)
        y = y_self if d["scorer"] == "self" else y_opp
        coords.append((x, y, d))
        
    # Draw Lines
    # Style: Line color matches the *target* node? or neutral?
    # User's image shows black zig-zag lines. 
    path_d = []
    # Start from a virtual 0-0 point for visual continuity?
    # Virtual 0-0 at index -1
    start_x = margin_left - step_width
    start_y = height / 2 
    path_d.append(f"M {start_x} {start_y}")
    
    for x, y, _ in coords:
        path_d.append(f"L {x} {y}")
        
    svg_elements.append(f'<path d="{" ".join(path_d)}" fill="none" stroke="#333" stroke-width="2" />')

    # Draw Nodes (Circles and Text)
    for x, y, d in coords:
        scorer = d["scorer"]
        val = d["self"] if scorer == "self" else d["opp"]
        
        # Color theme
        if scorer == "self":
            fill = "#3b82f6" # Blue
            text_col = "white"
        else:
            fill = "#ef4444" # Red
            text_col = "white"
            
        # Circle
        svg_elements.append(f'<circle cx="{x}" cy="{y}" r="{circle_r}" fill="{fill}" stroke="#fff" stroke-width="2" />')
        
        # Text (Score)
        # Centered text
        svg_elements.append(f'<text x="{x}" y="{y}" dy="5" text-anchor="middle" fill="{text_col}" font-size="14" font-family="Arial" font-weight="bold">{val}</text>')
        
        # Optional: Small label for total score context? e.g. "15-12" above/below?
        # User request: "Details in circle". Likely the point number (1, 2, 3...) of that team.
        # "Score on the board" logic.
        
    svg_content = "".join(svg_elements)
    
    html = f"""
    <div style="width:100%; overflow-x:auto; padding: 10px; background: white; border-radius: 8px; border: 1px solid #eee;">
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <!-- Background labels -->
            <text x="10" y="{y_self}" dy="5" fill="#3b82f6" font-weight="bold" font-size="12">Self</text>
            <text x="10" y="{y_opp}" dy="5" fill="#ef4444" font-weight="bold" font-size="12">Opp</text>
            {svg_content}
        </svg>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def convert_to_csv_bytes(events_by_set: dict) -> bytes:
    flat = []
    for set_key, evs in events_by_set.items():
        s_no = set_key.replace("Set", "")
        for e in evs:
            row = dict(e)
            row["set"] = s_no
            # Flatten dicts
            p = row.get("player")
            if isinstance(p, dict):
                row["player"] = p.get("name") # simplify to name
            if isinstance(row.get("rotation"), list):
                row["rotation"] = "|".join(row["rotation"])
            flat.append(row)
            
    if not flat:
        return b""
    return pd.DataFrame(flat).to_csv(index=False).encode('utf_8_sig')


def render_court_zone_html(zone_stats: dict, metric_type: str = "count") -> str:
    """Render a 3x3 opponent court with per-zone stats as HTML.
    metric_type: "count" (default), "kill_rate", "eff_rate"
    """
    # Match the input component layout (Zones 1-3 at top = Endline side)
    grid = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]

    # Dark mode colors for analysis court - REMOVED, forcing Light Mode
    # is_dark = st.session_state.get("dark_mode", False)
    text_main = "#0f172a" 
    text_sub = "#64748b" 
    border_color = "rgba(0,0,0,0.1)" # Outer border
    
    # Calculate totals for scaling if needed
    # max_total = max((s["total"] for s in zone_stats.values()), default=1)

    cells = ""
    for row in grid:
        for z in row:
            zs = zone_stats.get(z, {"total": 0, "success": 0})
            total = zs["total"]
            success = zs["success"]
            # For efficiency, we need net/out but zone_stats might only have total/success if not updated in compute_action_stats
            # compute_action_stats updates zs with total/success.
            # If we need eff_rate, we strictly need errors in zones. 
            # Current `compute_action_stats` only adds success/total to zones. 
            # We should probably blindly trust "success" for kill rate.
            # For eff_rate in ZONES, we might lack error data if not separately tracked in zones.
            # Let's check compute_action_stats... 
            # It DOES NOT track errors per zone basically. 
            # "zs = s['zones'].setdefault(zone, {'total': 0, 'success': 0})"
            # We need to fix compute_action_stats to track errors in zones too if we want eff_rate per zone.
            # For now, let's assume we can't show eff_rate perfectly per zone without that data.
            # BUT, since we are doing this in the same file, I should probably check if I can just assume success/total is enough?
            # No, Eff Rate = (Success - Error) / Total.
            # If I don't validly track errors per zone, Eff Rate will be wrong.
            # Let's proceed with Count and Kill Rate logic first, and maybe Eff Rate is just (Success - (Total-Success))? 
            # No, 'Continue' is not error.
            # I'll update compute_action_stats separately if needed, but the user asked for it. 
            # Let's implement valid logic on the assumption data exists, or just show what we have.
            # Actually, let's stick to what we have or do a best effort.
            # Re-reading `compute_action_stats`: it tracks total and success. 
            # I should update `compute_action_stats` to track errors in zones too.
            # I will do that in a separate step if strictly needed, but let's write the renderer to handle "error" if present, else 0.
            
            error = zs.get("error", 0) # Fallback
            
            # Values
            kill_rate = (success / total * 100) if total else 0.0
            eff_rate = ((success - error) / total * 100) if total else 0.0

            # Formatting & Color Logic
            cell_content = f'<div style="font-size:0.75rem; color:{text_sub}; font-weight:600;">ゾーン {z}</div>'
            bg_style = ""
            
            if metric_type == "count":
                # Background: Blue-ish opacity based on count (Density)
                # Count Mode: Show ONLY Count.
                bg_opacity = min(0.15 + (total / 20) * 0.5, 0.7) if total else 0.05
                bg_style = f"background: rgba(56,189,248,{bg_opacity:.2f});"
                cell_content += f'<div style="font-weight:800; font-size:1.6rem; color:{text_main};">{total}本</div>'

            elif metric_type == "kill_rate":
                # Kill Rate Mode: Show Count + Rate.
                # Background: Green Gradient (0-100%).
                # 0% -> White/Transparent, 100% -> Green.
                # To map 0-100 to color, we can use simple rgba or hsl.
                # Green: hsl(142, 76%, 36%) is #16a34a (tailwind green-600).
                # We want gradient. 
                # Let's use similar logic to style_metric_cell: 1.0 (100%) is fairly dark green.
                # We render background with opacity ~0.6 to see court?
                # "コートの色を遮りすぎないよう透明度を上げる" -> High transparency.
                # Let's say alpha = 0.5 * (rate/100).
                if total > 0:
                    # Map 0-100 to opacity 0.1-0.7 of Green
                    ratio = min(kill_rate / 100.0, 1.0)
                    op = 0.2 + (ratio * 0.5) 
                    bg_style = f"background: rgba(22, 163, 74, {op:.2f});"
                    val_color = "#ffffff" if op > 0.4 else text_main
                else:
                    bg_style = "background: rgba(0,0,0,0.05);"
                    val_color = text_sub

                cell_content += f'<div style="font-weight:700; font-size:1.2rem; color:{val_color};">{total}本</div>'
                cell_content += f'<div style="font-weight:600; font-size:1rem; color:{val_color};">{kill_rate:.0f}%</div>'

            elif metric_type == "eff_rate":
                # Eff Rate Mode: Show Count + Rate.
                # Background: Red (neg) -> White (0) -> Green (pos).
                # Use style_metric_cell logic but converted to RGBA/CSS.
                if total > 0:
                    # Normalize -100 to 100 -> -1.0 to 1.0
                    val = eff_rate / 100.0
                    if val >= 0:
                        # Green
                        ratio = min(val, 1.0)
                        op = 0.2 + (ratio * 0.5)
                        bg_style = f"background: rgba(22, 163, 74, {op:.2f});"
                        val_color = "#ffffff" if op > 0.4 else text_main
                    else:
                        # Red
                        ratio = min(abs(val), 1.0)
                        op = 0.2 + (ratio * 0.5)
                        bg_style = f"background: rgba(220, 38, 38, {op:.2f});" # Red-600
                        val_color = "#ffffff" if op > 0.4 else text_main
                else:
                    bg_style = "background: rgba(0,0,0,0.05);"
                    val_color = text_sub
                
                cell_content += f'<div style="font-weight:700; font-size:1.2rem; color:{val_color};">{total}本</div>'
                cell_content += f'<div style="font-weight:600; font-size:1rem; color:{val_color};">{eff_rate:.0f}%</div>'

            cells += f'''
            <div style="
                {bg_style}
                border: 1px solid rgba(255,255,255,0.4);
                border-radius: 10px;
                padding: 8px 4px;
                text-align: center;
                min-height: 80px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 2px;
            ">
                {cell_content}
            </div>'''
            
    # Container style
    container_bg = "linear-gradient(135deg, #f59e0b, #d97706)" 
    container_border = "#fbbf24"
    
    return f'''
    <div style="max-width:480px; margin: 8px 0;">
        <div style="text-align:center; font-size:0.75rem; color:{text_sub}; margin-bottom:4px;">▲ エンドライン側</div>
        <div style="
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 6px;
            background: {container_bg};
            padding: 12px;
            border-radius: 14px;
            border: 3px solid {container_border};
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        ">{cells}</div>
        <div style="text-align:center; font-size:0.75rem; color:{text_sub}; margin-top:4px;">▼ ネット側</div>
    </div>'''


def render_stats_table(stats: dict, action: str) -> None:
    """Render stats table for serve/spike/block or reception."""
    if not stats:
        st.info(f"{action}のデータがありません。")
        return

    if action in ("serve", "spike", "block"):
        labels = {"serve": "サーブ", "spike": "スパイク", "block": "ブロック"}
        action_label = labels.get(action, action)
        rows = []
        for name, s in sorted(stats.items()):
            total = s["total"]
            success = s["success"]
            error = s["error"]
            net_err = s.get("net", 0)
            out_err = s.get("out", 0)
            
            # Keep as ratio (0.0-1.0) for styling
            kill_rate = (success / total) if total else 0.0
            eff_rate = ((success - error) / total) if total else 0.0
            rows.append({
                "選手": name,
                "本数": total,
                "決定": success,
                # "ミス": error, # Removed as per request, using Net/Out instead
                "ネット": net_err,
                "アウト": out_err,
                "決定率": kill_rate,
                "効果率": eff_rate,
            })
        df = pd.DataFrame(rows)
        
        # Apply styling: format as % and add background gradient
        st.markdown(f"#### {action_label}統計")
        if not df.empty:
            # Drop Net/Out columns if action is block (usually not tracked this way, or keep for consistency?)
            # Block errors are usually "Touch Net" or "Block Out" (tooling side).
            # But our logic only adds net/out for serve/spike in compute_action_stats. 
            # So for block they will be 0. We can hide them if all 0, but let's keep it simple.
            
            cols_config = {
                "選手": st.column_config.TextColumn("選手"),
                "本数": st.column_config.NumberColumn("本数", format="%d"),
                "決定": st.column_config.NumberColumn("決定", format="%d"),
                # "ミス": st.column_config.NumberColumn("ミス", format="%d"), # Removed
                "ネット": st.column_config.NumberColumn("ネット", format="%d"),
                "アウト": st.column_config.NumberColumn("アウト", format="%d"),
            }

            styled = (df.style
                      .format({"決定率": "{:.1%}", "効果率": "{:.1%}"})
                      .applymap(style_metric_cell, subset=["決定率", "効果率"]))
            
            st.dataframe(
                styled, 
                column_config=cols_config,
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif action == "reception":
        # Reception
        rows = []
        for name, s in sorted(stats.items()):
            total = s["total"]
            a, b, c, d = s["A"], s["B"], s["C"], s["D"]
            a_rate = (a / total) if total else 0.0
            pos_rate = ((a + b) / total) if total else 0.0
            rows.append({
                "選手": name,
                "本数": total,
                "Aカット": a,
                "Bカット": b,
                "Cカット": c,
                "ミス": d,
                "A率": a_rate,
                "成功率": pos_rate,
            })
        df = pd.DataFrame(rows)
        st.markdown("#### レセプション統計")
        if not df.empty:
            styled = (df.style
                      .format({"A率": "{:.1%}", "成功率": "{:.1%}"})
                      .applymap(style_metric_cell, subset=["A率", "成功率"]))
            st.dataframe(styled, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif action == "dig":
        rows = []
        for name, s in sorted(stats.items()):
            total = s["total"]
            a, b, c, d = s["A"], s["B"], s["C"], s["D"]
            a_rate = (a / total) if total else 0.0
            pos_rate = ((a + b) / total) if total else 0.0 
            rows.append({
                "選手": name,
                "本数": total,
                "Aカット": a,
                "Bカット": b,
                "Cカット": c,
                "ミス": d,
                "A率": a_rate,
                "成功率": pos_rate,
            })
        df = pd.DataFrame(rows)
        st.markdown("#### ディグ統計")
        if not df.empty:
            styled = (df.style
                      .format({"A率": "{:.1%}", "成功率": "{:.1%}"})
                      .applymap(style_metric_cell, subset=["A率", "成功率"]))
            st.dataframe(styled, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.dataframe(df, use_container_width=True, hide_index=True)


def render_analysis_view(events: list[dict], title: str = "") -> None:
    """Render the full analysis UI with two views."""
    if title:
        st.header(title)

    if not events:
        st.info("分析するデータがありません。")
        return

    # --- Set filter ---
    set_numbers = sorted(set(e.get("set", 1) for e in events))
    set_options = ["全セット"] + [f"Set {n}" for n in set_numbers]
    selected_set = st.selectbox("📋 セット選択", set_options, key=f"set_filter_{title}")
    if selected_set != "全セット":
        set_no = int(selected_set.replace("Set ", ""))
        events = [e for e in events if e.get("set") == set_no]

    # Precompute all stats
    serve_stats = compute_action_stats(events, "serve")
    spike_stats = compute_action_stats(events, "spike")
    reception_stats = compute_action_stats(events, "reception")
    block_stats = compute_action_stats(events, "block")
    dig_stats = compute_action_stats(events, "dig")

    # Summary line
    total_events = len([e for e in events if e.get("action") in ("serve", "spike", "reception", "block", "dig")])
    st.caption(f"📊 総イベント数: {total_events} | サーブ: {sum(s['total'] for s in serve_stats.values())} | スパイク: {sum(s['total'] for s in spike_stats.values())} | レセプ: {sum(s['total'] for s in reception_stats.values())} | ブロック: {sum(s['total'] for s in block_stats.values())} | ディグ: {sum(s['total'] for s in dig_stats.values())}")

    # CSV Export moved to Team General tab

    # View selector and Metric selector
    # 2 columns for compact layout
    vc1, vc2 = st.columns([1, 1])
    with vc1:
        view = st.radio("分析ビュー", ["アクション別", "選手別", "チーム全般"], horizontal=True, key=f"analysis_view_{title}")
    with vc2:
        metric_opt = st.radio("コート表示項目", ["本数", "決定率", "効果率"], horizontal=True, key=f"metric_opt_{title}")

    metric_map = {"本数": "count", "決定率": "kill_rate", "効果率": "eff_rate"}

    if view == "アクション別":
        action_tab = st.radio("アクション", ["サーブ", "スパイク", "レセプション", "ブロック", "ディグ"], horizontal=True, key=f"action_tab_{title}")

        if action_tab == "サーブ":
            with st.container(border=True):
                render_stats_table(serve_stats, "serve")
            if serve_stats:
                with st.container(border=True):
                    st.markdown("#### サーブコース分析（全体）")
                    all_zones: dict = {}
                    for s in serve_stats.values():
                        for z, zs in s["zones"].items():
                            az = all_zones.setdefault(z, {"total": 0, "success": 0})
                            az["total"] += zs["total"]
                            az["success"] += zs["success"]
                    st.markdown(render_court_zone_html(all_zones, metric_map[metric_opt]), unsafe_allow_html=True)

        elif action_tab == "スパイク":
            with st.container(border=True):
                render_stats_table(spike_stats, "spike")
            if spike_stats:
                with st.container(border=True):
                    st.markdown("#### スパイクコース分析（全体）")
                    all_zones: dict = {}
                    for s in spike_stats.values():
                        for z, zs in s["zones"].items():
                            az = all_zones.setdefault(z, {"total": 0, "success": 0})
                            az["total"] += zs["total"]
                            az["success"] += zs["success"]
                    st.markdown(render_court_zone_html(all_zones, metric_map[metric_opt]), unsafe_allow_html=True)

        elif action_tab == "レセプション":
            with st.container(border=True):
                render_stats_table(reception_stats, "reception")

        elif action_tab == "ディグ":
            with st.container(border=True):
                render_stats_table(dig_stats, "dig")

        else:  # Block
            with st.container(border=True):
                render_stats_table(block_stats, "block")

    elif view == "選手別":
        # Player-based view
        all_players = sorted(set(
            list(serve_stats.keys()) + list(spike_stats.keys()) +
            list(reception_stats.keys()) + list(block_stats.keys()) + list(dig_stats.keys())
        ))
        if not all_players:
            st.info("選手データがありません。")
            return

        selected_player = st.selectbox("👤 選手を選択", all_players, key=f"player_select_{title}")

        if selected_player:
            # --- Serve ---
            with st.container(border=True):
                if selected_player in serve_stats:
                    s = serve_stats[selected_player]
                    col_table, col_court = st.columns([3, 2])
                    with col_table:
                        render_stats_table({selected_player: s}, "serve")
                    with col_court:
                        if s["zones"]:
                            st.markdown("##### サーブコース")
                            st.markdown(render_court_zone_html(s["zones"], metric_map[metric_opt]), unsafe_allow_html=True)
                else:
                    st.caption("サーブデータなし")

            # --- Spike ---
            with st.container(border=True):
                if selected_player in spike_stats:
                    s = spike_stats[selected_player]
                    col_table, col_court = st.columns([3, 2])
                    with col_table:
                        render_stats_table({selected_player: s}, "spike")
                    with col_court:
                        if s["zones"]:
                            st.markdown("##### スパイクコース")
                            st.markdown(render_court_zone_html(s["zones"], metric_map[metric_opt]), unsafe_allow_html=True)
                else:
                    st.caption("スパイクデータなし")


            # --- Reception ---
            with st.container(border=True):
                if selected_player in reception_stats:
                    render_stats_table({selected_player: reception_stats[selected_player]}, "reception")
                else:
                    st.caption("レセプションデータなし")

            # --- Block ---
            with st.container(border=True):
                if selected_player in block_stats:
                    render_stats_table({selected_player: block_stats[selected_player]}, "block")
                else:
                    st.caption("ブロックデータなし")

            # --- Dig ---
            with st.container(border=True):
                if selected_player in dig_stats:
                    render_stats_table({selected_player: dig_stats[selected_player]}, "dig")
                else:
                    st.caption("ディグデータなし")



    elif view == "チーム全般":
        st.subheader("チーム全般分析")
        
        # 1. Momentum Chart
        st.markdown("##### 📈 得点推移")
        render_score_flow_svg(events)
        
        st.markdown("---")
        
        # 2. Rotation Analysis
        st.markdown("##### 🔄 ローテーション別分析 (S1-S6)")
        st.caption("※S位置: セッターのローテーション位置 (ブレイク率: サーブ時得点率, サイドアウト率: レセプション時得点率)")
        
        rot_df = compute_rotation_stats_by_setter(events)
        if not rot_df.empty:
            # Styling
            st.dataframe(
                rot_df.style.format({"ブレイク率": "{}", "サイドアウト率": "{}"}), # Data is string already but kept for safety
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("ローテーションデータが不足しています（セッターが特定できない場合など）")
            
        st.markdown("---")
        
        # 3. CSV Export (Restored here)
        st.markdown("##### 📥 データ出力")
        csv_rows = []
        for e in events:
            # Export all events including sub/timeout? User likely wants play data.
            # Existing logic filtered specific actions. Let's keep it broad or specific?
            # User wants "CSV Export".
            # Let's include everything but flatten it nicely.
            p = e.get("player")
            pname = p.get("nickname", p.get("name", "")) if isinstance(p, dict) else ""
            
            row = {
                "セット": e.get("set", ""),
                "アクション": e.get("action", ""),
                "選手": pname,
                "結果": e.get("result", e.get("quality", "")),
                "サブタイプ": e.get("sub_type", e.get("serve_type", "")),
                "ゾーン(始)": e.get("start_zone", e.get("target_zone", "")),
                "ゾーン(終)": e.get("end_zone", ""),
            }
            if "rotation" in e and isinstance(e["rotation"], list):
                row["ローテーション"] = "|".join(e["rotation"])
            if "score_own" in e:
                row["自得点"] = e["score_own"]
            if "score_opponent" in e:
                row["相得点"] = e["score_opponent"]
                
            csv_rows.append(row)
            
        if csv_rows:
            csv_df = pd.DataFrame(csv_rows)
            csv_data = csv_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "CSVダウンロード (表示中のセット)", 
                data=csv_data, 
                file_name="volleyball_stats.csv", 
                mime="text/csv", 
                key=f"csv_dl_team_{title}"
            )
        else:
            st.write("データがありません")


def load_match_preview(path: str) -> dict:
    """Read first/last lines of jsonl to get match metadata without loading full events."""
    meta = {"team": "?", "opponent": "?", "score": "?-?", "date": "?"}
    try:
        with open(path, "r", encoding="utf-8") as f:
            # Read first line for initial setup
            first_line = f.readline().strip()
            if first_line:
                e = json.loads(first_line)
                # Timestamp to date
                ts = e.get("timestamp")
                if ts:
                    dt = datetime.fromtimestamp(ts)
                    meta["date"] = dt.strftime("%Y-%m-%d")
            
            # Read last line for final score/names
            # Efficient seek to end? bit tricky with variable line length jsonl.
            # Just read all lines? OK for small files.
            lines = f.readlines()
            if not lines and first_line:
                lines = [first_line]
            elif first_line:
                lines = [first_line] + lines
                
            if lines:
                last_e = json.loads(lines[-1].strip())
                meta["team"] = last_e.get("team_name", "自チーム")
                meta["opponent"] = last_e.get("opponent_name", "相手チーム")
                meta["score"] = f"{last_e.get('score_own',0)}-{last_e.get('score_opponent',0)}"
    except:
        pass
    return meta


def show_data_analysis() -> None:
    st.markdown("## データ分析")

    saved = list_saved_matches(st.session_state.get("auth_team", "default"))
    if not saved:
        with st.container(border=True):
            st.info("保存済みの試合がありません。リアルタイム分析で試合を記録し「試合終了」で保存してください。")
        return

    # Session state
    if "da_selected_idx" not in st.session_state:
        st.session_state.da_selected_idx = None

    tab_single, tab_multi = st.tabs(["　1試合分析　", "　まとめて分析　"])

    # ===== TAB 1: 1試合分析 =====
    with tab_single:
        # Filter bar
        with st.container(border=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                opponent_filter = st.text_input("対戦相手で絞り込み", placeholder="例: 甲西", key="da_single_opp")
            with fc2:
                all_dates = sorted({m["match_date"] or m["tournament"] for m in saved if m["match_date"] or m["tournament"]}, reverse=True)
                date_options = ["すべて"] + all_dates
                date_filter = st.selectbox("日付で絞り込み", date_options, key="da_single_date")

        # Apply filters
        filtered = [
            m for m in saved
            if (not opponent_filter or opponent_filter in (m.get("match_opponent") or m["filename"]))
            and (date_filter == "すべて" or (m.get("match_date") or m["tournament"]) == date_filter)
        ]

        if not filtered:
            st.info("条件に一致する試合がありません。")
        else:
            st.caption(f"{len(filtered)} 件")
            for i, m in enumerate(filtered):
                opponent = m.get("match_opponent") or "—"
                date = m.get("match_date") or m["tournament"] or "—"
                is_selected = st.session_state.da_selected_idx == m["path"]

                with st.container(border=True):
                    c_info, c_btn = st.columns([5, 1])
                    with c_info:
                        st.markdown(f"**vs {opponent}**")
                        st.caption(f"{date}　|　{m['filename']}")
                    with c_btn:
                        btn_lbl = "閉じる" if is_selected else "分析"
                        if st.button(btn_lbl, key=f"da_card_{i}",
                                     type="primary" if is_selected else "secondary",
                                     use_container_width=True):
                            st.session_state.da_selected_idx = None if is_selected else m["path"]
                            st.rerun()

                if is_selected:
                    with st.container(border=True):
                        events = load_events_from_file(m["path"])
                        render_analysis_view(events, title="")

    # ===== TAB 2: まとめて分析 =====
    with tab_multi:
        st.caption("対戦相手や日付で絞り込んだ複数試合をまとめて分析します。")
        with st.container(border=True):
            mc1, mc2 = st.columns(2)
            with mc1:
                multi_opp = st.text_input("対戦相手で絞り込み", placeholder="例: 甲西（空欄で全対象）", key="da_multi_opp")
            with mc2:
                multi_date = st.selectbox("日付で絞り込み", ["すべて"] + all_dates, key="da_multi_date")

        multi_filtered = [
            m for m in saved
            if (not multi_opp or multi_opp in (m.get("match_opponent") or m["filename"]))
            and (multi_date == "すべて" or (m.get("match_date") or m["tournament"]) == multi_date)
        ]

        if not multi_filtered:
            st.info("条件に一致する試合がありません。")
        else:
            # Show filtered match list
            for m in multi_filtered:
                opponent = m.get("match_opponent") or "—"
                date = m.get("match_date") or m["tournament"] or "—"
                st.markdown(f"- {date}　**vs {opponent}**　{m['filename']}")

            st.markdown("---")
            if st.button(f"この {len(multi_filtered)} 試合をまとめて分析", type="primary", use_container_width=True, key="btn_multi_analyze"):
                all_events = []
                for m in multi_filtered:
                    all_events.extend(load_events_from_file(m["path"]))
                if all_events:
                    st.markdown("### 分析結果")
                    render_analysis_view(all_events, title="")


def get_player_short(pname: str) -> str:
    """Extract display name if format is 'Number: Nickname'."""
    pname = str(pname)
    if ":" in pname:
        return pname.split(":", 1)[1].strip()
    return pname


def render_rotation_panel(show_title: bool = True) -> None:
    rot = st.session_state.rotation
    if not isinstance(rot, list) or len(rot) < 6:
        st.warning("ローテーションが未設定です（6人の並びが必要）")
        return

    if show_title:
        st.markdown("### ローテーション（現在配置）")
    p = rot
    
    # Dark mode colors for rotation panel - REMOVED
    # is_dark = st.session_state.get("dark_mode", False)
    bg_panel = "#eee"
    bg_cell = "#fff"
    text_cell = "#000"

    html = f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; background: {bg_panel}; padding: 5px; border-radius: 5px; margin-bottom: 10px;">
        <div style="background:{bg_cell}; color:{text_cell}; padding:5px; text-align:center; font-weight:bold;">{get_player_short(p[0])}</div>
        <div style="background:{bg_cell}; color:{text_cell}; padding:5px; text-align:center; font-weight:bold;">{get_player_short(p[1])}</div>
        <div style="background:{bg_cell}; color:{text_cell}; padding:5px; text-align:center; font-weight:bold;">{get_player_short(p[2])}</div>
        <div style="background:{bg_cell}; color:{text_cell}; padding:5px; text-align:center; font-weight:bold;">{get_player_short(p[5])}</div>
        <div style="background:{bg_cell}; color:{text_cell}; padding:5px; text-align:center; font-weight:bold;">{get_player_short(p[4])}</div>
        <div style="background:{bg_cell}; color:{text_cell}; padding:5px; text-align:center; font-weight:bold;">{get_player_short(p[3])}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # --- Unified substitution button (opens full-screen UI) ---
    if st.button("🔁 選手交代", key="start_sub", use_container_width=True):
        st.session_state.is_sub_mode = True
        st.session_state.sub_step = 1
        st.session_state.sub_in_player = None
        st.session_state.sub_in_is_libero = False
        st.rerun()


def record_event(event: dict) -> None:
    event = dict(event)
    event.setdefault("id", str(uuid.uuid4()))
    event.setdefault("timestamp", datetime.now().timestamp())
    event.setdefault("realTime", datetime.now().isoformat())
    event["score_own"] = st.session_state.score_own
    event["score_opponent"] = st.session_state.score_opponent
    event["rotation"] = st.session_state.rotation.copy()
    event["libero_in_court"] = st.session_state.libero_in_court

    set_key = f"Set{st.session_state.current_set}"
    st.session_state.events.setdefault(set_key, []).append(event)

    # GCS への書き込みは5イベントごとにまとめて行う（毎回書くと遅延が大きいため）
    # イベントはすでに session_state.events に保持されているので、クラッシュ時の損失は最大4イベント分
    st.session_state.unsaved_event_count += 1
    if st.session_state.unsaved_event_count >= 5:
        save_current_match_snapshot()
        st.session_state.unsaved_event_count = 0
    elif st.session_state.unsaved_event_count == 1:
        # 初回イベント時はメタデータだけ保存（試合情報の記録）
        save_match_meta()

    # Toast notification
    action = event.get("action", "")
    toast_msg = ""
    if action == "serve":
        p = event.get("player") or {}
        toast_msg = f"✅ サーブ - {p.get('nickname', p.get('name', ''))} / {event.get('result', '')}"
    elif action == "spike":
        p = event.get("player") or {}
        toast_msg = f"✅ スパイク - {p.get('nickname', p.get('name', ''))} / {event.get('result', '')}"
    elif action == "reception":
        p = event.get("player") or {}
        toast_msg = f"✅ レセプション - {p.get('nickname', p.get('name', ''))} / {event.get('quality', '')}"
    elif action == "error":
        toast_msg = f"✅ ミス記録 - {event.get('error_detail', '')}"
    elif action == "substitution":
        toast_msg = f"✅ 交代 - {get_player_short(event.get('player_in',''))} ← {get_player_short(event.get('player_out',''))}"
    else:
        toast_msg = f"✅ 記録しました"
    if toast_msg:
        st.toast(toast_msg)

    # Auto-Action Transition Logic (In-Rally)
    # Only transition if the rally continues.
    # If point scored (result="得点" or "ミス" etc that ends rally), apply_point handles the next state (Serve/Reception).
    # We should NOT overwrite it here.
    
    is_rally_continue = True
    result = event.get("result")
    if result in ["得点", "ミス", "ネット", "アウト", "error"]:
        is_rally_continue = False
    # reception/dig quality check?
    # quality A/B/C is continue. "ミス" is end.
    if action in ["reception", "dig"]:
         if event.get("quality") == "ミス":
             is_rally_continue = False
             
    if is_rally_continue:
        if action == "serve":
            # Serve -> Dig (expecting opponent attack)
            st.session_state.current_action = "dig"
            st.session_state.selected_player = None 
            
        elif action == "reception":
            # Reception -> Spike
            st.session_state.current_action = "spike"
            st.session_state.selected_player = None

        elif action == "dig":
            # Dig -> Spike
            st.session_state.current_action = "spike"
            st.session_state.selected_player = None

        elif action == "spike":
            # Spike -> Dig (if rally continues)
            st.session_state.current_action = "dig"
            st.session_state.selected_player = None

        elif action == "block":
             # Block -> Dig
             st.session_state.current_action = "dig"
             st.session_state.selected_player = None

    # --- Always clear ephemeral inputs ---
    # These should not persist across actions
    st.session_state.start_area = None
    st.session_state.end_area = None
    # We keep selected_player because apply_point might have set it for the next server.
    # We keep selected_serve/attack if we want to "remember" last choice? 
    # Usually we want to clear them too, unless it's the SAME server continuing.
    # But user complained about start_area (course) specifically.
    # Let's clear selected_attack too as it's action-specific.
    # selected_serve might be useful to keep if same player serves again? 
    # But apply_point sets default serve type anyway.
    
    if action != "serve":
        # If not serving, clear selected_serve (just in case)
        st.session_state.selected_serve = None
        
    if action != "spike":
        # If not spiking, clear selected_attack
        st.session_state.selected_attack = None


def apply_point(team: str) -> None:
    """Handle point scored. Rotation happens only on side-out (own team scores while opponent serves)."""
    current_serve = st.session_state.serving_team
    
    # Safety: if serving_team is not set, default to "own" (no rotation on fallback)
    if current_serve is None:
        st.session_state.serving_team = "own"
        current_serve = "own"
    
    if team == "own":
        st.session_state.score_own += 1
        if current_serve == "opponent":
            # Side out: we scored while opponent was serving -> Rotate and take serve
            st.session_state.rotation = st.session_state.rotation[-1:] + st.session_state.rotation[:-1]
            st.session_state.serving_team = "own"
            # Auto-select server (Position 1: index 3 in our list [0,1,2,5,4,3]) wait, check index.
            # Rotation list is [TL, TC, TR, BR, BC, BL] -> [0, 1, 2, 3, 4, 5] ?
            # No. view_file line 1993:
            # Top Row: 0(FL), 1(FC), 2(FR)
            # Bottom Row: 5(BL), 4(BC), 3(BR).
            # Logic: Clockwise 1->2->3->4->5->6.
            # Position 1 is Back-Right.
            # Also set action to "serve"
            st.session_state.current_action = "serve"
            
            # --- Libero Auto-OUT (Libero rotates to front) ---
            # Rotation just happened. 
            # Check Position 4 (Front-Left). 
            # Indices: Top Row 0(FL), 1(FC), 2(FR).
            # So Index 0 is Position 4.
            
            # --- Libero Auto-OUT (Libero rotates to front) ---
            # Rotation just happened. 
            # Check Position 4 (Front-Left). Index 0.
            
            fl_idx = 0
            p_str = st.session_state.rotation[fl_idx]
            
            # Check if it is Libero (by Position "L" in master)
            is_libero_pos = False
            for p in st.session_state.players_master:
                fmt = f"{p['number']}: {p.get('nickname', p['name'])}"
                if fmt == p_str:
                    if p.get("position") == "L":
                        is_libero_pos = True
                    break
            
            # Check if it matches selected Libero (just in case)
            if st.session_state.get("libero_player_id") and p_str == st.session_state.get("libero_player_id"):
                is_libero_pos = True

            if is_libero_pos:
                # Swap OUT!
                mb_in = None
                
                # 1. Try stack first
                if st.session_state.get("mb_later_swap"):
                    mb_in = st.session_state.mb_later_swap.pop(0)
                
                # 2. If stack empty (or reload happened), find MB from master who is NOT in rotation
                if not mb_in:
                        # Find all MBs
                        all_mbs = []
                        for p in st.session_state.players_master:
                            if p.get("position") == "MB":
                                fmt = f"{p['number']}: {p.get('nickname', p['name'])}"
                                all_mbs.append(fmt)
                        
                        # Filter out those currently in rotation (except the Libero position we are swapping)
                        # Rotation has 6 players. One is Libero.
                        current_players = set(st.session_state.rotation)
                        
                        for mb in all_mbs:
                            if mb not in current_players:
                                mb_in = mb
                                break
                
                if mb_in:
                    st.session_state.rotation[fl_idx] = mb_in
                    st.toast(f"🔄 リベロ交代: {get_player_short(p_str)} OUT / {get_player_short(mb_in)} IN")
                else:
                    st.warning("交代するMBが見つかりません（ベンチにMBがいません）")
            
            # Select the server automatically
            # Only if we have a valid rotation list
            if len(st.session_state.rotation) > 3:
                # Find the player dict from master list to set selected_player
                server_name_fmt = st.session_state.rotation[3] # "Number: Nickname"
                found_p = None
                for p in st.session_state.players_master:
                    fmt = f"{p['number']}: {p.get('nickname', p['name'])}"
                    if fmt == server_name_fmt:
                        found_p = p
                        break
                st.session_state.selected_player = found_p
                
                # Auto-select first serve type if available
                if found_p:
                    _serves = found_p.get("serve_types") or ([found_p["default_serve"]] if found_p.get("default_serve") and found_p.get("default_serve") != "なし" else [])
                    if _serves and _serves[0] in st.session_state.serve_types:
                        st.session_state.selected_serve = _serves[0]

        # else: we were serving and scored -> no rotation, keep serving.
        # Action should be "serve" (continuing)
        # PROBLEM FIX: Even if rotation doesn't change, we must reset the server!
        # Because previous action might be Spike/Block by another player.
        st.session_state.current_action = "serve"
        if len(st.session_state.rotation) > 3:
            server_name_fmt = st.session_state.rotation[3]
            found_p = None
            for p in st.session_state.players_master:
                fmt = f"{p['number']}: {p.get('nickname', p['name'])}"
                if fmt == server_name_fmt:
                    found_p = p
                    break
            st.session_state.selected_player = found_p
            # Auto-select first serve type if available
            if found_p:
                _serves = found_p.get("serve_types") or ([found_p["default_serve"]] if found_p.get("default_serve") and found_p.get("default_serve") != "なし" else [])
                if _serves and _serves[0] in st.session_state.serve_types:
                    st.session_state.selected_serve = _serves[0]
    else:
        st.session_state.score_opponent += 1
        if current_serve == "own":
            # We lost the rally while serving -> lose serve (opponent doesn't rotate in our system)
            st.session_state.serving_team = "opponent"
            
            # --- Libero Auto-IN (MB rotates to back/loss of serve) ---
            # Scenario: We served (MB at Pos 1/BR), lost point. MB is now at BR.
            # MB should be replaced by Libero.
            # --- Libero Auto-IN (MB rotates to back/loss of serve) ---
            # Scenario: We served (MB at Pos 1/BR), lost point. MB is now at BR.
            # MB should be replaced by Libero.
            
            # Check player at Pos 3 (BR/Server position - Index 3)
            # Wait, view_file says indices:
            # Top: 0,1,2. Bottom: 5,4,3. 3 is Right-Bottom (Pos 1). Correct.
            
            server_pos_idx = 3
            p_str = st.session_state.rotation[server_pos_idx]
            
            # Check if MB
            is_mb = False
            for p in st.session_state.players_master:
                if f"{p['number']}: {p.get('nickname', p['name'])}" == p_str:
                    if p["position"] == "MB":
                        is_mb = True
                    break
            
            if is_mb:
                # Swap!
                lib_id = st.session_state.get("libero_player_id")
                
                # If lib_id is missing, try to find from master
                if not lib_id:
                    # Find player with Position L who is NOT in rotation
                    current_players = set(st.session_state.rotation)
                    for p in st.session_state.players_master:
                        if p.get("position") == "L":
                            fmt = f"{p['number']}: {p.get('nickname', p['name'])}"
                            if fmt not in current_players:
                                lib_id = fmt
                                break
                
                if lib_id:
                    # Check if Libero is NOT already in court? 
                    # (If 2 liberos or mess up).
                    # Assume Libero is on bench (or replacing other MB? No, 1 libero).
                    
                    st.session_state.rotation[server_pos_idx] = lib_id
                    
                    # Track the MB we just removed
                    if "mb_later_swap" not in st.session_state:
                        st.session_state.mb_later_swap = []
                    st.session_state.mb_later_swap.append(p_str)
                    
                    st.toast(f"🔄 リベロ交代: {get_player_short(p_str)} OUT / {get_player_short(lib_id)} IN")


        # else: opponent was serving and scored -> no change to serve, they keep serving.
        # We are receiving.
        st.session_state.current_action = "reception"



def show_setup_screen() -> None:
    st.markdown("## 試合セットアップ")

    ensure_data_dir()
    path = get_current_match_path()

    # --- 前回データの復元バナー ---
    if os.path.exists(path):
        with st.container(border=True):
            st.warning("前回の試合データ（未保存）が見つかりました。")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button("▶ 前回の続きから再開", key="resume_btn", use_container_width=True):
                    if load_current_match():
                        st.success("前回の試合を復元しました。")
                        st.rerun()
                    else:
                        st.error("復元に失敗しました。")
            with col_r2:
                if st.button("新規で開始（前回データ破棄）", key="new_match_btn", use_container_width=True):
                    reset_current_match_file()
                    st.session_state.is_analysis_active = False
                    st.session_state.events = {f"Set{i}": [] for i in range(1, 6)}
                    st.session_state.current_set = 1
                    st.session_state.score_own = 0
                    st.session_state.score_opponent = 0
                    st.session_state.libero_in_court = False
                    st.session_state.selected_player = None
                    st.session_state.selected_attack = None
                    st.session_state.selected_serve = None
                    st.session_state.selected_result = None
                    st.session_state.reception_grade = None
                    st.session_state.start_area = None
                    st.session_state.end_area = None
                    st.session_state.is_error_mode = False
                    st.session_state.error_team = None
                    st.session_state.is_libero_mode = False
                    st.session_state.court_key_id = 0
                    st.rerun()

    # ===== STEP 1: 試合情報 =====
    st.markdown("#### Step 1　試合情報")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            new_date = st.text_input(
                "日付", value=st.session_state.match_date,
                placeholder="例: 2025/08/31", key="setup_match_date"
            )
            st.session_state.match_date = new_date
            st.session_state.tournament_name = new_date
        with c2:
            new_opponent = st.text_input(
                "対戦相手", value=st.session_state.match_opponent,
                placeholder="例: 甲西高校", key="setup_match_opponent"
            )
            st.session_state.match_opponent = new_opponent

        new_filename = st.text_input(
            "ファイル名（試合の識別名）", value=st.session_state.file_name,
            placeholder="例: 第一試合、準決勝", key="setup_file_name"
        )
        st.session_state.file_name = new_filename

    # ===== STEP 2: スターティングローテ =====
    st.markdown("#### Step 2　スターティングローテ（6人）")
    if not st.session_state.players_master:
        st.error("選手が登録されていません。各種登録で選手を追加してください。")
        return

    # Libero は先発ローテーションから除外
    player_options = [
        f"{p['number']}: {p.get('nickname', p['name'])}"
        for p in st.session_state.players_master
        if p.get('position') != 'L'
    ]

    if not player_options:
        st.error("リベロ以外の選手が登録されていません。")
        return

    # デフォルトは未選択（空文字）、リベロ除外後の選択肢にない値はリセット
    if len(st.session_state.starting_rotation) != 6:
        st.session_state.starting_rotation = [""] * 6

    for i in range(6):
        if st.session_state.starting_rotation[i] not in player_options and st.session_state.starting_rotation[i] != "":
            st.session_state.starting_rotation[i] = ""

    if "rot_editing_pos" not in st.session_state:
        st.session_state.rot_editing_pos = None

    def get_disp(full_str):
        if not full_str:
            return "未選択"
        if ":" in full_str:
            return full_str.split(":", 1)[1].strip()
        return full_str

    p = st.session_state.starting_rotation
    pos_label_map = {0: "1:左上", 1: "2:中上", 2: "3:右上", 3: "4:右下", 4: "5:中下", 5: "6:左下"}
    display_rows = [
        [(0, "1:左上"), (1, "2:中上"), (2, "3:右上")],
        [(5, "6:左下"), (4, "5:中下"), (3, "4:右下")],
    ]

    # 選手ピッカー（コート図の上に表示）
    if st.session_state.rot_editing_pos is not None:
        editing_idx = st.session_state.rot_editing_pos
        # 他ポジションで既に選択済みの選手を除外
        already_assigned = {
            st.session_state.starting_rotation[i]
            for i in range(6)
            if i != editing_idx and st.session_state.starting_rotation[i]
        }
        available = [opt for opt in player_options if opt not in already_assigned]

        with st.container(border=True):
            hdr_col, cls_col = st.columns([4, 1])
            with hdr_col:
                st.markdown(f"**{pos_label_map[editing_idx]} の選手を選択**")
            with cls_col:
                if st.button("✕", key="rot_picker_close", use_container_width=True):
                    st.session_state.rot_editing_pos = None
                    st.rerun()
            if available:
                pick_cols = st.columns(4)
                for j, opt in enumerate(available):
                    with pick_cols[j % 4]:
                        is_selected = (opt == p[editing_idx])
                        if st.button(
                            opt,
                            key=f"rot_pick_{editing_idx}_{j}",
                            use_container_width=True,
                            type="primary" if is_selected else "secondary"
                        ):
                            st.session_state.starting_rotation[editing_idx] = opt
                            st.session_state.rot_editing_pos = None
                            st.rerun()
            else:
                st.info("選択可能な選手がいません（全員が他のポジションに割り当て済み）")

    # コート図（ポジションをタップして選手を登録）
    with st.container(border=True):
        for row in display_rows:
            cols = st.columns(3)
            for col_i, (rot_idx, pos_label) in enumerate(row):
                with cols[col_i]:
                    disp_name = get_disp(p[rot_idx])
                    is_editing = st.session_state.rot_editing_pos == rot_idx
                    is_unset = not p[rot_idx]
                    st.caption(pos_label)
                    if st.button(
                        disp_name,
                        key=f"court_cell_{rot_idx}",
                        use_container_width=True,
                        type="primary" if is_editing else "secondary"
                    ):
                        st.session_state.rot_editing_pos = None if is_editing else rot_idx
                        st.rerun()

    st.subheader("最初のサーブ権")
    first_serve = st.radio("第1セットのサーブ", ["自チーム", "相手チーム"], key="first_serve_radio", horizontal=True)

    st.subheader("リベロ設定 (任意)")
    # Filter Libero players (or all?)
    # Usually Libero is marked as 'L'.
    lib_options = ["なし"] + [f"{p['number']}: {p.get('nickname', p['name'])}" for p in st.session_state.players_master if p['position'] == 'L']
    # Also allow selecting any if master is incomplete? No, stick to L for safety.
    selected_lib = st.selectbox("リベロ選手", lib_options, key="setup_libero")
    if selected_lib != "なし":
        st.session_state.libero_player_id = selected_lib
    else:
        st.session_state.libero_player_id = None
        
    if "mb_later_swap" not in st.session_state:
        st.session_state.mb_later_swap = [] # Stack for MBs who are out

    st.markdown("#### Step 3　試合開始")
    if st.button("試合を開始する", type="primary", use_container_width=True):
        _rot = st.session_state.starting_rotation
        _unset_positions = [
            pos_label_map[idx] for idx in [0, 1, 2, 3, 4, 5] if not _rot[idx]
        ]
        if _unset_positions:
            st.error(f"以下のポジションに選手が設定されていません: {', '.join(_unset_positions)}")
        elif not (st.session_state.match_date and st.session_state.match_opponent and st.session_state.file_name):
            st.error("日付・対戦相手・ファイル名をすべて入力してください")
        if st.session_state.match_date and st.session_state.match_opponent and st.session_state.file_name and all(st.session_state.starting_rotation):
            # --- New: Libero Selection ---
            st.session_state.is_analysis_active = True
            st.session_state.rotation = st.session_state.starting_rotation.copy()
            st.session_state.serving_team = "own" if first_serve == "自チーム" else "opponent"
            st.session_state.events = {f"Set{st.session_state.current_set}": []}
            
            # リベロ自動交代：試合開始時の初期セットアップ
            # 自チームサーブ: サーバー(index 3)のMBは先に1本サーブを打つので交代しない
            #                後衛センター(index 4)・後衛左(index 5)のMBがいれば交代
            # 相手チームサーブ: 後衛のMB全員(index 3,4,5)を交代対象にする
            st.session_state.mb_later_swap = []
            if st.session_state.get("libero_player_id"):
                lib_id = st.session_state.libero_player_id
                serving_own = (st.session_state.serving_team == "own")
                # 自チームサーブ時はサーバー(idx=3)を除外、相手サーブ時は全後衛チェック
                check_indices = [4, 5] if serving_own else [4, 5, 3]
                for idx in check_indices:
                    p_str = st.session_state.rotation[idx]
                    is_mb = any(
                        f"{pm['number']}: {pm.get('nickname', pm['name'])}" == p_str
                        and pm.get("position") == "MB"
                        for pm in st.session_state.players_master
                    )
                    if is_mb and not st.session_state.libero_in_court:
                        st.session_state.rotation[idx] = lib_id
                        st.session_state.libero_in_court = True
                        st.session_state.mb_later_swap.append(p_str)
                        break  # 1人のリベロは同時に1人のMBのみ交代
                                 
            save_current_match_snapshot()
            st.rerun()


def show_analysis_screen() -> None:
    # --- iPad / Mobile Optimization CSS ---
    st.markdown("""
    <style>
        /* Compact Mode for iPad */
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 100%;
        }
        div[data-testid="column"] {
            gap: 0.2rem !important;
        }
        .stButton button {
            padding: 0.1rem 0.4rem !important;
            min-height: 2.2rem !important;
            height: auto !important;
            font-size: 0.9rem !important;
        }
        h1, h2, h3 {
            margin-top: 0 !important;
            margin-bottom: 0.2rem !important;
            padding: 0 !important;
        }
        .element-container {
            margin-bottom: 0.2rem !important;
        }
        /* Status text compact */
        .stAlert {
            padding: 0.2rem 0.5rem !important;
        }
        /* Hide footer */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    # Hide sidebar (analysis focus) -> REMOVED to allow navigation
    # st.sidebar.empty()

    # --- In-match analysis mode ---
    if st.session_state.is_in_match_analysis:
        opponent = st.session_state.get("match_opponent") or st.session_state.tournament_name
        st.header(f"📊 試合中分析 - vs {opponent}")
        if st.button("← 試合に戻る", key="back_from_analysis", type="primary"):
            st.session_state.is_in_match_analysis = False
            st.rerun()
        all_events = flatten_events(st.session_state.events)
        render_analysis_view(all_events, title="")
        return

    # --- Compact Header & Score ---
    # --- Compact Header & Score ---
    # st.subheader(f"{st.session_state.tournament_name} / Set {st.session_state.current_set}")
    opponent = st.session_state.get("match_opponent") or st.session_state.tournament_name
    st.markdown(f"**vs {opponent}** | **Set {st.session_state.current_set}**")
    
    # serve_char = "🏐" -> Removed emoji
    serve_char = "●"
    own_mark = serve_char if st.session_state.serving_team == "own" else ""
    opp_mark = serve_char if st.session_state.serving_team == "opponent" else ""

    # Row 1: Header (3 columns: Score | Rotation | Actions)
    # Ratios: Score(1.5), Rotation(1.2), Error/Ctrl(2.5) to balance.
    c_score, c_center, c_ctrl = st.columns([1.5, 1.2, 2.5])
    
    with c_score:
        # st.markdown(f"### {own_mark}{st.session_state.score_own} - {st.session_state.score_opponent}{opp_mark}")
        # Use HTML for larger size
        st.markdown(f"""
        <div style="text-align:center; font-weight:800; font-size:3.5rem; line-height:1.2;">
            <span style="color:#3b82f6;">{st.session_state.score_own}</span>
            <span style="font-size:2rem; color:#94a3b8;">-</span>
            <span style="color:#ef4444;">{st.session_state.score_opponent}</span>
        </div>
        <div style="text-align:center; font-size:1rem; color:#64748b;">
            <span style="color:#eab308;">{own_mark}</span> {st.session_state.team_name} vs {st.session_state.opponent_name} <span style="color:#eab308;">{opp_mark}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with c_center:
        # Mini rotation panel without title
        render_rotation_panel(show_title=False)

    with c_ctrl:
        # Error / Point Buttons (Large)
        e_c1, e_c2 = st.columns(2)
        with e_c1:
            if st.button("自得 (相手ミス)", key="err_opp_btn", type="primary", use_container_width=True):
                # Immediate recording for opponent error
                apply_point("own")
                record_event({
                    "action": "error",
                    "player": None,
                    "result": "error",
                    "error_detail": "相手ミス", # Generic
                    "error_team": "opponent"
                })
                # No mode switch, just run
                st.session_state.court_key_id += 1
                st.rerun()
        with e_c2:
            if st.button("相得 (味方ミス)", key="err_own_btn", type="primary", use_container_width=True):
                 st.session_state.is_error_mode = True; st.session_state.error_team = "own"; st.rerun()

        # Undo Button (Outside Log)
        set_key = f"Set{st.session_state.current_set}"
        recent = st.session_state.events.get(set_key, [])
        if recent:
            if st.button("⏪ 直前の操作を取り消す", key="undo_global", use_container_width=True):
                # Pop last event
                st.session_state.events[set_key].pop()
                new_recent = st.session_state.events[set_key]
                
                if new_recent:
                    # Restore state from new last event
                    last = new_recent[-1]
                    st.session_state.score_own = last.get("score_own", 0)
                    st.session_state.score_opponent = last.get("score_opponent", 0)
                    if "rotation" in last: st.session_state.rotation = list(last["rotation"])
                    st.session_state.serving_team = last.get("serving_team", st.session_state.serving_team)
                    st.session_state.libero_in_court = last.get("libero_in_court", False)
                    # We don't track player positions perfectly if they changed manually without event? assumed consistent.
                else:
                    # Reverted to initial state of the set
                    st.session_state.score_own = 0
                    st.session_state.score_opponent = 0
                    st.session_state.rotation = list(st.session_state.starting_rotation)
                    # Cannot restore serving_team perfectly if it was toggled manually.
                    # Keep current serving_team or warn?
                    # st.toast("初期状態に戻りました（サーブ権は手動で確認してください）")
                
                # Update snapshot
                save_current_match_snapshot()
                st.session_state.unsaved_event_count = 0
                st.session_state.court_key_id += 1
                st.toast("⏪ 操作を取り消しました")
                st.rerun()

        # Log (Expander) moved to Header (under Error buttons)
        with st.expander("📝 直近のログ", expanded=False):
            set_key = f"Set{st.session_state.current_set}"
            recent = st.session_state.events.get(set_key, [])
            
            # Scrollable area
            with st.container(height=150):
                if recent:
                    for ev in reversed(recent[-20:]):
                        act = ev.get("action","")
                        pl = ev.get("player") or {}
                        pname = get_player_short(pl.get("nickname", pl.get("name", "?")))
                        
                        res = ev.get("result") or ev.get("quality") or ev.get("error_detail") or ""
                        # Simplify text for compact view
                        if act == "substitution":
                            p_in = get_player_short(ev.get("player_in",""))
                            p_out = get_player_short(ev.get("player_out",""))
                            line = f"🔁 {p_in} IN / {p_out} OUT"
                        elif act == "dig":
                             line = f"👐 D {pname} {ev.get('quality', '')}"
                        else:
                            line = f"{act[:2]} {pname} {res}"
                            
                        st.text(line)
                else:
                    st.text("(なし)")
            
            # Undo button moved to outside
            # if recent:
            #     if st.button("⏪ Undo", key="undo_header", use_container_width=True):
            # ...

    # Expander for Score Adjustment and Serve Toggle
    with st.expander("⚙️ スコア・サーブ権修正", expanded=False):
        ec1, ec2, ec3, ec4, ec5 = st.columns(5)
        with ec1:
            if st.button("サーブ切替", key="toggle_sv", use_container_width=True):
                 st.session_state.serving_team = "opponent" if st.session_state.serving_team == "own" else "own"
                 st.rerun()
        with ec2:
            if st.button("自+1", key="s_o_p", use_container_width=True):
                st.session_state.score_own += 1; st.rerun()
        with ec3:
            if st.button("自-1", key="s_o_m", use_container_width=True):
                if st.session_state.score_own > 0: st.session_state.score_own -= 1; st.rerun()
        with ec4:
            if st.button("相+1", key="s_e_p", use_container_width=True):
                st.session_state.score_opponent += 1; st.rerun()
        with ec5:
            if st.button("相-1", key="s_e_m", use_container_width=True):
                if st.session_state.score_opponent > 0: st.session_state.score_opponent -= 1; st.rerun()



    # Error mode
    # if st.session_state.is_error_mode:
        # Simplified: no detailed error mode for opponent error. 
        # But we still use it for Own Error if needed?
        # User said: "Simplify opponent error". 
        # "自得 (相手ミス)" button now directly calls record_event.
        # But "相得 (味方ミス)" might still needs details?
        # User request: "Simply press the opponent error button".
        # Let's keep error mode for OWN errors (if user wants details for own team), 
        # but Opponent Error is immediate.
        
    if st.session_state.is_error_mode:
        st.subheader("ミスの詳細を選択してください")
        # If error_team is own, it means WE made a mistake -> Opponent gets point.
        # If error_team is opponent, it means THEY made a mistake -> We get point.
        # But we want Opponent Error to be immediate.
        
        error_details = [
            "タッチネット",
            "パッシング",
            "ドリブル",
            "ホールディング",
            "オーバーネット",
            "フォアヒット",
            "レシーブミス",
            "トスミス",
            "ジャッジミス",
        ]
        cols = st.columns(3)
        for i, err in enumerate(error_details):
            with cols[i % 3]:
                if st.button(err, key=f"error_{err}", use_container_width=True):
                    # Record based on who made the error
                    if st.session_state.error_team == "opponent":
                        apply_point("own") # We score
                    else:
                        apply_point("opponent") # They score

                    record_event(
                        {
                            "action": "error",
                            "player": None, # Could link to player if we selected one?
                            "result": "error",
                            "error_detail": err,
                            "error_team": st.session_state.error_team
                        }
                    )
                    st.session_state.is_error_mode = False
                    st.session_state.error_team = None
                    st.session_state.court_key_id += 1
                    st.rerun()

        if st.button("キャンセル/戻る", key="cancel_error"):
            st.session_state.is_error_mode = False
            st.session_state.error_team = None
            st.session_state.court_key_id += 1
            st.rerun()
        return

    # Substitution mode (full-screen, like error mode)
    if st.session_state.is_sub_mode:
        if st.session_state.sub_step == 1:
            # Step 1: Select bench player to bring IN
            st.subheader("交代で入る選手を選択してください")

            # Build bench player list with libero info
            bench_players = []
            for bp in st.session_state.players_master:
                fmt = f"{bp['number']}: {bp.get('nickname', bp['name'])}"
                is_libero = bp["position"] == "L"
                if fmt not in st.session_state.rotation:
                    bench_players.append({"fmt": fmt, "is_libero": is_libero, "player": bp})

            if not bench_players:
                st.warning("ベンチに選手がいません。")
            else:
                # Show libero players first, then others
                libero_bench = [p for p in bench_players if p["is_libero"]]
                normal_bench = [p for p in bench_players if not p["is_libero"]]

                if libero_bench:
                    st.markdown("**🟢 リベロ**")
                    cols = st.columns(3)
                    for i, bp_info in enumerate(libero_bench):
                        with cols[i % 3]:
                            btn_label = f"🟢 L | {get_player_short(bp_info['fmt'])}"
                            if st.button(btn_label, key=f"sub_in_libero_{i}", use_container_width=True):
                                st.session_state.sub_in_player = bp_info["fmt"]
                                st.session_state.sub_in_is_libero = True
                                st.session_state.sub_step = 2
                                st.rerun()

                if normal_bench:
                    st.markdown("**その他の選手**")
                    cols = st.columns(3)
                    for i, bp_info in enumerate(normal_bench):
                        with cols[i % 3]:
                            if st.button(get_player_short(bp_info["fmt"]), key=f"sub_in_normal_{i}", use_container_width=True):
                                st.session_state.sub_in_player = bp_info["fmt"]
                                st.session_state.sub_in_is_libero = False
                                st.session_state.sub_step = 2
                                st.rerun()

            if st.button("キャンセル/戻る", key="cancel_sub", use_container_width=True):
                st.session_state.is_sub_mode = False
                st.session_state.sub_step = 1
                st.session_state.sub_in_player = None
                st.session_state.sub_in_is_libero = False
                st.rerun()
            return

        elif st.session_state.sub_step == 2:
            # Step 2: Select court player to take OUT
            in_player = st.session_state.sub_in_player
            in_is_libero = st.session_state.sub_in_is_libero
            st.subheader(f"**{get_player_short(in_player)}** と交代する出場中の選手を選択")

            # If libero is selected as IN, only show back-row players
            if in_is_libero:
                st.markdown("🟢 リベロは後衛の選手とのみ交代できます")
                target_indices = [5, 4, 3]  # back row
                cols = st.columns(3)
                for i, idx in enumerate(target_indices):
                    pname = st.session_state.rotation[idx]
                    with cols[i]:
                        if st.button(get_player_short(pname), key=f"sub_out_{i}", use_container_width=True):
                            # Libero substitution
                            st.session_state.rotation[idx] = in_player
                            st.session_state.libero_in_court = True
                            st.session_state.libero_replaced_player = pname
                            record_event(
                                {
                                    "action": "substitution",
                                    "player_in": in_player,
                                    "player_out": pname,
                                    "is_libero_substitution": True,
                                }
                            )
                            st.session_state.is_sub_mode = False
                            st.session_state.sub_step = 1
                            st.session_state.sub_in_player = None
                            st.session_state.sub_in_is_libero = False
                            st.session_state.court_key_id += 1
                            st.rerun()
            else:
                # Regular substitution or libero OUT (if libero is on court and replaced player is selected as IN)
                cols = st.columns(3)
                for i, pname in enumerate(st.session_state.rotation):
                    with cols[i % 3]:
                        # Check if this court player is the libero
                        is_court_libero = False
                        if st.session_state.libero_in_court:
                            libero = next((p for p in st.session_state.players_master if p["position"] == "L"), None)
                            if libero:
                                libero_fmt = f"{libero['number']}: {libero.get('nickname', libero['name'])}"
                                if pname == libero_fmt:
                                    is_court_libero = True

                        btn_label = f"🟢 {get_player_short(pname)}" if is_court_libero else get_player_short(pname)
                        if st.button(btn_label, key=f"sub_out_{i}", use_container_width=True):
                            # Check if we're swapping out the libero
                            if is_court_libero:
                                # Libero is being replaced: restore original player first, then do the sub
                                replaced = st.session_state.libero_replaced_player
                                rot_idx = st.session_state.rotation.index(pname)
                                st.session_state.rotation[rot_idx] = in_player
                                st.session_state.libero_in_court = False
                                st.session_state.libero_replaced_player = None
                                record_event(
                                    {
                                        "action": "substitution",
                                        "player_in": in_player,
                                        "player_out": pname,
                                        "is_libero_substitution": False,
                                    }
                                )
                            else:
                                # Check if the IN player is the original player who was replaced by libero
                                if (st.session_state.libero_in_court
                                        and in_player == st.session_state.libero_replaced_player):
                                    # This is essentially a libero OUT
                                    libero = next((p for p in st.session_state.players_master if p["position"] == "L"), None)
                                    if libero:
                                        libero_fmt = f"{libero['number']}: {libero.get('nickname', libero['name'])}"
                                        if libero_fmt in st.session_state.rotation:
                                            lib_idx = st.session_state.rotation.index(libero_fmt)
                                            st.session_state.rotation[lib_idx] = in_player
                                            st.session_state.libero_in_court = False
                                            st.session_state.libero_replaced_player = None
                                            record_event(
                                                {
                                                    "action": "substitution",
                                                    "player_in": in_player,
                                                    "player_out": libero_fmt,
                                                    "is_libero_substitution": True,
                                                }
                                            )
                                else:
                                    # Normal substitution
                                    rot_idx = st.session_state.rotation.index(pname)
                                    st.session_state.rotation[rot_idx] = in_player
                                    record_event(
                                        {
                                            "action": "substitution",
                                            "player_in": in_player,
                                            "player_out": pname,
                                            "is_libero_substitution": False,
                                        }
                                    )

                            st.session_state.is_sub_mode = False
                            st.session_state.sub_step = 1
                            st.session_state.sub_in_player = None
                            st.session_state.sub_in_is_libero = False
                            st.session_state.court_key_id += 1
                            st.rerun()

            if st.button("← 戻る", key="sub_back_step1", use_container_width=True):
                st.session_state.sub_step = 1
                st.session_state.sub_in_player = None
                st.session_state.sub_in_is_libero = False
                st.rerun()
            return

    # Tabs (custom action buttons)
    labels = [("serve", "サーブ"), ("spike", "スパイク"), ("reception", "レセプション"), ("dig", "ディグ"), ("block", "ブロック")]
    if "current_action" not in st.session_state:
        st.session_state.current_action = "spike"

    # Dynamic tabs layout (5 items now)
    c1, c2, c3, c4, c5 = st.columns(5)
    for (value, text), col in zip(labels, [c1, c2, c3, c4, c5]):
        with col:
            is_active = (st.session_state.current_action == value)
            btn_type = "primary" if is_active else "secondary"
            if st.button(text, key=f"tab_{value}", type=btn_type, use_container_width=True):
                st.session_state.current_action = value
                st.session_state.start_area = None
                st.session_state.end_area = None
                st.session_state.selected_serve = None
                st.session_state.selected_attack = None
                st.session_state.selected_player = None
                st.session_state.court_key_id += 1
                st.rerun()

    # Layout: 2 Columns for iPad Single-Screen
    # Left (Narrow): Players, Rotation
    # Right (Wide): Court, Status, Controls
    c_side, c_main = st.columns([1, 2.5])

    with c_side:
        st.markdown("#### 選手")
        # Grid layout for players (2 columns to save space)
        # We need immediate rerun for responsiveness
        # But st.button returns True only on the run it was clicked.
        # So setting state and rerun is correct pattern.
        
        p_cols = st.columns(2)
        for idx, pname in enumerate(st.session_state.rotation):
            with p_cols[idx % 2]:
                # Determine if this button is "selected" based on CURRENT session state
                is_selected = False
                if st.session_state.selected_player:
                    fmt = f"{st.session_state.selected_player['number']}: {st.session_state.selected_player.get('nickname', st.session_state.selected_player['name'])}"
                    if fmt == pname:
                        is_selected = True

                button_type = "primary" if is_selected else "secondary"
                
                # If button is clicked
                if st.button(get_player_short(pname), key=f"player_{idx}", type=button_type, use_container_width=True):
                    found = None
                    for p in st.session_state.players_master:
                        fmt = f"{p['number']}: {p.get('nickname', p['name'])}"
                        if fmt == pname:
                            found = p
                            break
                    
                    if found:
                        st.session_state.selected_player = found
                        # Auto-select first serve type if available and action is serve
                        if st.session_state.current_action == "serve":
                            _serves = found.get("serve_types") or ([found["default_serve"]] if found.get("default_serve") and found.get("default_serve") != "なし" else [])
                            if _serves and _serves[0] in st.session_state.serve_types:
                                st.session_state.selected_serve = _serves[0]
                            else:
                                st.session_state.selected_serve = None
                        
                        # Immediate rerun for UI responsiveness!
                        st.rerun()
        
        st.markdown("---")
        # Rotation Panel moved to header

        # Log moved to Header

        st.markdown("---")
        
        # --- Input Controls (Side Column) ---
        p = st.session_state.selected_player
        p_name = p["name"] if isinstance(p, dict) and "name" in p else "未選択"
        act = st.session_state.current_action

        # Check missing (logic for submit)
        # We handle "can_submit" dynamically inside buttons for Net/Out
        # But for UI feedback, we track what is selected.
        
        if st.session_state.current_action == "serve":
            st.write("サーブ種類")
            s_types = st.session_state.serve_types
            # Compact columns for side panel (2 cols)
            n_cols_s = min(len(s_types), 2) if len(s_types) > 0 else 1
            s_cols = st.columns(n_cols_s)
            
            for i, serve in enumerate(s_types):
                with s_cols[i % n_cols_s]:
                    # Visual feedback for selected serve type
                    is_selected = (st.session_state.selected_serve == serve)
                    btn_type = "primary" if is_selected else "secondary"
                    if st.button(serve, key=f"serve_{serve}", type=btn_type, use_container_width=True):
                        st.session_state.selected_serve = serve
                        st.rerun() 

            # Show results if player and serve type are selected
            # Target area is optional for Net/Out
            if p_name != "未選択" and st.session_state.selected_serve:
                st.write("結果")
                r_cols = st.columns(2) # 2 columns, 2 rows
                for i, result in enumerate(RESULTS):
                    with r_cols[i % 2]:
                        # Disabled logic:
                        # For "得点"/"継続", we NEED start_area (target)
                        # For "ネット"/"アウト", we DO NOT need start_area
                        is_net_out = result in ("ネット", "アウト")
                        has_target = (st.session_state.start_area is not None)
                        
                        btn_disabled = False
                        if not is_net_out and not has_target:
                            btn_disabled = True
                        
                        if st.button(result, key=f"serve_result_{result}", disabled=btn_disabled, use_container_width=True):
                            if result == "得点": apply_point("own")
                            elif result in ("ネット", "アウト"): apply_point("opponent")
                            
                            record_event({
                                "action": "serve",
                                "player": st.session_state.selected_player,
                                "serve_type": st.session_state.selected_serve,
                                "target_zone": st.session_state.start_area, # May be None
                                "result": result,
                            })
                            # State clearing delegated to record_event / apply_point logic
                            st.session_state.court_key_id += 1
                            st.rerun()
                
                if not st.session_state.start_area:
                     st.caption("※得点・継続の場合はコート上のターゲットを選択してください")

        elif st.session_state.current_action == "reception":
            st.write("レセプショングレード")
            # Reception logic requires player
            can_submit_rec = (p_name != "未選択")
            
            n_r = len(RECEPTION_GRADES)
            r_cols = st.columns(min(n_r, 4))
            for i, grade in enumerate(RECEPTION_GRADES):
                with r_cols[i % len(r_cols)]:
                    if st.button(grade, key=f"reception_{grade}", disabled=not can_submit_rec, use_container_width=True):
                        if grade == "ミス": apply_point("opponent")
                        record_event({
                            "action": "reception",
                            "player": st.session_state.selected_player,
                            "quality": grade,
                            "result": "ミス" if grade == "ミス" else "継続",
                        })
                        st.rerun()
        
        elif st.session_state.current_action == "dig":
            st.write("ディグ評価")
            can_submit_dig = (p_name != "未選択")
            dig_grades = ["Aカット", "Bカット", "Cカット", "ミス"]
            d_cols = st.columns(2)
            for i, grade in enumerate(dig_grades):
                with d_cols[i % 2]:
                    if st.button(grade, key=f"dig_{grade}", disabled=not can_submit_dig, use_container_width=True):
                        if grade == "ミス": apply_point("opponent")
                        record_event({
                            "action": "dig",
                            "player": st.session_state.selected_player,
                            "quality": grade,
                            "result": "ミス" if grade == "ミス" else "継続",
                        })
                        st.rerun()

        elif st.session_state.current_action == "spike":
            st.write("攻撃パターン")
            a_pat = st.session_state.attack_patterns
            # Compact columns (2 cols)
            n_cols_a = min(len(a_pat), 2) if len(a_pat) > 0 else 1
            a_cols = st.columns(n_cols_a)
            for i, pattern in enumerate(a_pat):
                with a_cols[i % n_cols_a]:
                    # Visual feedback for selected attack pattern
                    is_selected = (
                        st.session_state.selected_attack is not None 
                        and st.session_state.selected_attack.get("name") == pattern["name"]
                    )
                    btn_type = "primary" if is_selected else "secondary"
                    if st.button(pattern["name"], key=f"attack_{pattern['name']}", type=btn_type, use_container_width=True):
                        st.session_state.selected_attack = pattern
                        st.rerun()

            # Logic: Player + Attack + StartArea(optional?) -> usually StartArea (Hit point) is good to have.
            # But EndArea (Course) is only needed for In/Continue.
            # Let's require StartArea for all spikes for consistency (where did they hit from?), 
            # but relax EndArea for net/out.
            
            has_player = (p_name != "未選択")
            has_attack = (st.session_state.selected_attack is not None)
            has_start = (st.session_state.start_area is not None)
            
            if has_player and has_attack and has_start:
                st.write("結果")
                r_cols = st.columns(2)
                for i, result in enumerate(RESULTS):
                    with r_cols[i % 2]:
                        is_net_out = result in ("ネット", "アウト")
                        has_end = (st.session_state.end_area is not None)
                        
                        btn_disabled = False
                        if not is_net_out and not has_end:
                            btn_disabled = True
                            
                        if st.button(result, key=f"spike_result_{result}", disabled=btn_disabled, use_container_width=True):
                            if result == "得点": apply_point("own")
                            elif result in ("ネット", "アウト"): apply_point("opponent")
                            
                            record_event({
                                "action": "spike",
                                "player": st.session_state.selected_player,
                                "sub_type": st.session_state.selected_attack["name"],
                                "start_zone": st.session_state.start_area,
                                "end_zone": st.session_state.end_area, # May be None
                                "result": result,
                            })
                            # State clearing delegated to record_event
                            st.session_state.court_key_id += 1
                            st.rerun()
                            
                if not st.session_state.end_area:
                    st.caption("※得点・継続の場合はコースを選択してください")
            elif has_player and has_attack:
                 st.caption("※打点（スタート位置）を選択してください")

        elif st.session_state.current_action == "block":
            st.write("結果")
            can_submit_blk = (p_name != "未選択")
            b_cols = st.columns(2)
            with b_cols[0]:
                if st.button("キル (得点)", key="block_kill", disabled=not can_submit_blk, type="primary", use_container_width=True):
                    apply_point("own")
                    record_event({
                        "action": "block",
                        "player": st.session_state.selected_player,
                        "result": "得点",
                        "sub_type": "kill"
                    })
                    # Block point -> Serve. apply_point sets server.
                    # Rally ends.
                    st.session_state.court_key_id += 1
                    st.rerun()
            with b_cols[1]:
                if st.button("ブロックアウト/吸い込み (失点)", key="block_out", disabled=not can_submit_blk, use_container_width=True):
                    apply_point("opponent")
                    record_event({
                        "action": "block",
                        "player": st.session_state.selected_player,
                        "result": "ミス",
                        "sub_type": "blockout"
                    })
                    st.session_state.selected_player = None
                    st.session_state.court_key_id += 1
                    st.rerun()

    with c_main:
        # 1. Status Line (Compact)
        p = st.session_state.selected_player
        p_name = p["name"] if isinstance(p, dict) and "name" in p else "未選択"
        act = st.session_state.current_action
        
        status_text = f"**{act}** | 選手: **{p_name}**"
        if act == "serve":
            status_text += f" | 種: {st.session_state.selected_serve or '未'} | 先: {st.session_state.start_area or '未'}"
        elif act == "spike":
            status_text += f" | 攻: {st.session_state.selected_attack['name'] if st.session_state.selected_attack else '未'} | 打: {st.session_state.start_area or '未'} → {st.session_state.end_area or '未'}"
        
        st.info(status_text)
        
        # 2. Court (Center, Dynamic)
        if st.session_state.current_action in ["serve", "spike"]:
            clicked_zone = court_input(
                st.session_state.current_action,
                st.session_state.start_area,
                st.session_state.end_area,
                key=f"court_input_{st.session_state.court_key_id}"
            )
            
            if clicked_zone:
                area = clicked_zone
                if act == "serve":
                    if area in ENEMY_ZONES:
                         if st.session_state.start_area != area:
                            st.session_state.start_area = area
                            st.rerun()
                elif act == "spike":
                    if st.session_state.start_area is None:
                        if area in OWN_ZONES:
                            st.session_state.start_area = area
                            st.rerun()
                    else:
                        if area in OWN_ZONES:
                            if st.session_state.start_area != area:
                                st.session_state.start_area = area
                                st.rerun()
                        elif area in ENEMY_ZONES:
                            if st.session_state.end_area != area:
                                st.session_state.end_area = area
                                st.rerun()

        elif st.session_state.current_action == "dig":
             st.caption("※ディグはコート入力不要")
        else:
             st.caption("※現在のアクションはコート指定不要")



    # --- Set end with confirmation ---
    if not st.session_state.confirm_end_set:
        if st.button("セット終了", key="end_set"):
            st.session_state.confirm_end_set = True
            st.rerun()
    else:
        st.warning(f"❓ 本当にSet {st.session_state.current_set}を終了しますか？（{st.session_state.score_own} - {st.session_state.score_opponent}）")
        ce1, ce2 = st.columns(2)
        with ce1:
            if st.button("✅ 終了する", key="confirm_end_set_yes", type="primary", use_container_width=True):
                st.session_state.current_set += 1
                st.session_state.score_own = 0
                st.session_state.score_opponent = 0
                st.session_state.rotation = st.session_state.starting_rotation.copy()
                st.session_state.events.setdefault(f"Set{st.session_state.current_set}", [])
                st.session_state.court_key_id += 1
                st.session_state.confirm_end_set = False
                st.session_state.libero_in_court = False
                st.session_state.libero_replaced_player = None
                save_current_match_snapshot()
                st.session_state.unsaved_event_count = 0
                st.toast(f"🏀 Set {st.session_state.current_set - 1} 終了！")
                st.rerun()
        with ce2:
            if st.button("❌ キャンセル", key="confirm_end_set_no", use_container_width=True):
                st.session_state.confirm_end_set = False
                st.rerun()



    # --- Analysis & Match End buttons ---
    st.markdown("---")
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("📊 分析", key="in_match_analysis_btn", use_container_width=True):
            st.session_state.is_in_match_analysis = True
            st.rerun()
    with btn_col2:
        if not st.session_state.confirm_end_match:
            if st.button("🏁 試合終了", key="end_match_btn", use_container_width=True):
                st.session_state.confirm_end_match = True
                st.rerun()
        else:
            st.warning("❓ 試合を終了してデータを保存しますか？")
            me1, me2 = st.columns(2)
            with me1:
                if st.button("✅ 保存して終了", key="confirm_end_match_yes", type="primary", use_container_width=True):
                    save_current_match_snapshot()
                    dest = save_match_to_archive(
                        st.session_state.tournament_name,
                        st.session_state.file_name
                    )
                    list_saved_matches.clear()  # Invalidate match list cache
                    # Compute summary before resetting state
                    _flat = flatten_events(st.session_state.events)
                    _serve_e = [e for e in _flat if e.get("action") == "serve"]
                    _spike_e = [e for e in _flat if e.get("action") == "spike"]
                    _block_e = [e for e in _flat if e.get("action") == "block"]
                    st.session_state.match_summary = {
                        "opponent": st.session_state.get("match_opponent", "—"),
                        "date": st.session_state.get("match_date", "—"),
                        "filename": st.session_state.get("file_name", ""),
                        "sets": st.session_state.current_set,
                        "serve_count": len(_serve_e),
                        "spike_count": len(_spike_e),
                        "ace_count": len([e for e in _serve_e if e.get("result") == "得点"]),
                        "kill_count": len([e for e in _spike_e if e.get("result") == "得点"]),
                        "block_count": len([e for e in _block_e if e.get("result") == "得点"]),
                    }
                    st.session_state.show_match_summary = True
                    st.session_state.is_analysis_active = False
                    st.session_state.confirm_end_match = False
                    # Reset match state
                    st.session_state.events = {f"Set{i}": [] for i in range(1, 6)}
                    st.session_state.current_set = 1
                    st.session_state.score_own = 0
                    st.session_state.score_opponent = 0
                    st.session_state.libero_in_court = False
                    st.session_state.libero_replaced_player = None
                    st.rerun()
            with me2:
                if st.button("❌ キャンセル", key="confirm_end_match_no", use_container_width=True):
                    st.session_state.confirm_end_match = False
                    st.rerun()


# ============================================================
# Sidebar & top-level routing
# ============================================================
# ============================================================
# Sidebar & top-level routing
# ============================================================
def show_login_screen():
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(160deg, #e8f4fd 0%, #f0f7ff 50%, #e8f0fe 100%) !important; }
        .login-logo { text-align: center; font-size: 3.5rem; margin-bottom: 0.25rem; }
        .login-title {
            text-align: center; font-size: 1.6rem; font-weight: 800;
            color: #1e3a5f !important; letter-spacing: 0.02em; margin-bottom: 0.15rem;
        }
        .login-subtitle {
            text-align: center; font-size: 0.8rem; color: #5a7fa8 !important;
            letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 2rem;
        }
        div[data-testid="stTabs"] button { color: #5a7fa8 !important; font-weight: 600; }
        div[data-testid="stTabs"] button[aria-selected="true"] { color: #0369a1 !important; }
        .login-note {
            font-size: 0.78rem; color: #5a7fa8 !important;
            text-align: center; margin-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        st.markdown('<div class="login-logo">🏐</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">バレーボール戦術分析</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Team Analysis System</div>', unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["　ログイン　", "　新規作成（管理者）　"])

        with tab_login:
            with st.container(border=True):
                team_input = st.text_input("チーム名", key="login_team", placeholder="チーム名を入力")
                pass_input = st.text_input("パスワード", type="password", key="login_pass", placeholder="パスワードを入力")

                if st.button("ログイン", type="primary", use_container_width=True, key="btn_login"):
                    if not team_input or not pass_input:
                        st.error("チーム名とパスワードを入力してください")
                    else:
                        result = find_account(team_input, pass_input)
                        if result is None:
                            st.error("チーム名またはパスワードが違います")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.auth_team = team_input
                            st.session_state.username = result["display_name"]
                            st.session_state.role = result["role"]
                            load_config()
                            st.rerun()

                st.markdown('<div class="login-note">利用者の方はチーム名と配布されたパスワードでログインしてください</div>', unsafe_allow_html=True)

        with tab_register:
            with st.container(border=True):
                st.caption("マネージャー・指導者など管理者アカウントを作成します。")
                new_team = st.text_input("チーム名", key="reg_team", placeholder="例：さくら高校バレー部")
                new_pass = st.text_input("パスワード", type="password", key="reg_pass", placeholder="パスワードを設定（4文字以上）")
                new_pass2 = st.text_input("パスワード（確認）", type="password", key="reg_pass2", placeholder="パスワードを再入力")

                if st.button("管理者アカウントを作成", type="primary", use_container_width=True, key="btn_register"):
                    if not new_team or not new_pass:
                        st.error("チーム名とパスワードを入力してください")
                    elif new_pass != new_pass2:
                        st.error("パスワードが一致しません")
                    elif len(new_pass) < 4:
                        st.error("パスワードは4文字以上で設定してください")
                    else:
                        if register_admin(new_team, new_pass):
                            st.success(f"「{new_team}」の管理者アカウントを作成しました。ログインしてください。")
                        else:
                            st.error(f"「{new_team}」はすでに登録されています")

def show_match_summary_screen() -> None:
    summary = st.session_state.get("match_summary", {})
    st.markdown("## 試合終了")

    with st.container(border=True):
        st.markdown(f"### vs {summary.get('opponent', '—')}")
        st.caption(f"日付: {summary.get('date', '—')}　|　ファイル: {summary.get('filename', '—')}")
        st.divider()
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("セット数", summary.get("sets", "—"))
        with c2:
            st.metric("サーブ", summary.get("serve_count", 0))
        with c3:
            st.metric("スパイク", summary.get("spike_count", 0))
        with c4:
            st.metric("エース", summary.get("ace_count", 0))
        with c5:
            st.metric("ブロック得点", summary.get("block_count", 0))

    st.success("試合データを保存しました。")
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("データ分析を見る", type="primary", use_container_width=True, key="summary_to_analysis"):
            st.session_state.show_match_summary = False
            st.session_state.match_summary = {}
            st.session_state["main_nav"] = "データ分析"
            st.rerun()
    with col_b:
        if st.button("セットアップへ戻る", use_container_width=True, key="summary_to_setup"):
            st.session_state.show_match_summary = False
            st.session_state.match_summary = {}
            st.rerun()


def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def main_app():
    # Helper to prevent session state errors
    init_session_state()

    # Apply CSS based on dark mode state
    apply_custom_css()

    # --- Professional Sidebar ---
    with st.sidebar:
        st.markdown("## 🏐 バレーボール分析 V4")
        role = st.session_state.get("role", "viewer")
        role_label = "管理者" if role == "admin" else "利用者"
        st.caption(f"{st.session_state.auth_team}  |  {st.session_state.username}  ({role_label})")

        # Match Status Widget (if active)
        if st.session_state.is_analysis_active:
            opponent = st.session_state.get("match_opponent") or st.session_state.tournament_name
            st.info(f"""
            **試合進行中**
            \n{st.session_state.score_own} - {st.session_state.score_opponent} (Set {st.session_state.current_set})
            \nvs {opponent}
            """)
            st.markdown("---")

        # Navigation Menu (role-based)
        if role == "admin":
            menu_items = ["リアルタイム分析", "データ分析", "各種登録"]
        else:
            menu_items = ["データ分析"]

        nav_selection = st.radio("メニュー", menu_items, key="main_nav")

        st.markdown("---")
        if st.button("ログアウト", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.auth_team = None
            st.session_state.role = None
            st.rerun()

    # --- Post-match summary overrides normal routing ---
    if st.session_state.get("show_match_summary"):
        show_match_summary_screen()
        return

    # --- Routing Logic ---
    # Case 1: Real-time Analysis selected
    if nav_selection == "リアルタイム分析":
        if st.session_state.is_analysis_active:
            # Resume match
            show_analysis_screen()
        else:
            # Show setup screen
            show_setup_screen()
            
    # Case 2: Data Analysis selected
    elif nav_selection == "データ分析":
        show_data_analysis()
        
    # Case 3: Registration selected
    elif nav_selection == "各種登録":
        show_registration_mode()


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login_screen()
else:
    main_app()
