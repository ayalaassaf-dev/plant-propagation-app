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
            <div style="font-size:22px; color:#2f6f3e; letter-spacing:2px">{dots}</div>
        </div>
        """

    st.markdown(f"""
    <div style="
        background:#f6fbf7;
        padding:18px 18px 14px 18px;
        border-radius:16px;
        margin: 0 0 14px 0;
        border:1px solid #d8eadc;
        box-shadow: 0 1px 0 rgba(0,0,0,0.03);
    ">
        <div style="font-size:20px; font-weight:700; margin-bottom:8px; color:#2f6f3e">{safe_title}</div>
        <div style="font-size:18px; line-height:1.7">{safe_content}</div>
        {months_html}
    </div>
    """, unsafe_allow_html=True)

# =======================
# כותרת אפליקציה
# =======================
st.markdown(f"""
<h1 style="text-align:center; margin-bottom:0">{TITLE}</h1>
<p style="text-align:center; font-size:20px; margin-top:6px; opacity:0.9">{SUBTITLE}</p>
""", unsafe_allow_html=True)

# =======================
# טעינת נתונים + זיהוי עמודות
# =======================
df = load_data()

name_col = find_col(df, "שם הצמח")
if not name_col:
    st.error("לא נמצאה עמודת 'שם הצמח'. בדקי שבשורה 1 קיימת כותרת שכוללת את הטקסט 'שם הצמח'.")
    st.write("עמודות שנמצאו כרגע:")
    st.write(list(df.columns))
    st.stop()

df = df[df[name_col].notna()].copy()
df[name_col] = df[name_col].astype(str).str.strip()

# =======================
# בחירת צמח
# =======================
plant = st.selectbox("בחרי צמח", [""] + sorted(df[name_col].unique().tolist()))
st.caption(CREDIT)

if not plant:
    st.stop()

row = df[df[name_col] == plant].iloc[0]
st.markdown(f"<h2 style='margin-top:6px'>{html.escape(plant)}</h2>", unsafe_allow_html=True)

# =======================
# שיוך
# =======================
categories = ["עץ","שיח","בן שיח","מטפס","עשבוני","מושך חיות","עץ מאכל","ירקות קיץ","ירקות חורף","בצלים ופקעות","תיבול ומרפא"]
tags = [c for c in categories if c in row.index and is_marked(row.get(c))]
card("שיוך", " · ".join(tags) if tags else "אין מידע")

# =======================
# ריבוי וגטטיבי
# =======================
div_yes = "כן" if is_marked(row.get("ריבוי בחלוקה")) else "לא"
sto_yes = "כן" if is_marked(row.get("ריבוי בשלוחות")) else "לא"
veg_html = f"חלוקה: {div_yes}<br>שלוחות: {sto_yes}"
card("ריבוי וגטטיבי", veg_html)

# =======================
# ריבוי מזרעים
# =======================
fresh_yes = "כן" if is_marked(row.get("טרי")) else "לא"
dry_yes = "כן" if is_marked(row.get("יבש")) else "לא"
seed_html = f"טרי: {fresh_yes}<br>יבש: {dry_yes}"

treat = row.get("טיפול")
if is_marked(treat):
    seed_html += f"<br>טיפול: {str(treat).strip()}"

seed_months = get_months(row, "זרעים")
card("ריבוי מזרעים", seed_html, seed_months)

# =======================
# ריבוי מייחורים
# =======================
types = [t for t in ["מעוצה","קודקודי","עשבוני","עלה"] if is_marked(row.get(t))]
cut_html = " · ".join(types) if types else "אין מידע"
cut_months = get_months(row, "ייחורים")
card("ריבוי מייחורים", cut_html, cut_months)

# =======================
# תנאי גידול
# =======================
grow_html = f"""
השקיה: {show_value(row.get("השקיה"))}<br>
אור: {show_value(row.get("אור"))}<br>
ריח: {show_value(row.get("ריח"))}
"""
card("תנאי גידול", grow_html)

st.caption(CREDIT)
