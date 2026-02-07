import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="טבלת ריבוי צמחים", layout="centered")

st.markdown("""
<style>
/* כיוון כתיבה + יישור */
html, body, .stApp, .main, .block-container {
  direction: rtl !important;
  text-align: right !important;
}

/* טקסטים וכותרות */
h1, h2, h3, h4, h5, h6, p, li, div, span, label {
  direction: rtl !important;
  text-align: right !important;
}

/* שדה בחירה / חיפוש */
[data-baseweb="select"] * {
  direction: rtl !important;
  text-align: right !important;
}

/* תיבת טקסט/חיפוש אם תשתמשי בה */
input, textarea {
  direction: rtl !important;
  text-align: right !important;
}
</style>
""", unsafe_allow_html=True)


# ===== עיצוב כללי + עברית =====
st.markdown("""
<style>
html, body, [class*="css"]  {
    direction: rtl;
    text-align: right;
    font-family: "Assistant", "Heebo", sans-serif;
}

.stSelectbox label {
    text-align:right;
}

.block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    color:#2f6f3e;
}
</style>
""", unsafe_allow_html=True)


CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGk2pn1I3JZjuhLZbIEWrMfMN02EV_kxuZl2Q3sWxMiRlvLekN-xucADwoy6x9fg/pub?gid=570603705&single=true&output=csv"

TITLE = "טבלת ריבוי צמחים"
SUBTITLE = "מידע לריבוי צמחי גן ונוי"
CREDIT = "המידע נאסף ע״י בועז שחם · האפליקציה הוכנה ע״י אילה אסף"

MONTHS_HE = ["ינו","פבר","מרץ","אפר","מאי","יונ","יול","אוג","ספט","אוק","נוב","דצמ"]

def is_marked(v):
    if v is None: return False
    s = str(v).strip()
    return s != "" and s.lower() not in ("nan","none")

def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = [str(c).strip() for c in df.columns]
    return df



def show_months(months):
    dots=["●" if i in months else "·" for i in range(1,13)]
    st.code("  ".join(MONTHS_HE)+"\n"+"   ".join(dots))

import html

def card(title, content, months=None):
    # הגנה – שלא יהיו תווים ששוברים HTML
    safe_title = html.escape(str(title))
    safe_content = html.escape(str(content)).replace("&lt;br&gt;", "<br>")

    # הגנה – months תמיד רשימה
    try:
        months = [int(x) for x in (months or [])]
    except Exception:
        months = []

    months_html = ""
    if len(months) > 0:
        month_names = ["ינו","פבר","מרץ","אפר","מאי","יונ","יול","אוג","ספט","אוק","נוב","דצמ"]
        dots = "".join([
            f"<span style='color:#2f6f3e;font-size:22px'>{'●' if (i+1) in months else '○'}</span> "
            for i in range(12)
        ])
        months_html = f"""
        <div style='margin-top:10px'>
            <div style='font-size:14px'>{' '.join(month_names)}</div>
            <div>{dots}</div>
        </div>
        """

    st.markdown(f"""
    <div style="
        background-color:#f6fbf7;
        padding:20px;
        border-radius:15px;
        margin-bottom:18px;
        border:1px solid #d8eadc;
    ">
        <h3>{safe_title}</h3>
        <div style="font-size:18px">{safe_content}</div>
        {months_html}
    </div>
    """, unsafe_allow_html=True)



st.markdown(f"""
<h1 style='text-align:center'>{TITLE}</h1>
<p style='text-align:center;font-size:20px'>{SUBTITLE}</p>
""", unsafe_allow_html=True)


df=load_data()
df=df[df["שם הצמח"].notna()]

plant=st.selectbox("בחרי צמח",[""]+sorted(df["שם הצמח"].unique()))

st.caption(CREDIT)

if not plant:
    st.stop()

row=df[df["שם הצמח"]==plant].iloc[0]
st.header(plant)

categories = ["עץ","שיח","בן שיח","מטפס","עשבוני","מושך חיות","עץ מאכל","ירקות קיץ","ירקות חורף","בצלים ופקעות","תיבול ומרפא"]
tags = [c for c in categories if c in row and is_marked(row[c])]
card("שיוך", " · ".join(tags) if tags else "אין מידע")


veg = f"""
חלוקה: {"כן" if is_marked(row.get("ריבוי בחלוקה")) else "לא"}<br>
שלוחות: {"כן" if is_marked(row.get("ריבוי בשלוחות")) else "לא"}
"""
card("ריבוי וגטטיבי", veg)


seed_text = f"""
טרי: {"כן" if is_marked(row.get("טרי")) else "לא"}<br>
יבש: {"כן" if is_marked(row.get("יבש")) else "לא"}
"""
if is_marked(row.get("טיפול")):
    seed_text += f"<br>טיפול: {row['טיפול']}"

seed_months = get_months(row,"זרעים")
card("ריבוי מזרעים", seed_text, seed_months)


types=[t for t in ["מעוצה","קודקודי","עשבוני","עלה"] if is_marked(row.get(t))]
cut_months = get_months(row,"ייחורים")
card("ריבוי מייחורים", " · ".join(types) if types else "אין מידע", cut_months)



def show_value(v):
    if v is None: return "לא ידוע"
    s=str(v).strip()
    return s if s else "לא ידוע"

st.write("השקיה:", show_value(row.get("השקיה")))
st.write("אור:", show_value(row.get("אור")))
st.write("ריח:", show_value(row.get("ריח")))


st.caption(CREDIT)
