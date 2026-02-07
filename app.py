import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="טבלת ריבוי צמחים", layout="centered")

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

def get_months(row, prefix):
    months=[]
    for i in range(1,13):
        col=f"{prefix} {i}"
        if col in row and is_marked(row[col]):
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
tags=[c for c in categories if c in row and is_marked(row[c])]
st.write(" · ".join(tags) if tags else "—")

st.subheader("ריבוי וגטטיבי")
st.write("חלוקה:", "כן" if is_marked(row.get("ריבוי בחלוקה")) else "—")
st.write("שלוחות:", "כן" if is_marked(row.get("ריבוי בשלוחות")) else "—")

st.subheader("ריבוי מזרעים")
show_months(get_months(row,"זרעים"))
st.write("טרי:", "כן" if is_marked(row.get("טרי")) else "—")
st.write("יבש:", "כן" if is_marked(row.get("יבש")) else "—")
if is_marked(row.get("טיפול")):
    st.write("טיפול:",row["טיפול"])

st.subheader("ריבוי מייחורים")
show_months(get_months(row,"ייחורים"))
types=[t for t in ["מעוצה","קודקודי","עשבוני","עלה"] if is_marked(row.get(t))]
st.write(" · ".join(types) if types else "—")

st.subheader("תנאי גידול")
st.write("השקיה:",row.get("השקיה","—"))
st.write("אור:",row.get("אור","—"))
st.write("ריח:",row.get("ריח","—"))

st.caption(CREDIT)
