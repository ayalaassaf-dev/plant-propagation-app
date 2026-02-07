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

def has_value(v):
    return str(v).strip() != ""


def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.fillna("")   # ← זה גורם לכך שכל NaN יהפוך לתא ריק אמיתי NaN.!
    return df


def get_months(row, prefix):
    months=[]
    for i in range(1,13):
        col=f"{prefix} {i}"
        if col in row and has_value(row[col]):
            months.append(i)
    return months


def show_months(months):
    dots=["●" if i in months else "·" for i in range(1,13)]
    st.code("  ".join(MONTHS_HE)+"\n"+"   ".join(dots))

st.title(TITLE)
st.caption(SUBTITLE)

df=load_data()
df=df[df["שם הצמח"].notna()]

plant=st.selectbox("בחרי צמח",[""]+sorted(df["שם הצמח"].unique()))

st.caption(CREDIT)

if not plant:
    st.stop()

row=df[df["שם הצמח"]==plant].iloc[0]
st.header(plant)

st.subheader("שיוך")
categories=["עץ","שיח","בן שיח","מטפס","עשבוני","מושך חיות","עץ מאכל","ירקות קיץ","ירקות חורף","בצלים ופקעות","תיבול ומרפא"]
tags=[c for c in categories if c in row and has_value(row[c])]
st.write(" · ".join(tags) if tags else "—")

st.subheader("ריבוי וגטטיבי")
st.write("חלוקה:", "כן" if has_value(row.get("ריבוי בחלוקה")) else "לא")
st.write("שלוחות:", "כן" if has_value(row.get("ריבוי בשלוחות")) else "לא")

st.subheader("ריבוי מזרעים")
show_months(get_months(row,"זרעים"))
st.write("טרי:", "כן" if has_value(row.get("טרי")) else "לא")
st.write("יבש:", "כן" if has_value(row.get("יבש")) else "לא")
if has_value(row.get("טיפול")):
    st.write("טיפול:",row["טיפול"])

if has_value(row.get("טיפול")):
    st.write("טיפול:", row["טיפול"])

st.subheader("ריבוי מייחורים")
show_months(get_months(row,"ייחורים"))
types=[t for t in ["מעוצה","קודקודי","עשבוני","עלה"] if has_value(row.get(t))]
st.write(" · ".join(types) if types else "—")

def show_value(v):
    if v is None: return "לא ידוע"
    s=str(v).strip()
    return s if s else "לא ידוע"

st.write("השקיה:", show_value(row.get("השקיה")))
st.write("אור:", show_value(row.get("אור")))
st.write("ריח:", show_value(row.get("ריח")))


st.caption(CREDIT)
