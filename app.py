import streamlit as st
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import io
import zipfile

# --- 1. Налаштування сторінки (Page Config) ---
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
    
    /* Картки */
    .rules-card { background-color: #f0f8ff; padding: 20px; border-radius: 8px; border-left: 5px solid #007bff; margin-bottom: 15px; }
    .contact-card { background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .bio-card { background-color: #f9f9f9; padding: 20px; border-radius: 10px; border: 1px solid #ddd; }
    
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
    
    /* Кнопки */
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 3. Словник перекладів ---
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
        
        # BIO
        "bio_title": "В'ячеслав Андрійович Ясінський (1957-2015)",
        "bio_text": """
        **В'ячеслав Андрійович Ясінський** — видатний український педагог, доцент, Заслужений вчитель України. 
        Він присвятив своє життя навчанню обдарованої молоді та популяризації олімпіадного руху.
        
        В'ячеслав Андрійович був справжнім Майстром геометричної задачі. Його авторські задачі прикрашали не лише українські, 
        а й міжнародні математичні олімпіади. Ця олімпіада створена, щоб продовжити його справу — закохувати учнів у красу геометрії.
        """,
        
        # FAQ
        "faq_q1": "Чи участь в олімпіаді платна?",
        "faq_a1": "Ні, участь в олімпіаді є повністю безкоштовною.",
        "faq_q2": "Як оформити розв'язок?",
        "faq_a2": "Розв'язки можна писати від руки (розбірливо) та сканувати, або набирати в редакторах (MS Word, LaTeX). Формат файлу — PDF.",
        "faq_q3": "Хто може брати участь?",
        "faq_a3": "Завдання розраховані на учнів 8-11 класів, але молодші школярі також можуть спробувати свої сили.",

        # Current
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
        
        # Archive & History
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
        "footer_rights": "© 2025 Yasinskyi Geometry Olympiad. Всі права захищено."
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
        # HOME Tabs
        "tab_general": "ℹ️ General Info",
        "tab_bio": "👤 Bio of V. Yasinskyi",
        "tab_faq": "❓ FAQ",

        "banner_title": "Yasinskyi Geometry Olympiad",
        "about_desc": """
        **The Yasinskyi Geometry Olympiad** is an annual competition that brings together fans of geometry problems. 
        It was first held by the Department of Algebra and Teaching Methods of VSPU in **2017**.
        """,
        "rules_title": "Rules and Format",
        "rules_list": [
            "👥 **Participants:** Students of grades 8-11.",
            "💻 **Format:** Online.",
            "🧩 **Tasks:** 5 geometry problems.",
            "⏳ **Duration:** 4 hours.",
            "⚖️ **Grading:** 0 to 7 points per problem."
        ],
        "math_beauty_title": "Geometry Aesthetics",
        "math_beauty_desc": "Geometry is the art of correct reasoning on incorrect figures. (G. Polya)",
        "example_problem_label": "Example Problem (Demo)",
        "example_problem_text": """
        Let $ABC$ be an acute-angled triangle where $AB < AC$. A circle $\omega$ passes through points $B$ and $C$ and intersects sides $AB$ and $AC$ at points $D$ and $E$ respectively.
        Prove that if $BD = CE$, then:
        """,

        # BIO
        "bio_title": "Vyacheslav Andriyovych Yasinskyi (1957-2015)",
        "bio_text": """
        **Vyacheslav Andriyovych Yasinskyi** was an outstanding Ukrainian educator, associate professor, and Honored Teacher of Ukraine. 
        He dedicated his life to teaching gifted youth and promoting the Olympiad movement.
        
        Vyacheslav Andriyovych was a true Master of geometric problems. His authored problems adorned not only Ukrainian 
        but also international mathematical Olympiads. This competition was created to continue his legacy — to make students fall in love with the beauty of geometry.
        """,

        # FAQ
        "faq_q1": "Is participation free?",
        "faq_a1": "Yes, participation in the Olympiad is completely free.",
        "faq_q2": "How to format the solution?",
        "faq_a2": "Solutions can be handwritten (legibly) and scanned, or typed (MS Word, LaTeX). File format — PDF.",
        "faq_q3": "Who can participate?",
        "faq_a3": "Tasks are designed for students in grades 8-11.",

        "current_title": "Olympiad 2025/2026",
        "next_date_label": "Next Olympiad Date:",
        "next_date_val": "November 2026",
        "reg_title": "Registration and Submission",
        "reg_form_header": "Participant Form (Demo)",
        "f_name": "First Name", "f_surname": "Last Name", "f_email": "Email",
        "f_country": "Country", "f_city": "City", "f_school": "School (Full Name)",
        "f_grade": "Grade", "f_file": "Upload Solutions (PDF)",
        "f_submit": "Submit Work",
        "success_msg": "Your work has been submitted successfully!",
        "archive_title": "Materials Library (2017–2025)",
        "btn_zip": "🚀 Download ALL materials as ZIP",
        "zip_generating": "Scanning site and generating archive...",
        "link_view": "👁️ View/Download on Website",
        "hist_title": "Statistics and Hall of Fame",
        "metric_participants": "Participants in 2025",
        "metric_countries": "Participating Countries",
        "metric_total": "Total Participants",
        "chart_title": "Olympiad Growth Dynamics",
        "winners_table_title": "🏆 Last Olympiad Winners (Demo Data)",
        "abs_winner": "Absolute Winner 2024",

        "contact_page_title": "📞 Contacts",
        "contact_title": "Contact Organizers",
        "contact_subtitle_phones": "Contact Phones:",
        "contact_address_label": "Our Address:",
        "contact_address_val": "21100, Vinnytsia, Ostrozkoho Str., 32<br>Building 3, 5th Floor.",
        "contact_email_label": "Email:",
        "contact_email_val": "yasinskyi.geometry.olympiad@gmail.com",
        "c_person_1": "**Konoshevskyi Oleh Leonidovych**",
        "c_role_1": "Associate Professor, Department of Algebra and Methods of Teaching Mathematics",
        "c_phone_1": "+38 (067) 29-010-78",
        "c_person_2": "**Panasenko Oleksii Borysovych**",
        "c_role_2": "Associate Professor, Department of Algebra and Methods of Teaching Mathematics",
        "c_phone_2": "+38 (067) 215-15-71, +38 (063) 153-04-67",
        "feedback_label": "Send us a message",
        "send_btn": "Send",
        "footer_rights": "© 2025 Yasinskyi Geometry Olympiad. All rights reserved."
    }
}

# --- 4. Змінні та Кешування ---
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

# --- 5. Сайдбар ---
with st.sidebar:
    # 3. Багатомовність: Реалізовано через Selectbox, який оновлює змінну t
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

# --- 6. Шапка ---
col_l, col_c, col_r = st.columns([1, 6, 1])
with col_l:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=90)
    else: st.write("🏛️") 
with col_c:
    st.markdown(f'<h2 class="header-university">{t["uni_name"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-faculty">{t["faculty_name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-dept">{t["dept_name"]}</div>', unsafe_allow_html=True)

# --- 7. Контент ---

# === HOME (Оновлено: Tabs, Bio, FAQ) ===
if current_page == "home":
    st.title(t["banner_title"])
    
    # Використовуємо вкладки для кращої структури
    tab_gen, tab_bio, tab_faq = st.tabs([t["tab_general"], t["tab_bio"], t["tab_faq"]])
    
    # --- ВКЛАДКА 1: ЗАГАЛЬНЕ ---
    with tab_gen:
        col1, col2 = st.columns([1, 2])
        with col1:
            if os.path.exists(PHOTO_YASINSKYI):
                st.image(PHOTO_YASINSKYI, caption="В. А. Ясінський", use_container_width=True)
            else:
                st.warning("Фото відсутнє")
                st.image("https://via.placeholder.com/300x400", use_container_width=True)
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
        with st.expander(t["example_problem_label"]):
            st.markdown(t["example_problem_text"])
            st.latex(r"\angle A = 60^\circ")

    # --- ВКЛАДКА 2: БІОГРАФІЯ (4. Біографія В. Ясінського) ---
    with tab_bio:
        st.markdown(f"### {t['bio_title']}")
        c_bio_img, c_bio_txt = st.columns([1, 3])
        with c_bio_img:
            # Тут можна додати ефект "чорно-білого фото" через CSS, якщо треба, але просто фото теж ок
            if os.path.exists(PHOTO_YASINSKYI):
                st.image(PHOTO_YASINSKYI, use_container_width=True)
        with c_bio_txt:
            st.markdown(f'<div class="bio-card">{t["bio_text"]}</div>', unsafe_allow_html=True)

    # --- ВКЛАДКА 3: FAQ (6. Розділ FAQ) ---
    with tab_faq:
        st.subheader("Frequently Asked Questions")
        with st.expander(t["faq_q1"]): st.write(t["faq_a1"])
        with st.expander(t["faq_q2"]): st.write(t["faq_a2"])
        with st.expander(t["faq_q3"]): st.write(t["faq_a3"])

# === CURRENT ===
elif current_page == "current":
    st.title(t["current_title"])
    col1, col2 = st.columns(2)
    with col1: st.metric(label=t["next_date_label"], value=t["next_date_val"])
    with col2: st.info("Status: **Planned / Заплановано**")
    st.markdown("---")
    st.subheader(t["reg_title"])
    with st.form("registration_form"):
        st.markdown(f"**{t['reg_form_header']}**")
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
    st.info("💡 " + t["zip_generating"])
    if st.button(t["btn_zip"]):
        with st.spinner("Wait..."):
            links = get_live_pdf_links()
            if links:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for item in links:
                        try:
                            resp = requests.get(item["url"], headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                            if resp.status_code == 200: zf.writestr(item["name"], resp.content)
                        except: pass
                zip_buffer.seek(0)
                st.download_button("💾 Download .ZIP", zip_buffer, "yasinskyi_full_archive.zip", "application/zip")
            else: st.error("Error fetching files.")

    st.markdown("---")
    st.subheader("Live Links")
    all_links = get_live_pdf_links()
    for year in range(2025, 2016, -1):
        with st.expander(f"📁 {year}"):
            year_links = [L for L in all_links if str(year) in L['name']]
            if year_links:
                for link in year_links: st.link_button(f"📄 {link['name']} ({t['link_view']})", link['url'])
            else: st.caption("Web archive.")

# === HISTORY (Оновлено: 5. Інтерактивна галерея) ===
elif current_page == "history":
    st.title(t["hist_title"])
    
    # Метрики
    m1, m2, m3 = st.columns(3)
    m1.metric(t["metric_participants"], "139", "+81")
    m2.metric(t["metric_countries"], "7", "+1")
    m3.metric(t["abs_winner"], "Ivan Ivanov", "42 pts") # Приклад з st.metric
    
    st.markdown("---")
    
    # Інтерактивна таблиця
    st.subheader(t["winners_table_title"])
    # Демо-дані
    winners_data = {
        "Rank": [1, 2, 2, 3, 3],
        "Name": ["Ivan Ivanov", "Maria Petrenko", "John Doe", "Olga S.", "Taras K."],
        "Country": ["Ukraine", "Ukraine", "USA", "Poland", "Ukraine"],
        "Score": [42, 40, 40, 38, 38],
        "Award": ["Gold", "Silver", "Silver", "Bronze", "Bronze"]
    }
    df_winners = pd.DataFrame(winners_data)
    # st.dataframe дозволяє сортувати стовпці кліком
    st.dataframe(df_winners, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader(t["chart_title"])
    data = {'Year': ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'],
            'Participants': [58, 76, 129, 136, 169, 145, 100, 58, 139]}
    st.bar_chart(pd.DataFrame(data).set_index('Year'), color="#800000")

# === CONTACTS ===
elif current_page == "contacts":
    st.title(t["contact_page_title"]) 
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown(f"### {t['contact_title']}")
        st.markdown(f"""
        **{t['contact_address_label']}**<br>{t['contact_address_val']}<br><br>
        **{t['contact_email_label']}** {t['contact_email_val']}
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.subheader(t["contact_subtitle_phones"])
        st.markdown(f"""<div class="contact-card">{t['c_person_1']}<br><span style="color:grey; font-size:0.9em;">{t['c_role_1']}</span><br>📞 <b>{t['c_phone_1']}</b></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="contact-card">{t['c_person_2']}<br><span style="color:grey; font-size:0.9em;">{t['c_role_2']}</span><br>📞 <b>{t['c_phone_2']}</b></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"### {t['feedback_label']}")
        st.text_area("", height=150)
        st.button(t["send_btn"])

# === METHODOLOGICAL ===
elif current_page == "method":
    st.title(t["menu_items"]["method"])
    st.info("Розділ для студентів кафедри.")
    with st.form("method_gen"):
        st.write("Генератор методичної картки")
        st.text_input("Тема")
        st.form_submit_button("Згенерувати")

# --- 7. Футер (Підвал) ---
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align:center; color:grey; padding: 20px;'>
        <p>{t['footer_rights']}</p>
        <p>
            <a href="#" style="text-decoration: none; color: #800000;">Facebook</a> | 
            <a href="#" style="text-decoration: none; color: #800000;">Instagram</a> | 
            <a href="mailto:yasinskyi.geometry.olympiad@gmail.com" style="text-decoration: none; color: #800000;">Email</a>
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)
