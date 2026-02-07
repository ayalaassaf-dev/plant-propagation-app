import html
import pandas as pd
import streamlit as st

# =======================
# הגדרות בסיס
# =======================
st.set_page_config(page_title="טבלת ריבוי צמחים", layout="centered")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGk2pn1I3JZjuhLZbIEWrMfMN02EV_kxuZl2Q3sWxMiRlvLekN-xucADwoy6x9fg/pub?gid=570603705&single=true&output=csv"
TITLE = "טבלת ריבוי צמחים"
SUBTITLE = "מידע לריבוי צמחי גן ונוי"
CREDIT = "המידע נאסף ע״י בועז שחם · האפליקציה הוכנה ע״י אילה אסף"

MONTHS_HE = ["ינו", "פבר", "מרץ", "אפר", "מאי", "יונ", "יול", "אוג", "ספט", "אוק", "נוב", "דצמ"]

# =======================
# RTL + עיצוב
# =======================
st.markdown("""
<style>
html, body, .stApp, .main, .block-container {
  direction: rtl !important;
  text-align: right !important;
  font-family: "Assistant","Heebo",sans-serif !important;
}

/* כותרות */
h1, h2, h3 { color:#2f6f3e; }

/* selectbox */
[data-baseweb="select"] * {
  direction: rtl !important;
  text-align: right !important;
}

/* inputs */
input, textarea {
  direction: rtl !important;
  text-align: right !important;
}
</style>
""", unsafe_allow_html=True)

# =======================
# פונקציות עזר
# =======================
def is_marked(v) -> bool:
    """כל ערך לא-ריק נחשב 'כן' (כולל *, V, ק, מ וכו')"""
    if v is None:
        return False
    s = str(v).strip()
    return s != "" and s.lower() not in ("nan", "none")

def show_value(v) -> str:
    if v is None:
        return "לא ידוע"
    s = str(v).strip()
    return s if s and s.lower() not in ("nan", "none") else "לא ידוע"

@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_URL)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def find_col(df: pd.DataFrame, contains_text: str):
    """מוצא עמודה שהשם שלה מכיל טקסט (למשל 'שם הצמח')"""
    for c in df.columns:
        if contains_text in str(c).strip():
            return c
    return None

def get_months(row: pd.Series, prefix: str):
    """קורא חודשים מעמודות בשם 'זרעים 1..12' או 'ייחורים 1..12' """
    months = []
    for i in range(1, 13):
        col = f"{prefix} {i}"
        if col in row.index and is_marked(row.get(col)):
            months.append(i)
    return months

def card(title: str, content_html: str, months=None):
    """
    כרטיס HTML יפה. content_html יכול לכלול <br>.
    אנחנו בורחים (escape) הכל כדי שלא ישבור HTML ואז מחזירים <br> בלבד.
    """
    safe_title = html.escape(str(title))

    safe_content = html.escape(str(content_html)).replace("&lt;br&gt;", "<br>")

    try:
        months = [int(x) for x in (months or [])]
    except Exception:
        months = []

    months_html = ""
    if len(months) > 0:
        dots = " ".join([("●" if (i+1) in months else "○") for i in range(12)])
        months_html = f"""
        <div style="margin-top:12px">
            <div style="font-size:14px; opacity:0.85">{'  '.join(MONTHS_HE)}</div>
            <div style="font-size:22px; color:#2f6f3e; letter-s
