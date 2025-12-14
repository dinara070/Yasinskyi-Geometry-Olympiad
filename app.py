import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import io
import zipfile
import pandas as pd
import os
from datetime import datetime

# --- 1. Налаштування сторінки ---
st.set_page_config(
    page_title="Portal of the Department of Algebra and Methods of Teaching Mathematics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Словник перекладів (UA / EN) ---
TRANSLATIONS = {
    "ua": {
        "uni_name": "Вінницький державний педагогічний університет<br>імені Михайла Коцюбинського",
        "faculty_name": "Факультет математики, фізики і комп'ютерних наук",
        "dept_name": "Кафедра алгебри і методики навчання математики",
        "nav_title": "Навігація",
        "nav_options": ["🏠 Головна кафедри", "📐 Олімпіада ім. В. Ясінського", "📝 Методичний кабінет", "📞 Контакти"],
        "footer": "© 2025 ВДПУ ім. М. Коцюбинського | Кафедра алгебри і методики навчання математики",
        "dev_info": "Розроблено для підтримки навчального процесу та олімпіадного руху.",
        
        # Головна
        "home_welcome": "Вітаємо на цифровому порталі кафедри!",
        "home_desc": """
        <div class="info-card">
        Цей ресурс створено для студентів, викладачів та вчителів математики. Тут ви знайдете:
        <ul>
            <li>Матеріали для підготовки до олімпіад.</li>
            <li>Інструменти для створення методичних карток.</li>
            <li>Архіви задач та наукових робіт.</li>
        </ul>
        </div>
        """,
        "news_title": "📢 Оголошення",
        "news_1": "Оновлено базу олімпіадних задач.",
        "news_2": "Запрошуємо до участі у конкурсі творчих робіт.",
        "science_title": "🔬 Наукова робота",
        "science_1": "Методика навчання алгебри",
        "science_2": "Олімпіадна геометрія",

        # Олімпіада
        "olymp_title": "Олімпіада геометричної творчості імені В. А. Ясінського",
        "tab_about": "ℹ️ Про олімпіаду",
        "tab_archive": "📚 Архів задач",
        "tab_stats": "📊 Статистика",
        "yasinskyi_caption": "**В’ячеслав Андрійович Ясінський** (1957-2015)",
        "olymp_history": """
            У **2017 році** кафедра алгебри і методики навчання математики Вінницького державного педагогічного університету імені Михайла Коцюбинського започаткувала проведення **Олімпіади геометричної творчості імені В. А. Ясінського**.
            """,
        "olymp_directions_title": "Напрямки проведення заходу:",
        "olymp_directions_list": """
            Захід проходить у ВДПУ ім. М. Коцюбинського за такими напрямками:
            * 🧑‍🏫 **Турнір методичних знахідок** (для вчителів геометрії).
            * ✏️ **Змагання з розв’язування геометричних задач** (для учнів).
            * 🎨 **Конкурс творчих робіт з геометрії** (для колективів учнів під керівництвом учителя).
            """,
        "olymp_regulations": "📜 Пропонуємо ознайомитись із **Положенням про Олімпіаду** (зверніться на кафедру або завантажте нижче).",
        "archive_desc": "Автоматизований модуль для завантаження методичних матеріалів олімпіади.",
        "btn_download": "🚀 Завантажити повний архів задач (PDF)",
        "msg_connecting": "З'єднання з сервером олімпіади...",
        "msg_success": "Архівація завершена!",
        "msg_error": "Помилка доступу до джерела.",

        # Методичний кабінет
        "method_title": "🛠️ Генератор методичної картки уроку",
        "form_topic": "Тема уроку",
        "form_grade": "Клас",
        "form_goal": "Мета уроку",
        "form_type": "Тип уроку",
        "form_btn": "🖨️ Згенерувати картку",
        "card_success": "Картка згенерована!",
        "card_template": "ПЛАН-КОНСПЕКТ УРОКУ",

        # Контакти
        "contact_address_title": "📍 Наша адреса",
        "contact_address": """
        **21100, м. Вінниця, вул. Острозького, 32**<br>Факультет математики, фізики і комп'ютерних наук<br>
        **Корпус 3, поверх 5.**
        """,
        "contact_phones_title": "☎️ Контактні телефони:",
        "role_docent": "доцент кафедри алгебри і методики навчання математики",
        "role_senior": "старший викладач кафедри алгебри і методики навчання математики"
    },
    "en": {
        "uni_name": "Vinnytsia Mykhailo Kotsiubynskyi<br>State Pedagogical University",
        "faculty_name": "Faculty of Mathematics, Physics and Computer Science",
        "dept_name": "Department of Algebra and Methods of Teaching Mathematics",
        "nav_title": "Navigation",
        "nav_options": ["🏠 Department Home", "📐 Yasinskyi Olympiad", "📝 Methodological Cabinet", "📞 Contacts"],
        "footer": "© 2025 VSPU named after M. Kotsiubynskyi | Department of Algebra and Methods of Teaching Mathematics",
        "dev_info": "Developed to support the educational process and the Olympiad movement.",

        # Home
        "home_welcome": "Welcome to the Department's Digital Portal!",
        "home_desc": """
        <div class="info-card">
        This resource was created for students, lecturers, and mathematics teachers. Here you will find:
        <ul>
            <li>Materials for Olympiad preparation.</li>
            <li>Tools for creating methodological lesson cards.</li>
            <li>Archives of problems and scientific works.</li>
        </ul>
        </div>
        """,
        "news_title": "📢 Announcements",
        "news_1": "Olympiad problem database updated.",
        "news_2": "We invite you to participate in the creative works contest.",
        "science_title": "🔬 Scientific Work",
        "science_1": "Methods of Teaching Algebra",
        "science_2": "Olympiad Geometry",

        # Olympiad
        "olymp_title": "Yasinskyi Olympiad of Geometric Creativity",
        "tab_about": "ℹ️ About the Olympiad",
        "tab_archive": "📚 Problem Archive",
        "tab_stats": "📊 Statistics",
        "yasinskyi_caption": "**Vyacheslav Andriyovych Yasinskyi** (1957-2015)",
        "olymp_history": """
            In **2017**, the Department of Algebra and Methods of Teaching Mathematics at Vinnytsia State Pedagogical University initiated the **Yasinskyi Olympiad of Geometric Creativity**.
            """,
        "olymp_directions_title": "Event Directions:",
        "olymp_directions_list": """
            The event is held at VSPU named after M. Kotsiubynskyi in the following directions:
            * 🧑‍🏫 **Tournament of Methodological Findings** (for geometry teachers).
            * ✏️ **Competition in solving geometric problems** (for students).
            * 🎨 **Contest of creative works in geometry** (for student teams under teacher supervision).
            """,
        "olymp_regulations": "📜 We suggest reviewing the **Regulations on the Olympiad** (contact the department or download below).",
        "archive_desc": "Automated module for downloading Olympiad methodological materials.",
        "btn_download": "🚀 Download Full Problem Archive (PDF)",
        "msg_connecting": "Connecting to the Olympiad server...",
        "msg_success": "Archiving completed!",
        "msg_error": "Error accessing source.",

        # Methodological Cabinet
        "method_title": "🛠️ Lesson Plan Generator",
        "form_topic": "Lesson Topic",
        "form_grade": "Grade",
        "form_goal": "Lesson Objective",
        "form_type": "Lesson Type",
        "form_btn": "🖨️ Generate Card",
        "card_success": "Card generated successfully!",
        "card_template": "LESSON PLAN CONSPECTUS",

        # Contacts
        "contact_address_title": "📍 Our Address",
        "contact_address": """
        **21100, Vinnytsia, Ostrozkoho Str., 32**<br>Faculty of Mathematics, Physics and Computer Science<br>
        **Building 3, 5th Floor.**
        """,
        "contact_phones_title": "☎️ Contact Phones:",
        "role_docent": "Associate Professor, Department of Algebra and Methods of Teaching Mathematics",
        "role_senior": "Senior Lecturer, Department of Algebra and Methods of Teaching Mathematics"
    }
}

# --- 3. CSS та Стилі ---
st.markdown("""
    <style>
    .header-university { color: #800000; font-family: 'Times New Roman', serif; text-align: center; margin-bottom: 0px; }
    .header-faculty { color: #2c3e50; font-family: sans-serif; text-align: center; font-size: 1.2rem; margin-top: 0px; font-weight: bold; }
    .header-dept { color: #555; text-align: center; font-style: italic; margin-bottom: 20px; border-bottom: 2px solid #800000; padding-bottom: 10px; }
    .info-card { padding: 20px; border-radius: 10px; background-color: #f8f9fa; border-left: 5px solid #800000; margin-bottom: 20px; }
    .stButton>button { background-color: #800000; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #a00000; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Змінні ---
PHOTO_YASINSKYI = "yasinskyi.png"
LOGO_FILE = "logo.png" 

# --- 5. Допоміжні функції ---
def get_pdf_links(target_url):
    try:
        r = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        return [urljoin(target_url, a['href']) for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]
    except: return []

# --- 6. Навігація та Вибір мови ---
with st.sidebar:
    # Вибір мови
    lang_choice = st.selectbox("Language / Мова", ["Українська", "English"])
    lang_code = "ua" if lang_choice == "Українська" else "en"
    t = TRANSLATIONS[lang_code] # Завантажуємо потрібний словник

    st.markdown("---")
    st.title(t["nav_title"])
    
    # Меню (відображаємо текст залежно від мови, але логіку зберігаємо по індексу)
    selected_option_text = st.radio("Menu", t["nav_options"], label_visibility="collapsed")
    
    # Визначаємо, який розділ обрано (за індексом), щоб код знав, що показувати
    menu_index = t["nav_options"].index(selected_option_text)
    
    st.markdown("---")
    st.info(t["dev_info"])

# --- 7. Шапка (Header) ---
col_l, col_c, col_r = st.columns([1, 6, 1])
with col_l:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=100)
    else: st.write("🏛️") 

with col_c:
    st.markdown(f'<h2 class="header-university">{t["uni_name"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-faculty">{t["faculty_name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-dept">{t["dept_name"]}</div>', unsafe_allow_html=True)

# --- 8. ЛОГІКА СТОРІНОК ---

# === 0. ГОЛОВНА (HOME) ===
if menu_index == 0:
    st.subheader(t["home_welcome"])
    st.markdown(t["home_desc"], unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {t['news_title']}")
        st.info(f"📅 **{datetime.now().strftime('%d.%m.%Y')}**: {t['news_1']}")
        st.write(f"🔹 {t['news_2']}")
        
    with col2:
        st.markdown(f"### {t['science_title']}")
        st.progress(85, text=t["science_1"])
        st.progress(70, text=t["science_2"])

# === 1. ОЛІМПІАДА (OLYMPIAD) ===
elif menu_index == 1:
    st.markdown(f"### 🏆 {t['olymp_title']}")
    
    tab1, tab2, tab3 = st.tabs([t["tab_about"], t["tab_archive"], t["tab_stats"]])
    
    with tab1:
        col_img, col_text = st.columns([1, 2])
        with col_img:
            if os.path.exists(PHOTO_YASINSKYI):
                st.image(PHOTO_YASINSKYI, use_container_width=True)
                st.caption(t["yasinskyi_caption"])
            else:
                st.warning("No photo / Фото відсутнє")
        
        with col_text:
            st.markdown(t["olymp_history"])
            st.markdown(f"#### {t['olymp_directions_title']}")
            st.markdown(t["olymp_directions_list"])
            st.info(t["olymp_regulations"])

    with tab2:
        st.write(t["archive_desc"])
        if st.button(t["btn_download"]):
            with st.spinner(t["msg_connecting"]):
                links = get_pdf_links("https://yasinskyi-geometry-olympiad.com/")
                if links:
                    buf = io.BytesIO()
                    with zipfile.ZipFile(buf, "w") as zf:
                        for url in links:
                            try:
                                r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                                zf.writestr(unquote(url.split('/')[-1]), r.content)
                            except: pass
                    buf.seek(0)
                    st.success(t["msg_success"])
                    st.download_button("💾 ZIP", buf, "yasinskyi_archive.zip", "application/zip")
                else:
                    st.error(t["msg_error"])

    with tab3:
        data = {'Year': ['2021', '2022', '2023', '2024', '2025'], 'Participants': [169, 145, 100, 58, 139]}
        st.bar_chart(pd.DataFrame(data).set_index('Year'))

# === 2. МЕТОДИЧНИЙ КАБІНЕТ (METHODOLOGICAL CABINET) ===
elif menu_index == 2:
    st.markdown(f"### {t['method_title']}")
    with st.form("lesson_plan"):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(t["form_topic"], "Pythagorean theorem" if lang_code == 'en' else "Теорема Піфагора")
            grade = st.selectbox(t["form_grade"], ["7", "8", "9", "10", "11"])
        with col2:
            goal = st.text_area(t["form_goal"], "...")
            type_lesson = st.selectbox(t["form_type"], ["New knowledge" if lang_code=='en' else "Засвоєння нових знань", "Practice" if lang_code=='en' else "Практикум"])
        
        submitted = st.form_submit_button(t["form_btn"])
    
    if submitted:
        st.success(t["card_success"])
        st.code(f"{t['card_template']}\nClass: {grade} | Topic: {topic}\nType: {type_lesson}\nGoal: {goal}", language="text")

# === 3. КОНТАКТИ (CONTACTS) ===
elif menu_index == 3:
    st.markdown(f"### {t['contact_address_title']}")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(t["contact_address"], unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"### {t['contact_phones_title']}")
        st.write(f"🧑‍🏫 **Konoshevskyi Oleh Leonidovych**" if lang_code == 'en' else "🧑‍🏫 **Коношевський Олег Леонідович**")
        st.caption(t["role_docent"])
        st.write("📞 `(067) 29-010-78`")
        
        st.markdown("---")
        
        st.write(f"🧑‍🏫 **Panasenko Oleksii Borysovych**" if lang_code == 'en' else "🧑‍🏫 **Панасенко Олексій Борисович**")
        st.caption(t["role_senior"])
        st.write("📞 `(067) 215-15-71`")
        st.write("📞 `(063) 153-04-67`")
    
    st.markdown("---")
    st.map(pd.DataFrame({'lat': [49.2325], 'lon': [28.4833]}))

# --- Підвал ---
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: gray;'>{t['footer']}</div>", unsafe_allow_html=True)
