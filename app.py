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

#החלפת פונקצית חודשים כדי שהסימון יהיה קריא יותר 

def show_months(months):
    symbols = ["✔" if i in months else "✖" for i in range(1, 13)]

    header = "".join([
        f"<th style='border:1px solid #ccc; padding:6px 8px; text-align:center; background:#f7f7f7;'>{m}</th>"
        for m in MONTHS_HE
    ])

    row = "".join([
        f"<td style='border:1px solid #ccc; padding:6px 8px; text-align:center; font-size:18px;"
        f" color:{'#2f9e44' if s=='✔' else '#e03131'};'>{s}</td>"
        for s in symbols
    ])

    st.markdown(f"""
    <div dir="rtl" style="width:100%; overflow-x:auto;">
      <table style="border-collapse:collapse; margin-top:6px;">
        <tr>{header}</tr>
        <tr>{row}</tr>
      </table>
    </div>
    """, unsafe_allow_html=True)



#def show_months(months):
#    dots=["●" if i in months else "·" for i in range(1,13)]
#    st.code("  ".join(MONTHS_HE)+"\n"+"   ".join(dots))

# ************************************************************************************
# קטע שהוספתי כדי שתהיה הבחנה בין סוגי הייחורים הרלבנטים בחודשי השנה
# ************************************************************************************

def parse_cutting_cell(v):
    """מחזיר סט של סימונים מתוך תא חודש בייחורים: {'*','מ','ק','ע'}"""
    s = str(v).strip()
    if s == "":
        return set()
    # מנקה רווחים/גרשיים/מפרידים נפוצים
    s = s.replace(" ", "").replace('"', "").replace("'", "").replace("\\", "").replace("|", "")
    return set(list(s))  # תומך גם במצב שיש כמה סימנים באותו תא

def get_cuttings_by_type(row, prefix="ייחורים"):
    """
    קורא את העמודות 'ייחורים 1'...'ייחורים 12' ומחזיר dict:
    { 'מעוצה': [חודשים], 'קודקודי': [...], 'עלה': [...] }
    כוכבית * = כל סוגי הייחורים הרלוונטיים לצמח (לפי העמודות מעוצה/קודקודי/עלה אם קיימות)
    """
    # אילו סוגים רלוונטיים לצמח לפי עמודות הסוג (כמו שכבר יש אצלך)
    relevant_types = []
    for t in ["מעוצה", "קודקודי", "עלה"]:
        if has_value(row.get(t)):
            relevant_types.append(t)

    # אם אין בכלל סימון סוגים בצמח, נניח ש-* אומר "כל הסוגים"
    if not relevant_types:
        relevant_types = ["מעוצה", "קודקודי", "עלה"]

    months_by_type = {t: [] for t in relevant_types}

    for i in range(1, 13):
        col = f"{prefix} {i}"
        if col not in row:
            continue

        marks = parse_cutting_cell(row[col])
        if not marks:
            continue

        # פירוש סימונים
        if "*" in marks:
            for t in relevant_types:
                months_by_type[t].append(i)
        if "מ" in marks and "מעוצה" in months_by_type:
            months_by_type["מעוצה"].append(i)
        if "ק" in marks and "קודקודי" in months_by_type:
            months_by_type["קודקודי"].append(i)
        if "ע" in marks and "עלה" in months_by_type:
            months_by_type["עלה"].append(i)

    # ניקוי כפילויות ושמירה על סדר
    for t in months_by_type:
        months_by_type[t] = sorted(set(months_by_type[t]))

    return months_by_type


def is_star_mark(v):
    s = str(v).strip()
    return s == "*"

def extract_note(v):
    s = str(v).strip()
    # אם ריק או רק כוכבית – אין הערה
    if s == "" or s == "*":
        return ""
    return s

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

# הצגת תמונה אם קיימת
if has_value(row.get("תמונה")):
    st.image(row.get("תמונה"), use_container_width=True)


# ===== שיוך =====
st.subheader("שיוך")

categories = [
    "עץ","שיח","בן שיח","מטפס","עשבוני","מושך חיות",
    "עץ מאכל","ירקות קיץ","ירקות חורף","בצלים ופקעות","תיבול ומרפא"
]

tags = [c for c in categories if c in row and has_value(row.get(c))]

st.write(" · ".join(tags) if tags else "—")


# ===== תכונות מיוחדות =====
if has_value(row.get("תכונות מיוחדות/הערות")):
    st.caption("תכונות מיוחדות/הערות: " + str(row["תכונות מיוחדות/הערות"]).strip())


# st.subheader("ריבוי וגטטיבי")
# st.write("חלוקה:", "כן" if has_value(row.get("ריבוי בחלוקה")) else "לא")
# st.write("שלוחות:", "כן" if has_value(row.get("ריבוי בשלוחות")) else "לא")

st.subheader("ריבוי וגטטיבי")

if has_value(row.get("ריבוי בחלוקה")):
    st.write("חלוקה: כן")
else:
    st.info("לא ניתן לריבוי ע״י חלוקה")

if has_value(row.get("ריבוי בשלוחות")):
    st.write("שלוחות: כן")
else:
    st.info("לא ניתן לריבוי משלוחות")


# st.subheader("ריבוי מזרעים")
# show_months(get_months(row,"זרעים"))
# st.write("טרי:", "כן" if has_value(row.get("טרי")) else "לא")
# st.write("יבש:", "כן" if has_value(row.get("יבש")) else "לא")
# if has_value(row.get("טיפול לפני זריעה")):
#     st.write("טיפול לפני זריעה:",row["טיפול לפני זריעה"])

st.subheader("ריבוי מזרעים")

fresh = has_value(row.get("טרי"))
dry = has_value(row.get("יבש"))

# אם אין בכלל ריבוי מזרעים
if not fresh and not dry:
    st.info("לא ניתן לריבוי מזרעים")

else:
    # חודשים לזריעה
    show_months(get_months(row, "זרעים"))

    # ניסוח יפה לפי סוג הזרעים
    if fresh:
        st.write("סוג זרעים: טריים")
    elif dry:
        st.write("סוג זרעים: יבשים")

    # טיפול בזרעים אם קיים
    if has_value(row.get("טיפול")):
        st.write("טיפול בזרעים:", row.get("טיפול"))



# קוד ישן של ייחורים
#השארתי כאן רק למקרה שנרצה לחזור אליו


#st.subheader("ריבוי מייחורים")
#show_months(get_months(row,"ייחורים"))
#types=[t for t in ["מעוצה","קודקודי","עשבוני","עלה"] if has_value(row.get(t))]
#st.write(" · ".join(types) if types else "—")


# st.subheader("ריבוי מייחורים")

# # מציג אילו סוגים רלוונטיים לצמח
# types = [t for t in ["מעוצה", "קודקודי", "עלה"] if has_value(row.get(t))]
# st.write("סוגי ייחורים רלוונטיים:", " · ".join(types) if types else "—")

# # מציג חודשים לפי סוג, לפי הסימונים בעמודות החודשיות (*/מ/ק/ע)
# months_by_type = get_cuttings_by_type(row, "ייחורים")

# #st.markdown("**חודשים לפי סוג ייחור:**")
# #for t, months in months_by_type.items():
#  #   st.write(f"{t}:")
#  #   show_months(months)

# # אם אין בכלל חודשים לשום סוג – נכתוב הודעה
# if not any(months for months in months_by_type.values()):
#     st.info("לא ניתן לריבוי מייחורים")
# else:
#     st.markdown("**חודשים לפי סוג ייחור:**")
#     for t, months in months_by_type.items():
#         if months:  # מציגים רק סוגים שבאמת יש להם חודשים
#             st.write(f"{t}:")
#             show_months(months)

st.subheader("ריבוי מייחורים")

# סוגי ייחורים שסומנו כרלוונטיים לצמח (אם קיימים בגיליון)
types = [t for t in ["מעוצה", "קודקודי", "עלה"] if has_value(row.get(t))]

# חודשים לפי סוג, לפי הסימונים בעמודות החודשיות (*/מ/ק/ע)
months_by_type = get_cuttings_by_type(row, "ייחורים")

# אם אין בכלל חודשים לשום סוג – נכתוב הודעה
if not any(months for months in months_by_type.values()):
    st.info("לא ניתן לריבוי מייחורים")
else:
    # מציגים שורת סוגים רק אם באמת יש רשימה (בלי קו)
    if types:
        st.write("סוגי ייחורים רלוונטיים:", " · ".join(types))

    st.markdown("**חודשים לפי סוג ייחור:**")
    for t, months in months_by_type.items():
        if months:  # מציגים רק סוגים שבאמת יש להם חודשים
            st.write(f"{t}:")
            show_months(months)


#סוף הבלוק החדש במקום הקוד הישן של ייחורים


def show_value(v):
    if v is None: return "לא ידוע"
    s=str(v).strip()
    return s if s else "לא ידוע"

st.write("השקיה:", show_value(row.get("השקיה")))
st.write("אור:", show_value(row.get("אור")))
st.write("ריח:", show_value(row.get("ריח")))


st.caption(CREDIT)
