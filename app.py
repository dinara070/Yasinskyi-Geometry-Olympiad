import streamlit as st
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import io
import zipfile

# --- БЕЗПЕЧНІ ІМПОРТИ ---
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

# --- 1. Налаштування сторінки ---
st.set_page_config(
    page_title="Yasinskyi Geometry Olympiad | VSPU",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Візуальний тюнінг (CSS) ---
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; }
    .header-university { color: #800000; font-family: 'Times New Roman', serif; text-align: center; margin-bottom: 0px; }
    .header-faculty { color: #2c3e50; font-family: sans-serif; text-align: center; font-size: 1.1rem; font-weight: bold; }
    .header-dept { color: #555; text-align: center; font-style: italic; margin-bottom: 20px; border-bottom: 2px solid #800000; padding-bottom: 10px; }
    .bio-text { font-size: 1.05rem; line-height: 1.6; text-align: justify; color: #333; }
    .quote-card { background-color: #f8f9fa; border-left: 5px solid #800000; padding: 15px; font-style: italic; margin: 15px 0; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: white; color: #555; text-align: center; padding: 10px; border-top: 1px solid #eaeaea; font-size: 0.9rem; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 3. Банк завдань (DEMO PROBLEM BANK) ---
# Завдання записані латиницею, щоб уникнути проблем зі шрифтами PDF без файлу .ttf
PROBLEM_BANK = {
    "Тригонометрія": {
        "Початковий": [
            "1. Calculate: sin(30) + cos(60).",
            "2. Simplify: sin^2(x) + cos^2(x).",
            "3. Find tan(x) if sin(x) = 3/5 and cos(x) = 4/5."
        ],
        "Середній": [
            "1. Solve for x: 2sin(x) = 1, where 0 < x < 90.",
            "2. Prove identity: (1 - cos x)(1 + cos x) = sin^2 x.",
            "3. Calculate the value of cos(120)."
        ],
        "Високий (Олімпіадний)": [
            "1. Solve: sin(x) + cos(x) = sqrt(2).",
            "2. Prove that sin(3x) = 3sin(x) - 4sin^3(x).",
            "3. Find the maximum value of f(x) = 3sin(x) + 4cos(x)."
        ]
    },
    "Квадратні рівняння": {
        "Початковий": [
            "1. Solve: x^2 - 4 = 0.",
            "2. Calculate the discriminant of: x^2 + 5x + 6 = 0.",
            "3. Find roots: (x-1)(x+2) = 0."
        ],
        "Середній": [
            "1. Solve: 2x^2 - 5x + 2 = 0.",
            "2. Find p if x^2 + px + 10 = 0 has a root x = 2.",
            "3. Form a quadratic equation with roots 3 and -5."
        ],
        "Високий (Олімпіадний)": [
            "1. Solve for x: x^2 + |x| - 6 = 0.",
            "2. Find parameter a for which x^2 - (2a+1)x + a^2 = 0 has equal roots.",
            "3. Solve: (x^2 + x + 1)(x^2 + x + 2) = 12."
        ]
    },
    # Для інших тем додаємо заглушки
    "Вектори": {"Початковий": ["1. Find vector AB if A(1,1), B(2,2)."], "Середній": ["1. Dot product of a(1,2) and b(3,4)."], "Високий (Олімпіадний)": ["1. Find angle between vectors."]},
    "Похідна": {"Початковий": ["1. Find f'(x) for f(x) = x^2."], "Середній": ["1. Find derivative of sin(x)*cos(x)."], "Високий (Олімпіадний)": ["1. Find local maximum of x^3 - 3x."]}
}

# --- 4. Функція генерації PDF ---
def create_pdf(topic, difficulty, problems):
    if not FPDF_AVAILABLE:
        return None
    
    pdf = FPDF()
    pdf.add_page()
    
    # Використовуємо Arial (стандартний шрифт FPDF, підтримує латиницю)
    pdf.set_font("Arial", size=16)
    
    # Заголовок
    pdf.cell(200, 10, txt="Math Task Sheet", ln=1, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="VSPU Geometry Olympiad Generator", ln=1, align='C')
    
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    # Інформація про варіант
    pdf.set_font("Arial", 'B', size=12)
    # Транслітерація теми для безпеки (щоб не було ??? замість кирилиці)
    topic_map = {
        "Тригонометрія": "Trigonometry", 
        "Квадратні рівняння": "Quadratic Equations",
        "Вектори": "Vectors",
        "Похідна": "Derivatives"
    }
    safe_topic = topic_map.get(topic, "Math Topic")
    
    # Вивід теми та складності англійською (для безпеки шрифтів)
    pdf.cell(0, 10, txt=f"Topic: {safe_topic}", ln=1)
    # Difficulty mapping
    diff_map = {"Початковий": "Basic Level", "Середній": "Medium Level", "Високий (Олімпіадний)": "Advanced Level"}
    pdf.cell(0, 10, txt=f"Difficulty: {diff_map.get(difficulty, 'General')}", ln=1)
    
    pdf.ln(10)
    
    # Вивід задач
    pdf.set_font("Arial", size=12)
    for prob in problems:
        pdf.cell(0, 10, txt=prob, ln=1)
        
    # Футер документа
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, txt="Generated by Yasinskyi Olympiad App", align='C')
    
    # Повертаємо бінарні дані (важливо для Streamlit!)
    # latin-1 кодування потрібне для FPDF версії < 2.5
    return pdf.output(dest='S').encode('latin-1')

# --- 5. Словник перекладів ---
TRANSLATIONS = {
    "ua": {
        "uni_name": "Вінницький державний педагогічний університет<br>імені Михайла Коцюбинського",
        "faculty_name": "Факультет математики, фізики і комп'ютерних наук",
        "dept_name": "Кафедра алгебри і методики навчання математики",
        "nav_title": "Меню навігації",
        "menu_items": {
            "home": "🏠 Про олімпіаду",
            "current": "📝 Поточна олімпіада (2025)",
            "archive": "📚 Архів задач",
            "history": "📊 Історія та результати",
            "contacts": "📞 Контакти",
            "method": "🎓 Методичний кабінет"
        },
        "tab_general": "ℹ️ Загальна інформація", "tab_bio": "👤 Біографія В. Ясінського", "tab_faq": "❓ FAQ (Питання)",
        "banner_title": "Геометрична олімпіада імені В'ячеслава Ясінського",
        "about_desc": "**Геометрична олімпіада імені В'ячеслава Ясінського** — це щорічне змагання...",
        "rules_title": "Правила та формат", "rules_list": ["👥 **Учасники:** Учні 8-11 класів.", "💻 **Формат:** Онлайн.", "🧩 **Завдання:** 5 задач."],
        "math_beauty_title": "Краса геометрії", "math_beauty_desc": "Геометрія — це мистецтво правильних міркувань...",
        "example_problem_label": "Приклад олімпіадної задачі (Демо)", "example_problem_text": "Нехай $ABC$ — гострокутний трикутник...",
        "bio_title": "В'ячеслав Андрійович Ясінський (1957–2015)",
        "bio_full_text": "**В'ячеслав Андрійович Ясінський** — легендарна постать... Автор понад 15 книг...",
        "bio_quote": "Математика вчить не лише рахувати, вона вчить думати...",
        "faq_q1": "Участь платна?", "faq_a1": "Ні, безкоштовно.", "faq_q2": "Формат?", "faq_a2": "PDF.", "faq_q3": "Хто?", "faq_a3": "8-11 клас.",
        "current_title": "Олімпіада 2025/2026", "next_date_label": "Наступна дата:", "next_date_val": "Листопад 2026",
        "reg_title": "Реєстрація", "reg_form_header": "Форма", "f_name": "Ім'я", "f_surname": "Прізвище", "f_email": "Email", "f_country": "Країна", "f_city": "Місто", "f_school": "Школа", "f_grade": "Клас", "f_file": "Файл (PDF)", "f_submit": "Надіслати", "success_msg": "Надіслано!",
        "archive_title": "Бібліотека", "btn_zip": "Завантажити ZIP", "zip_generating": "Сканування...", "link_view": "Переглянути",
        "hist_title": "Статистика", "metric_participants": "Учасників", "metric_countries": "Країн", "metric_total": "Всього", "winners_table_title": "Призери", "chart_title": "Динаміка", "abs_winner": "Абсолютний переможець",
        "contact_page_title": "Контакти", "contact_title": "Організатори", "contact_subtitle_phones": "Телефони:", "contact_address_label": "Адреса:", "contact_address_val": "м. Вінниця...", "contact_email_label": "Email:", "contact_email_val": "yasinskyi@gmail.com",
        "c_person_1": "**Коношевський О. Л.**", "c_role_1": "доцент", "c_phone_1": "(067) 29-010-78", "c_person_2": "**Панасенко О. Б.**", "c_role_2": "доцент", "c_phone_2": "(067) 215-15-71", "feedback_label": "Повідомлення", "send_btn": "Надіслати", "footer_rights": "© 2025 Yasinskyi Geometry Olympiad.",
        
        # METHODOLOGICAL
        "method_title": "Методичний кабінет", "mt_tab1": "🛠️ Генератор завдань", "mt_tab2": "✒️ LaTeX Редактор", "mt_tab3": "📂 Банк силабусів", "mt_tab4": "📊 Звітність",
        "gen_topic": "Оберіть тему:", "gen_diff": "Складність:", "gen_btn": "Згенерувати варіант (PDF)",
        "topics": ["Тригонометрія", "Квадратні рівняння", "Вектори", "Похідна"],
        "diffs": ["Початковий", "Середній", "Високий (Олімпіадний)"],
        "latex_desc": "Формула в LaTeX -> Картинка:", "latex_placeholder": r"\int x^2 dx", "latex_btn": "Скачати PNG",
        "syl_desc": "Силабуси:", "syl_btn": "Скачати", "report_gen_title": "Генератор звіту", "report_desc": "Авто-текст для звіту.", "btn_gen_report": "Текст звіту", "report_label": "Результат:", "report_template": "ЗВІТ..."
    },
    "en": {
        "uni_name": "Vinnytsia State Pedagogical University", "faculty_name": "Faculty of Math, Physics, CS", "dept_name": "Dept of Algebra", "nav_title": "Menu",
        "menu_items": {"home": "🏠 Home", "current": "📝 Current", "archive": "📚 Archive", "history": "📊 History", "contacts": "📞 Contacts", "method": "🎓 Methodological"},
        "tab_general": "Info", "tab_bio": "Bio", "tab_faq": "FAQ", "banner_title": "Yasinskyi Olympiad", "about_desc": "Competition...", "rules_title": "Rules", "rules_list": ["Grades 8-11"], "math_beauty_title": "Beauty", "math_beauty_desc": "Art...", "example_problem_label": "Demo Problem", "example_problem_text": "Triangle...", "bio_title": "V. Yasinskyi", "bio_full_text": "Legend...", "bio_quote": "Math teaches thinking...", "faq_q1": "Free?", "faq_a1": "Yes", "faq_q2": "Format?", "faq_a2": "PDF", "faq_q3": "Who?", "faq_a3": "8-11",
        "current_title": "Olympiad 2025", "next_date_label": "Next:", "next_date_val": "Nov 2026", "reg_title": "Registration", "reg_form_header": "Form", "f_name": "Name", "f_surname": "Surname", "f_email": "Email", "f_country": "Country", "f_city": "City", "f_school": "School", "f_grade": "Grade", "f_file": "File", "f_submit": "Submit", "success_msg": "Sent",
        "archive_title": "Archive", "btn_zip": "Download ZIP", "zip_generating": "Generating...", "link_view": "View", "hist_title": "Stats", "metric_participants": "Participants", "metric_countries": "Countries", "metric_total": "Total", "winners_table_title": "Winners", "chart_title": "Chart", "abs_winner": "Winner",
        "contact_page_title": "Contacts", "contact_title": "Organizers", "contact_subtitle_phones": "Phones", "contact_address_label": "Address", "contact_address_val": "Vinnytsia", "contact_email_label": "Email", "contact_email_val": "email@example.com", "c_person_1": "Konoshevskyi", "c_role_1": "Docent", "c_phone_1": "...", "c_person_2": "Panasenko", "c_role_2": "Docent", "c_phone_2": "...", "feedback_label": "Msg", "send_btn": "Send", "footer_rights": "reserved",
        "method_title": "Methodological", "mt_tab1": "Generator", "mt_tab2": "LaTeX", "mt_tab3": "Syllabus", "mt_tab4": "Reports",
        "gen_topic": "Topic:", "gen_diff": "Difficulty:", "gen_btn": "Generate PDF", "topics": ["Тригонометрія", "Квадратні рівняння", "Вектори", "Похідна"], "diffs": ["Початковий", "Середній", "Високий (Олімпіадний)"], "latex_desc": "LaTeX -> Image", "latex_placeholder": "...", "latex_btn": "Download PNG", "syl_desc": "Syllabuses", "syl_btn": "Download", "report_gen_title": "Report", "report_desc": "Auto text", "btn_gen_report": "Generate", "report_label": "Text", "report_template": "Report..."
    }
}

# --- 6. Змінні та Файли ---
PHOTO_YASINSKYI = "yasinskyi.png"
LOGO_FILE = "logo.png"
TARGET_URL = "https://yasinskyi-geometry-olympiad.com/"

@st.cache_data(ttl=3600)
def get_live_pdf_links():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(TARGET_URL, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(TARGET_URL, href)
                name = unquote(href.split('/')[-1])
                links.append({"name": name, "url": full_url})
        return links
    except: return []

def latex_to_image(formula, fontsize=16, dpi=300):
    if not MATPLOTLIB_AVAILABLE: return None
    buf = io.BytesIO()
    fig = plt.figure(figsize=(6, 1.5))
    fig.text(0.5, 0.5, f"${formula}$", size=fontsize, ha='center', va='center')
    plt.axis('off')
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=dpi, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf

# --- 7. Сайдбар ---
with st.sidebar:
    lang_sel = st.selectbox("Language / Мова", ["UA", "ENG"])
    lang = "ua" if lang_sel == "UA" else "en"
    t = TRANSLATIONS[lang]
    st.markdown("---")
    st.title(t["nav_title"])
    menu_options = list(t["menu_items"].values())
    selected_item = st.radio("Go to:", menu_options, label_visibility="collapsed")
    current_page = [k for k, v in t["menu_items"].items() if v == selected_item][0]
    st.caption(t["uni_name"].replace("<br>", " "))

# --- 8. Шапка ---
col_l, col_c, col_r = st.columns([1, 6, 1])
with col_l:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=100)
    else: st.write("🏛️")
with col_c:
    st.markdown(f'<h2 class="header-university">{t["uni_name"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-faculty">{t["faculty_name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-dept">{t["dept_name"]}</div>', unsafe_allow_html=True)

# --- 9. Контент ---

if current_page == "home":
    st.title(t["banner_title"])
    tab1, tab2, tab3 = st.tabs([t["tab_general"], t["tab_bio"], t["tab_faq"]])
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            if os.path.exists(PHOTO_YASINSKYI): st.image(PHOTO_YASINSKYI, use_container_width=True)
            else: st.image("https://via.placeholder.com/300")
        with c2:
            st.markdown(t["about_desc"])
            st.markdown(f"### {t['rules_title']}")
            st.markdown('<div class="rules-card">', unsafe_allow_html=True)
            for r in t["rules_list"]: st.markdown(r)
            st.markdown('</div>', unsafe_allow_html=True)
        st.subheader("📐 " + t["math_beauty_title"])
        st.info(t["math_beauty_desc"])
        st.latex(r"\frac{a}{\sin A} = 2R")
    with tab2:
        st.markdown(f"### {t['bio_title']}")
        c1, c2 = st.columns([1, 2])
        with c1: 
            if os.path.exists(PHOTO_YASINSKYI): st.image(PHOTO_YASINSKYI, use_container_width=True)
        with c2:
            st.markdown(f'<div class="quote-card">{t["bio_quote"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bio-text">{t["bio_full_text"]}</div>', unsafe_allow_html=True)
    with tab3:
        for q, a in [(t["faq_q1"], t["faq_a1"]), (t["faq_q2"], t["faq_a2"]), (t["faq_q3"], t["faq_a3"])]:
            with st.expander(q): st.write(a)

elif current_page == "current":
    st.title(t["current_title"])
    c1, c2 = st.columns(2)
    c1.metric(t["next_date_label"], t["next_date_val"])
    c2.info("Status: **Planned**")
    st.subheader(t["reg_title"])
    with st.form("reg"):
        c1, c2 = st.columns(2)
        with c1: st.text_input(t["f_name"]); st.text_input(t["f_email"]); st.text_input(t["f_city"]); st.selectbox(t["f_grade"], ["8", "9", "10", "11"])
        with c2: st.text_input(t["f_surname"]); st.text_input(t["f_country"]); st.text_input(t["f_school"]); st.file_uploader(t["f_file"], type=["pdf"])
        if st.form_submit_button(t["f_submit"], type="primary"): st.success(t["success_msg"])

elif current_page == "archive":
    st.title(t["archive_title"])
    if st.button(t["btn_zip"]):
        with st.spinner(t["zip_generating"]):
            links = get_live_pdf_links()
            if links:
                b = io.BytesIO()
                with zipfile.ZipFile(b, "w") as z:
                    for i in links:
                        try:
                            r = requests.get(i["url"], timeout=5)
                            if r.status_code==200: z.writestr(i["name"], r.content)
                        except: pass
                b.seek(0)
                st.download_button("💾 ZIP", b, "archive.zip", "application/zip")
            else: st.error("Error.")
    for y in range(2025, 2016, -1):
        with st.expander(f"{y}"): st.caption("Empty.")

elif current_page == "history":
    st.title(t["hist_title"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t["metric_participants"], "139"); c2.metric(t["metric_countries"], "7"); c3.metric(t["abs_winner"], "I. Ivanov")
    st.subheader(t["winners_table_title"])
    st.dataframe(pd.DataFrame({"Name": ["I. Ivanov", "P. Petrenko"], "Score": [42, 40]}), use_container_width=True)
    st.subheader(t["chart_title"])
    st.bar_chart(pd.DataFrame({'Y': ['23', '24', '25'], 'V': [100, 58, 139]}).set_index('Y'), color="#800000")

elif current_page == "contacts":
    st.title(t["contact_page_title"])
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"### {t['contact_title']}")
        st.markdown(f"**{t['contact_address_label']}**<br>{t['contact_address_val']}", unsafe_allow_html=True)
        st.markdown(f"**{t['contact_email_label']}** {t['contact_email_val']}")
        st.markdown(f"""<div class="contact-card">{t['c_person_1']}<br><small>{t['c_role_1']}</small><br>📞 {t['c_phone_1']}</div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="contact-card">{t['c_person_2']}<br><small>{t['c_role_2']}</small><br>📞 {t['c_phone_2']}</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"### {t['feedback_label']}")
        st.text_area(""); st.button(t["send_btn"])

# === METHODOLOGICAL (ТУТ ОСНОВНІ ЗМІНИ) ===
elif current_page == "method":
    st.title(t["method_title"])
    tab1, tab2, tab3, tab4 = st.tabs([t["mt_tab1"], t["mt_tab2"], t["mt_tab3"], t["mt_tab4"]])
    
    # 1. GENERATOR (ОНОВЛЕНО)
    with tab1:
        st.markdown(f"### {t['mt_tab1']}")
        if not FPDF_AVAILABLE:
            st.error("⚠️ Бібліотека 'fpdf' не знайдена! Додайте 'fpdf' у requirements.txt")
        
        c1, c2 = st.columns(2)
        with c1: sel_topic = st.selectbox(t["gen_topic"], t["topics"])
        with c2: sel_diff = st.selectbox(t["gen_diff"], t["diffs"])
        
        # Кнопка генерації
        # Отримуємо задачі з банку (якщо немає - беремо заглушку)
        tasks = PROBLEM_BANK.get(sel_topic, {}).get(sel_diff, ["No problems found."])
        
        # Генеруємо PDF у пам'яті
        pdf_bytes = create_pdf(sel_topic, sel_diff, tasks)
        
        if pdf_bytes:
            st.download_button(
                label=t["gen_btn"],
                data=pdf_bytes,
                file_name=f"Math_Task_{sel_topic}.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.warning("Генерація PDF недоступна (перевірте fpdf).")

    with tab2:
        st.markdown(f"### {t['mt_tab2']}")
        if not MATPLOTLIB_AVAILABLE: st.warning("Add 'matplotlib' to requirements.txt")
        c1, c2 = st.columns(2)
        with c1: latex_input = st.text_area("LaTeX:", value=t["latex_placeholder"])
        with c2:
            if latex_input:
                st.latex(latex_input)
                img = latex_to_image(latex_input)
                if img: st.download_button(t["latex_btn"], img, "eq.png", "image/png")

    with tab3:
        st.markdown(f"### {t['mt_tab3']}")
        st.caption(t["syl_desc"])
        for i in ["Alg", "Geom"]:
            c1, c2, c3 = st.columns([1, 4, 1])
            c1.write(f"**{i}**"); c2.write(f"Syllabus {i}"); c3.download_button(t["syl_btn"], "demo", f"{i}.pdf")
            st.divider()

    with tab4:
        st.markdown(f"### {t['mt_tab4']}")
        if st.button(t["btn_gen_report"]):
            st.text_area(t["report_label"], t["report_template"], height=200)

st.markdown("---")
st.markdown(f'<div class="footer">{t["footer_rights"]}</div>', unsafe_allow_html=True)
