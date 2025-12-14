import streamlit as st
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import io
import zipfile

# --- БЕЗПЕЧНИЙ ІМПОРТ MATPLOTLIB (Щоб сайт не падав) ---
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

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
    
    /* Стилі для карток */
    .bio-text { font-size: 1.05rem; line-height: 1.6; text-align: justify; color: #333; }
    .quote-card { background-color: #f8f9fa; border-left: 5px solid #800000; padding: 15px; font-style: italic; margin: 15px 0; }
    
    /* Футер */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #555;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #eaeaea;
        font-size: 0.9rem;
    }
    
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 3. Словник перекладів (З ОНОВЛЕНОЮ БІОГРАФІЄЮ) ---
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
        # HOME Tabs
        "tab_general": "ℹ️ Загальна інформація",
        "tab_bio": "👤 Біографія В. Ясінського",
        "tab_faq": "❓ FAQ (Питання)",
        
        "banner_title": "Геометрична олімпіада імені В'ячеслава Ясінського",
        "about_desc": """
        **Геометрична олімпіада імені В'ячеслава Ясінського** — це щорічне змагання, яке об'єднує поціновувачів геометричних задач.
        Вперше вона була проведена кафедрою алгебри і методики навчання математики ВДПУ у **2017 році**.
        """,
        "rules_title": "Правила та формат",
        "rules_list": [
            "👥 **Учасники:** Учні 8-11 класів.",
            "💻 **Формат:** Онлайн (дистанційно).",
            "🧩 **Завдання:** 5 геометричних задач.",
            "⏳ **Тривалість:** 4 години.",
            "⚖️ **Оцінювання:** Кожна задача від 0 до 7 балів."
        ],
        "math_beauty_title": "Краса геометрії",
        "math_beauty_desc": "Геометрія — це мистецтво правильних міркувань на неправильних кресленнях. (Д. Пойя)",
        "example_problem_label": "Приклад олімпіадної задачі (Демо)",
        "example_problem_text": """
        Нехай $ABC$ — гострокутний трикутник, в якому $AB < AC$. Коло $\omega$ проходить через точки $B$ і $C$ та перетинає сторони $AB$ і $AC$ у точках $D$ і $E$ відповідно.
        Доведіть, що якщо $BD = CE$, то:
        """,
        
        # --- РОЗШИРЕНА БІОГРАФІЯ ---
        "bio_title": "В'ячеслав Андрійович Ясінський (1957–2015)",
        "bio_full_text": """
        **В'ячеслав Андрійович Ясінський** — легендарна постать у світі української математичної освіти. Кандидат фізико-математичних наук, доцент кафедри алгебри і методики навчання математики Вінницького державного педагогічного університету імені Михайла Коцюбинського, Заслужений вчитель України, Соросівський вчитель.

        Він народився 12 січня 1957 року на Хмельниччині. Своє життя присвятив не просто викладанню, а створенню унікальної методики підготовки олімпіадників.

        **Основні досягнення та спадщина:**
        * 🏅 **Тренер чемпіонів:** Багато років був одним із керівників та тренерів збірної команди України на Міжнародних математичних олімпіадах. Його учні здобували золоті, срібні та бронзові медалі на найпрестижніших змаганнях світу.
        * 📚 **Автор книг:** Написав понад 15 книг, які стали настільними для вчителів та учнів: *"Задачі математичних олімпіад та методи їх розв'язування"*, *"Секрети підготовки до математичних олімпіад"* (у співавторстві) та унікальні збірники з геометрії.
        * 📐 **Геометр від Бога:** В'ячеслав Андрійович вважав геометрію "поезією математики". Його авторські задачі вирізнялися витонченістю, красою формулювань та несподіваними розв'язками.

        Він пішов із життя 5 листопада 2015 року, але залишив після себе тисячі вдячних учнів і послідовників. Ця олімпіада — данина пам'яті Майстру.
        """,
        "bio_quote": "Математика вчить не лише рахувати, вона вчить думати, аналізувати і бачити красу в простих речах.",

        # FAQ
        "faq_q1": "Чи участь в олімпіаді платна?",
        "faq_a1": "Ні, участь в олімпіаді є повністю безкоштовною.",
        "faq_q2": "Як оформити розв'язок?",
        "faq_a2": "Розв'язки можна писати від руки (розбірливо) та сканувати, або набирати в редакторах (MS Word, LaTeX). Формат файлу — PDF.",
        "faq_q3": "Хто може брати участь?",
        "faq_a3": "Завдання розраховані на учнів 8-11 класів, але молодші школярі також можуть спробувати свої сили.",

        # Current & Archive
        "current_title": "Олімпіада 2025/2026",
        "next_date_label": "Наступна олімпіада відбудеться:",
        "next_date_val": "Листопад 2026 року",
        "reg_title": "Реєстрація та подача робіт",
        "reg_form_header": "Форма учасника (Демонстрація)",
        "f_name": "Ім'я", "f_surname": "Прізвище", "f_email": "Email",
        "f_country": "Країна", "f_city": "Місто", "f_school": "Школа (повна назва)",
        "f_grade": "Клас", "f_file": "Завантажте файл з розв'язками (PDF)",
        "f_submit": "Надіслати роботу",
        "success_msg": "Ваша робота успішно надіслана! Дякуємо за участь.",
        "archive_title": "Бібліотека матеріалів (2017–2025)",
        "btn_zip": "🚀 Завантажити ВСІ матеріали одним архівом (ZIP)",
        "zip_generating": "Сканування сайту та створення архіву...",
        "link_view": "👁️ Переглянути/Скачати на сайті",
        "hist_title": "Статистика та Зала слави",
        "metric_participants": "Учасників у 2025",
        "metric_countries": "Країн-учасниць",
        "metric_total": "Всього учасників",
        "chart_title": "Динаміка зростання олімпіади",
        "winners_table_title": "🏆 Призери останньої олімпіади (Демо-дані)",
        "abs_winner": "Абсолютний переможець 2024",

        # Contacts & Footer
        "contact_page_title": "📞 Контакти",
        "contact_title": "Зв'язок з організаторами",
        "contact_subtitle_phones": "Контактні телефони:",
        "contact_address_label": "Наша адреса:",
        "contact_address_val": "21100, м. Вінниця, вул. Острозького, 32<br>Корпус 3, 5-й поверх.",
        "contact_email_label": "Email:",
        "contact_email_val": "yasinskyi.geometry.olympiad@gmail.com",
        "c_person_1": "**Коношевський Олег Леонідович**",
        "c_role_1": "доцент кафедри алгебри і методики навчання математики",
        "c_phone_1": "(067) 29-010-78",
        "c_person_2": "**Панасенко Олексій Борисович**",
        "c_role_2": "доцент кафедри алгебри і методики навчання математики",
        "c_phone_2": "(067) 215-15-71, (063) 153-04-67",
        "feedback_label": "Напишіть нам повідомлення",
        "send_btn": "Надіслати",
        "footer_rights": "© 2025 Yasinskyi Geometry Olympiad. Всі права захищено.",

        # METHODOLOGICAL
        "method_title": "Методичний кабінет",
        "mt_tab1": "🛠️ Генератор завдань",
        "mt_tab2": "✒️ LaTeX Редактор",
        "mt_tab3": "📂 Банк силабусів",
        "mt_tab4": "📊 Звітність кафедри",
        
        "gen_topic": "Оберіть тему:",
        "gen_diff": "Рівень складності:",
        "gen_btn": "Згенерувати варіант (PDF)",
        "topics": ["Квадратні рівняння", "Вектори", "Тригонометрія", "Похідна"],
        "diffs": ["Початковий", "Середній", "Високий (Олімпіадний)"],
        
        "latex_desc": "Введіть формулу LaTeX, щоб отримати картинку для презентації (PowerPoint) або Word.",
        "latex_placeholder": r"\int_{a}^{b} x^2 dx = \frac{b^3 - a^3}{3}",
        "latex_btn": "💾 Завантажити як картинку (PNG)",
        
        "syl_desc": "Актуальні робочі програми дисциплін кафедри (2025/2026 н.р.)",
        "syl_btn": "Завантажити",
        "report_gen_title": "Генератор звіту про профорієнтацію",
        "report_desc": "Автоматичне формування тексту для річного звіту кафедри.",
        "btn_gen_report": "📄 Згенерувати текст звіту",
        "report_label": "Готовий текст:",
        "report_template": """ЗВІТ ПРО ПРОВЕДЕННЯ ПРОФОРІЄНТАЦІЙНОЇ РОБОТИ (ОЛІМПІАДА)\n\nУ 2025/2026 н.р. кафедрою алгебри..."""
    },
    "en": {
        "uni_name": "Vinnytsia Mykhailo Kotsiubynskyi<br>State Pedagogical University",
        "faculty_name": "Faculty of Mathematics, Physics and Computer Science",
        "dept_name": "Department of Algebra and Methods of Teaching Mathematics",
        "nav_title": "Navigation Menu",
        "menu_items": {
            "home": "🏠 About the Olympiad",
            "current": "📝 Current Olympiad (2025)",
            "archive": "📚 Problem Archive",
            "history": "📊 History & Results",
            "contacts": "📞 Contacts",
            "method": "🎓 Methodological Cabinet"
        },
        "tab_general": "ℹ️ General Info", "tab_bio": "👤 Bio of V. Yasinskyi", "tab_faq": "❓ FAQ",
        "banner_title": "Yasinskyi Geometry Olympiad",
        "about_desc": "**The Yasinskyi Geometry Olympiad** is an annual competition...",
        "rules_title": "Rules and Format", "rules_list": ["Participants: Grades 8-11", "Format: Online"],
        "math_beauty_title": "Geometry Aesthetics", "math_beauty_desc": "Geometry is the art of correct reasoning...",
        "example_problem_label": "Example Problem (Demo)", "example_problem_text": "Let ABC be an acute-angled triangle...",
        
        # English Bio (Shortened)
        "bio_title": "Vyacheslav Andriyovych Yasinskyi (1957–2015)",
        "bio_full_text": """
        **Vyacheslav Andriyovych Yasinskyi** was a legendary figure in Ukrainian mathematics education. He was an Associate Professor at VSPU, an Honored Teacher of Ukraine, and a Soros Teacher.

        Born in 1957, he dedicated his life to training Olympiad students. He served as a trainer for the Ukrainian team at the International Mathematical Olympiad (IMO), guiding many students to medals. He authored over 15 books on Olympiad mathematics.
        """,
        "bio_quote": "Mathematics teaches us not only to count but to think.",

        "faq_q1": "Free?", "faq_a1": "Yes.", "faq_q2": "Format?", "faq_a2": "PDF.", "faq_q3": "Who?", "faq_a3": "Grades 8-11.",
        "current_title": "Olympiad 2025/2026", "next_date_label": "Next Date:", "next_date_val": "Nov 2026",
        "reg_title": "Registration", "reg_form_header": "Form", "f_name": "Name", "f_surname": "Surname", "f_email": "Email", "f_country": "Country", "f_city": "City", "f_school": "School", "f_grade": "Grade", "f_file": "File", "f_submit": "Submit", "success_msg": "Sent!",
        "archive_title": "Materials Library", "btn_zip": "Download ZIP", "zip_generating": "Generating...", "link_view": "View",
        "hist_title": "Statistics", "metric_participants": "Participants", "metric_countries": "Countries", "metric_total": "Total", "chart_title": "Growth", "winners_table_title": "Winners", "abs_winner": "Winner",
        "contact_page_title": "Contacts", "contact_title": "Organizers", "contact_subtitle_phones": "Phones:", "contact_address_label": "Address:", "contact_address_val": "Vinnytsia...", "contact_email_label": "Email:", "contact_email_val": "email@example.com", "c_person_1": "Konoshevskyi O.L.", "c_role_1": "Associate Professor", "c_phone_1": "...", "c_person_2": "Panasenko O.B.", "c_role_2": "Associate Professor", "c_phone_2": "...", "feedback_label": "Message", "send_btn": "Send", "footer_rights": "© 2025 Yasinskyi Geometry Olympiad.",
        "method_title": "Methodological Cabinet", "mt_tab1": "🛠️ Generator", "mt_tab2": "✒️ LaTeX Editor", "mt_tab3": "📂 Syllabus", "mt_tab4": "📊 Reports",
        "gen_topic": "Topic:", "gen_diff": "Difficulty:", "gen_btn": "Generate", "topics": ["Quadratic Eq", "Vectors"], "diffs": ["Basic", "Advanced"],
        "latex_desc": "Type LaTeX for image.", "latex_placeholder": r"\int", "latex_btn": "Download PNG",
        "syl_desc": "Syllabuses", "syl_btn": "Download", "report_gen_title": "Report Generator", "report_desc": "Auto-text.", "btn_gen_report": "Generate", "report_label": "Text:", "report_template": "Report..."
    }
}

# --- 4. Змінні та Кешування ---
# ВАЖЛИВО: Назви файлів мають точно збігатися з тим, що у вас на GitHub
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
    except Exception as e:
        return []

# Допоміжна функція для рендеру LaTeX
def latex_to_image(formula, fontsize=16, dpi=300):
    if not MATPLOTLIB_AVAILABLE:
        return None
    buf = io.BytesIO()
    fig = plt.figure(figsize=(6, 1.5))
    fig.text(0.5, 0.5, f"${formula}$", size=fontsize, ha='center', va='center')
    plt.axis('off')
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=dpi, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf

# --- 5. Сайдбар ---
with st.sidebar:
    lang_sel = st.selectbox("Language / Мова", ["UA", "ENG"])
    lang = "ua" if lang_sel == "UA" else "en"
    t = TRANSLATIONS[lang]
    st.markdown("---")
    st.title(t["nav_title"])
    menu_options = list(t["menu_items"].values())
    selected_item = st.radio("Go to:", menu_options, label_visibility="collapsed")
    current_page = [k for k, v in t["menu_items"].items() if v == selected_item][0]
    st.markdown("---")
    st.caption(t["uni_name"].replace("<br>", " "))

# --- 6. Шапка (З ЛОГОТИПОМ) ---
col_l, col_c, col_r = st.columns([1, 6, 1])
with col_l:
    # Перевіряємо, чи існує файл логотипу, перш ніж показувати
    if os.path.exists(LOGO_FILE): 
        st.image(LOGO_FILE, width=100)
    else: 
        st.write("🏛️") 
with col_c:
    st.markdown(f'<h2 class="header-university">{t["uni_name"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-faculty">{t["faculty_name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-dept">{t["dept_name"]}</div>', unsafe_allow_html=True)

# --- 7. Контент ---

# === HOME ===
if current_page == "home":
    st.title(t["banner_title"])
    tab_gen, tab_bio, tab_faq = st.tabs([t["tab_general"], t["tab_bio"], t["tab_faq"]])

    with tab_gen:
        col1, col2 = st.columns([1, 2])
        with col1:
            # Тут використовуємо фото Ясінського
            if os.path.exists(PHOTO_YASINSKYI):
                st.image(PHOTO_YASINSKYI, caption="В. А. Ясінський", use_container_width=True)
            else:
                st.image("https://via.placeholder.com/300x400", caption="Фото відсутнє", use_container_width=True)
        with col2:
            st.markdown(t["about_desc"])
            st.markdown(f"### {t['rules_title']}")
            st.markdown('<div class="rules-card">', unsafe_allow_html=True)
            for rule in t["rules_list"]: st.markdown(f"{rule}")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("📐 " + t["math_beauty_title"])
        st.info(t["math_beauty_desc"])
        st.latex(r"\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C} = 2R")

    # --- ВКЛАДКА БІОГРАФІЇ (ОНОВЛЕНА) ---
    with tab_bio:
        st.markdown(f"### {t['bio_title']}")
        c_bio_img, c_bio_txt = st.columns([1, 2])
        
        with c_bio_img:
            if os.path.exists(PHOTO_YASINSKYI):
                st.image(PHOTO_YASINSKYI, use_container_width=True)
                st.caption("Легенда олімпіадного руху")
        
        with c_bio_txt:
            st.markdown(f'<div class="quote-card">{t["bio_quote"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bio-text">{t["bio_full_text"]}</div>', unsafe_allow_html=True)

    with tab_faq:
        st.subheader("FAQ")
        for q, a in [(t["faq_q1"], t["faq_a1"]), (t["faq_q2"], t["faq_a2"]), (t["faq_q3"], t["faq_a3"])]:
            with st.expander(q): st.write(a)

# === CURRENT ===
elif current_page == "current":
    st.title(t["current_title"])
    col1, col2 = st.columns(2)
    with col1: st.metric(label=t["next_date_label"], value=t["next_date_val"])
    with col2: st.info("Status: **Planned**")
    st.markdown("---")
    st.subheader(t["reg_title"])
    with st.form("reg"):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input(t["f_name"])
            st.text_input(t["f_email"])
            st.text_input(t["f_city"])
            st.selectbox(t["f_grade"], ["8", "9", "10", "11"])
        with c2:
            st.text_input(t["f_surname"])
            st.text_input(t["f_country"])
            st.text_input(t["f_school"])
            st.file_uploader(t["f_file"], type=["pdf"])
        if st.form_submit_button(t["f_submit"], type="primary"):
            st.success(t["success_msg"])

# === ARCHIVE ===
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
                st.download_button("💾 Download ZIP", b, "archive.zip", "application/zip")
            else: st.error("Error.")
    st.markdown("---")
    links = get_live_pdf_links()
    for y in range(2025, 2016, -1):
        with st.expander(f"{y}"):
            yl = [x for x in links if str(y) in x['name']]
            if yl:
                for l in yl: st.link_button(f"📄 {l['name']}", l['url'])
            else: st.caption("Empty.")

# === HISTORY ===
elif current_page == "history":
    st.title(t["hist_title"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t["metric_participants"], "139", "+81")
    c2.metric(t["metric_countries"], "7")
    c3.metric(t["abs_winner"], "Ivan Ivanov")
    st.subheader(t["winners_table_title"])
    st.dataframe(pd.DataFrame({"Name": ["I. Ivanov", "P. Petrenko"], "Score": [42, 40]}), use_container_width=True)
    st.subheader(t["chart_title"])
    st.bar_chart(pd.DataFrame({'Year': ['2023', '2024', '2025'], 'Val': [100, 58, 139]}).set_index('Year'), color="#800000")

# === CONTACTS ===
elif current_page == "contacts":
    st.title(t["contact_page_title"])
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"### {t['contact_title']}")
        st.markdown(f"**{t['contact_address_label']}**<br>{t['contact_address_val']}", unsafe_allow_html=True)
        st.markdown(f"**{t['contact_email_label']}** {t['contact_email_val']}")
        st.markdown("---")
        st.markdown(f"""<div class="contact-card">{t['c_person_1']}<br><small>{t['c_role_1']}</small><br>📞 {t['c_phone_1']}</div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="contact-card">{t['c_person_2']}<br><small>{t['c_role_2']}</small><br>📞 {t['c_phone_2']}</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"### {t['feedback_label']}")
        st.text_area("")
        st.button(t["send_btn"])

# === METHODOLOGICAL (РОЗШИРЕНИЙ РОЗДІЛ) ===
elif current_page == "method":
    st.title(t["method_title"])
    
    tab1, tab2, tab3, tab4 = st.tabs([t["mt_tab1"], t["mt_tab2"], t["mt_tab3"], t["mt_tab4"]])
    
    # 1. Генератор варіантів
    with tab1:
        st.markdown("### " + t["mt_tab1"])
        c_gen1, c_gen2 = st.columns(2)
        with c_gen1:
            sel_topic = st.selectbox(t["gen_topic"], t["topics"])
        with c_gen2:
            sel_diff = st.selectbox(t["gen_diff"], t["diffs"])
        
        if st.button(t["gen_btn"], type="primary"):
            st.success(f"Згенеровано варіант: **{sel_topic}** ({sel_diff})")
            st.info("Файл готовий до завантаження (імітація).")
            st.download_button("📥 Завантажити PDF", "Demo Content", file_name=f"Test_{sel_topic}.pdf")

    # 2. LaTeX Редактор
    with tab2:
        st.markdown("### " + t["mt_tab2"])
        
        if not MATPLOTLIB_AVAILABLE:
            st.warning("⚠️ Для генерації картинок потрібна бібліотека 'matplotlib'. Будь ласка, додайте її у файл requirements.txt.")
        else:
            st.caption(t["latex_desc"])
            col_inp, col_out = st.columns([1, 1])
            with col_inp:
                latex_input = st.text_area("LaTeX Code:", value=t["latex_placeholder"], height=150)
            with col_out:
                st.markdown("**Preview:**")
                if latex_input:
                    st.latex(latex_input)
                    try:
                        img_buffer = latex_to_image(latex_input)
                        if img_buffer:
                            st.download_button(label=t["latex_btn"], data=img_buffer, file_name="formula.png", mime="image/png")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # 3. Банк силабусів
    with tab3:
        st.markdown("### " + t["mt_tab3"])
        st.caption(t["syl_desc"])
        syllabus_data = [
            {"code": "ОК 12", "name": "Алгебра та теорія чисел", "level": "Бакалавр", "file": "syl_alg.pdf"},
            {"code": "ОК 14", "name": "Геометрія", "level": "Бакалавр", "file": "syl_geom.pdf"},
        ]
        for item in syllabus_data:
            c_s1, c_s2, c_s3 = st.columns([1, 4, 1])
            c_s1.write(f"**{item['code']}**")
            c_s2.write(item['name'])
            with c_s3:
                st.download_button("⬇️ PDF", "demo content", file_name=item['file'], key=item['code'])
            st.divider()

    # 4. Звіти
    with tab4:
        st.markdown("### " + t["mt_tab4"])
        st.info(t["report_desc"])
        if st.button(t["btn_gen_report"]):
            stats = {"total": 139, "countries": 7, "regions": 12, "avg_score": 18.5, "schools": "Ліцей №17; Русанівський ліцей"}
            rep = t["report_template"].format(**stats)
            st.text_area(t["report_label"], rep, height=300)
            st.caption("Графік успішності:")
            st.bar_chart(pd.DataFrame({"Marks": [5, 12, 45, 30, 10]}, index=["0-10", "10-20", "20-30", "30-34", "35"]))

# --- 8. Футер ---
st.markdown("---")
st.markdown(
    f"""<div class="footer"><p>{t['footer_rights']}</p></div>""",
    unsafe_allow_html=True
)
