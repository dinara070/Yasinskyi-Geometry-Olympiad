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
        
        "banner_title": "Геометрична олімпіада імені В'ячеслава Ясінського",
        "about_desc": """
        **Геометрична олімпіада імені В'ячеслава Ясінського** — це унікальне щорічне змагання, започатковане у **2017 році**, яке об'єднує талановиту молодь, закохану в красу геометричних побудов та логічних міркувань.
        
        Олімпіада носить ім'я видатного педагога, **В'ячеслава Андрійовича Ясінського**, чий внесок у розвиток олімпіадного руху в Україні є неоціненним. Наша мета — не просто визначити найсильніших, а й показати естетику математики, розвинути просторову уяву та креативне мислення учнів.
        """,
        "rules_title": "Правила та формат проведення",
        "rules_list": [
            "👥 **Учасники:** До участі запрошуються учні 8-11 класів загальноосвітніх навчальних закладів.",
            "💻 **Формат:** Змагання проходить онлайн (дистанційно), що дозволяє долучитися учасникам з будь-якого куточка світу.",
            "🧩 **Завдання:** Пропонується розв'язати 5 авторських геометричних задач різного рівня складності.",
            "⏳ **Тривалість:** На виконання роботи відводиться 4 астрономічні години.",
            "⚖️ **Оцінювання:** Кожна задача оцінюється від 0 до 7 балів відповідно до критеріїв математичних олімпіад."
        ],
        "math_beauty_title": "Краса геометрії",
        "math_beauty_desc": "Геометрія — це мистецтво правильних міркувань на неправильних кресленнях. (Д. Пойя)",
        "example_problem_label": "Приклад олімпіадної задачі (Демонстрація)",
        "example_problem_text": """
        Нехай $ABC$ — гострокутний трикутник, в якому $AB < AC$. Коло $\omega$ проходить через точки $B$ і $C$ та перетинає сторони $AB$ і $AC$ у точках $D$ і $E$ відповідно.
        Доведіть, що якщо $BD = CE$, то:
        """,

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
        
        # Archive Theory (NEW)
        "archive_theory_title": "📘 Корисна теорія для олімпіадника",
        "theo_1_title": "Теорема Чеви",
        "theo_1_text": "Відрізки, що з'єднують вершини трикутника з точками на протилежних сторонах, перетинаються в одній точці тоді й тільки тоді, коли:",
        "theo_2_title": "Теорема Менелая",
        "theo_2_text": "Три точки на сторонах трикутника (або їх продовженнях) лежать на одній прямій тоді й тільки тоді, коли:",
        "theo_3_title": "Теорема Птолемея",
        "theo_3_text": "Для вписаного чотирикутника добуток діагоналей дорівнює сумі добутків протилежних сторін:",

        # Contacts & Footer
        "contact_page_title": "📞 Контакти",
        "invite_text": "Геометрична олімпіада імені В’ячеслава Ясінського запрошує математиків, педагогів та авторів геометричних задач до співпраці, щоб перетворити цю олімпіаду на подію світового рівня.",
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

        # Archive Theory (NEW)
        "archive_theory_title": "📘 Useful Theory for Olympiads",
        "theo_1_title": "Ceva's Theorem",
        "theo_1_text": "Cevians AD, BE, CF are concurrent if and only if:",
        "theo_2_title": "Menelaus' Theorem",
        "theo_2_text": "Points D, E, F on the sides (or extensions) are collinear if and only if:",
        "theo_3_title": "Ptolemy's Theorem",
        "theo_3_text": "For a cyclic quadrilateral, the product of diagonals equals the sum of products of opposite sides:",

        "contact_page_title": "📞 Contacts",
        "invite_text": "The Yasinskyi Geometry Olympiad invites mathematicians, educators, and authors of geometry problems to collaborate to transform this Olympiad into a world-class event.",
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

# === HOME ===
if current_page == "home":
    st.title(t["banner_title"])
    st.markdown(t["about_desc"])
    st.markdown("---")
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

# === ARCHIVE (Оновлено: додано теорію) ===
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

    # --- НОВИЙ БЛОК ТЕОРІЇ ---
    st.markdown("---")
    st.subheader(t["archive_theory_title"])
    
    col_t1, col_t2, col_t3 = st.columns(3)
    
    with col_t1:
        st.info("📌 " + t["theo_1_title"])
        st.markdown(t["theo_1_text"])
        st.latex(r"\frac{AF}{FB} \cdot \frac{BD}{DC} \cdot \frac{CE}{EA} = 1")

    with col_t2:
        st.info("📌 " + t["theo_2_title"])
        st.markdown(t["theo_2_text"])
        st.latex(r"\frac{AF}{FB} \cdot \frac{BD}{DC} \cdot \frac{CE}{EA} = 1")
        
    with col_t3:
        st.info("📌 " + t["theo_3_title"])
        st.markdown(t["theo_3_text"])
        st.latex(r"AC \cdot BD = AB \cdot CD + BC \cdot AD")

# === HISTORY ===
elif current_page == "history":
    st.title(t["hist_title"])
    m1, m2, m3 = st.columns(3)
    m1.metric(t["metric_participants"], "139", "+81")
    m2.metric(t["metric_countries"], "7", "+1")
    m3.metric(t["abs_winner"], "Ivan Ivanov", "42 pts")
    st.markdown("---")
    st.subheader(t["winners_table_title"])
    winners_data = {
        "Rank": [1, 2, 2, 3, 3],
        "Name": ["Ivan Ivanov", "Maria Petrenko", "John Doe", "Olga S.", "Taras K."],
        "Country": ["Ukraine", "Ukraine", "USA", "Poland", "Ukraine"],
        "Score": [42, 40, 40, 38, 38],
        "Award": ["Gold", "Silver", "Silver", "Bronze", "Bronze"]
    }
    df_winners = pd.DataFrame(winners_data)
    st.dataframe(df_winners, use_container_width=True, hide_index=True)
    st.markdown("---")
    st.subheader(t["chart_title"])
    data = {'Year': ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'],
            'Participants': [58, 76, 129, 136, 169, 145, 100, 58, 139]}
    st.bar_chart(pd.DataFrame(data).set_index('Year'), color="#800000")

# === CONTACTS ===
elif current_page == "contacts":
    st.title(t["contact_page_title"])
    
    st.success(f"🤝 **{t['invite_text']}**")
    st.markdown("---")

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

# === METHODOLOGICAL (ГЕНЕРАТОР КАРТОК) ===
elif current_page == "method":
    st.title(t["menu_items"]["method"])
    
    st.markdown("""
    ### 🎓 Вітаємо у методичному кабінеті!
    Цей інструмент розроблено спеціально для допомоги вчителям математики, керівникам гуртків та студентам.
    Тут ви можете автоматично згенерувати індивідуальні картки із завданнями для перевірки знань учнів або підготовки до олімпіад.
    
    **Як користуватися генератором:**
    1. Оберіть тему зі списку доступних.
    2. Вкажіть бажану кількість задач за допомогою повзунка.
    3. (Опціонально) Додайте примітку для студента.
    4. Натисніть кнопку **"Згенерувати картку"**.
    5. Завантажте готовий текстовий файл.
    """)
    st.info("💡 База даних постійно оновлюється новими авторськими задачами кафедри.")

    # --- 1. База даних тем та задач (5 тем по 3 задачі) ---
    topic_database = {
        "Вписані та описані кола": [
            "1. У трикутник зі сторонами 10, 10, 12 вписано коло. Знайдіть його радіус.",
            "2. Доведіть, що сума протилежних сторін описаного чотирикутника рівна.",
            "3. Знайдіть радіус кола, описаного навколо рівнобічної трапеції з основами 8 і 16 та висотою 4."
        ],
        "Подібність трикутників": [
            "1. Сторони трикутника відносяться як 4:5:7. Знайдіть сторони подібного йому трикутника, якщо його периметр дорівнює 48 см.",
            "2. У трикутнику ABC проведено пряму, паралельну стороні AC. Знайдіть відрізки, на які вона ділить сторони AB і BC.",
            "3. Доведіть, що висота прямокутного трикутника, проведена до гіпотенузи, ділить його на два подібні трикутники."
        ],
        "Площі фігур": [
            "1. Знайдіть площу ромба, якщо його діагоналі дорівнюють 10 см і 24 см.",
            "2. Площа трикутника ABC дорівнює S. Знайдіть площу трикутника, вершини якого є серединами сторін трикутника ABC.",
            "3. Обчисліть площу паралелограма, якщо його сторони 8 см і 12 см, а кут між ними 30 градусів."
        ],
        "Теорема Піфагора та прямокутні трикутники": [
            "1. Катети прямокутного трикутника відносяться як 3:4, а гіпотенуза дорівнює 25 см. Знайдіть периметр трикутника.",
            "2. Знайдіть висоту прямокутного трикутника, проведену до гіпотенузи, якщо проекції катетів на гіпотенузу дорівнюють 9 см і 16 см.",
            "3. У прямокутному трикутнику бісектриса гострого кута ділить протилежний катет на відрізки довжиною 4 см і 5 см. Знайдіть площу трикутника."
        ],
        "Теореми синусів і косинусів": [
            "1. Сторони трикутника дорівнюють 5 см, 7 см і 8 см. Знайдіть кут, що лежить проти середньої за довжиною сторони.",
            "2. У трикутнику ABC відомо, що AC = 6 см, кут A = 45 градусів, кут B = 60 градусів. Знайдіть сторону BC.",
            "3. Сторони паралелограма дорівнюють 4 см і 5 см, а кут між ними 60 градусів. Знайдіть діагоналі паралелограма."
        ]
    }

    st.markdown("---")
    st.markdown("### 🗂 Генератор методичної картки")
    
    with st.form("method_gen"):
        selected_topic = st.selectbox("Оберіть тему картки:", list(topic_database.keys()))
        available_count = len(topic_database[selected_topic])
        count = st.slider("Кількість задач:", 1, available_count, 1)
        teacher_note = st.text_input("Примітка для студента (опціонально):")
        
        submitted = st.form_submit_button("Згенерувати картку")

    if submitted:
        problems = topic_database[selected_topic][:count]
        card_content = f"МЕТОДИЧНА КАРТКА\nТема: {selected_topic}\n"
        if teacher_note:
            card_content += f"Примітка: {teacher_note}\n"
        card_content += "-" * 30 + "\n\n"
        
        for task in problems:
            card_content += f"{task}\n\n"
        
        card_content += "-" * 30 + "\nБажаємо успіхів!\nКафедра алгебри і методики навчання математики ВДПУ"

        st.success("Картку успішно згенеровано! Ви можете завантажити її нижче.")
        
        col_d1, col_d2 = st.columns([1, 2])
        with col_d1:
            st.download_button(
                label="📥 Завантажити картку (.txt)",
                data=card_content,
                file_name=f"card_{selected_topic}.txt",
                mime="text/plain"
            )
        
        with st.expander("Переглянути вміст картки"):
            st.text(card_content)

# --- 7. Футер ---
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
