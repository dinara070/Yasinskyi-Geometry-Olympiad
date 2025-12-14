import streamlit as st
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import io
import zipfile
import json
import hashlib # Для шифрування паролів

# --- 1. Налаштування сторінки ---
st.set_page_config(
    page_title="Yasinskyi Geometry Olympiad | VSPU",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. СИСТЕМА ФАЙЛІВ (CONFIG & USERS) ---
CONFIG_FILE = "site_config.json"
USERS_FILE = "users.json"

# --- 2.1 Налаштування сайту ---
DEFAULT_CONFIG = {
    "next_event_date_ua": "Листопад 2026 року",
    "next_event_date_en": "November 2026",
    "news_ua": "Оновлено базу олімпіадних задач.",
    "news_en": "Olympiad problem database updated.",
    "is_registration_open": False
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
        return DEFAULT_CONFIG
    else:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

site_config = load_config()

# --- 2.2 Система користувачів (Реєстрація/Вхід) ---
def hash_password(password):
    """Шифрує пароль у SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Завантажує користувачів або створює дефолтного адміна"""
    if not os.path.exists(USERS_FILE):
        # Створюємо першого адміна за замовчуванням
        default_users = {"admin": hash_password("admin123")}
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f, ensure_ascii=False, indent=4)
        return default_users
    else:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def save_users(users_data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

def authenticate(username, password):
    users = load_users()
    if username in users and users[username] == hash_password(password):
        return True
    return False

def register_user(username, password):
    users = load_users()
    if username in users:
        return False # Користувач вже існує
    users[username] = hash_password(password)
    save_users(users)
    return True

# --- 3. CSS Стилізація ---
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; }
    .header-university { color: #800000; font-family: 'Times New Roman', serif; text-align: center; margin-bottom: 0px; }
    .header-faculty { color: #2c3e50; font-family: sans-serif; text-align: center; font-size: 1.1rem; font-weight: bold; }
    .header-dept { color: #555; text-align: center; font-style: italic; margin-bottom: 20px; border-bottom: 2px solid #800000; padding-bottom: 10px; }
    .rules-card { background-color: #f0f8ff; padding: 20px; border-radius: 8px; border-left: 5px solid #007bff; margin-bottom: 15px; }
    .contact-card { background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .bio-card { background-color: #f9f9f9; padding: 20px; border-radius: 10px; border: 1px solid #ddd; }
    .stButton>button { width: 100%; border-radius: 5px; }
    .admin-box { border: 2px solid #e74c3c; padding: 20px; border-radius: 10px; background-color: #fff5f5; }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 4. Словник перекладів ---
TRANSLATIONS = {
    "ua": {
        "uni_name": "Вінницький державний педагогічний університет<br>імені Михайла Коцюбинського",
        "faculty_name": "Факультет математики, фізики і комп'ютерних наук",
        "dept_name": "Кафедра алгебри і методики навчання математики",
        "nav_title": "Меню навігації",
        "menu_items": {
            "home": "🏠 Про олімпіаду",
            "current": "📝 Поточна олімпіада",
            "archive": "📚 Архів задач",
            "history": "📊 Історія та результати",
            "contacts": "📞 Контакти",
            "method": "🎓 Методичний кабінет",
            "admin": "⚙️ Адмін-панель"
        },
        "banner_title": "Геометрична олімпіада імені В'ячеслава Ясінського",
        "tab_general": "ℹ️ Загальна інформація",
        "tab_bio": "👤 Біографія В. Ясінського",
        "tab_faq": "❓ FAQ",
        "about_desc": "**Геометрична олімпіада імені В'ячеслава Ясінського** — це щорічне змагання...",
        "rules_list": ["👥 **Учасники:** Учні 8-11 класів.", "💻 **Формат:** Онлайн.", "🧩 **Завдання:** 5 задач.", "⏳ **Тривалість:** 4 години.", "⚖️ **Оцінювання:** 0-7 балів."],
        "math_beauty_title": "Краса геометрії",
        "math_beauty_desc": "Геометрія — це мистецтво правильних міркувань на неправильних кресленнях. (Д. Пойя)",
        "bio_title": "В'ячеслав Андрійович Ясінський (1957-2015)",
        "bio_text": "Видатний український педагог, доцент, Заслужений вчитель України...",
        "current_title": "Поточна Олімпіада",
        "next_date_label": "Дата проведення:",
        "reg_title": "Реєстрація та подача робіт",
        "reg_form_header": "Форма учасника",
        "success_msg": "Ваша робота успішно надіслана!",
        "archive_title": "Бібліотека матеріалів (2017–2025)",
        "hist_title": "Статистика та Зала слави",
        "contact_page_title": "📞 Контакти",
        "contact_title": "Зв'язок з організаторами",
        "contact_address_val": "21100, м. Вінниця, вул. Острозького, 32<br>Корпус 3, 5-й поверх.",
        "c_person_1": "**Коношевський Олег Леонідович**",
        "c_role_1": "доцент кафедри алгебри і методики навчання математики",
        "c_phone_1": "(067) 29-010-78",
        "c_person_2": "**Панасенко Олексій Борисович**",
        "c_role_2": "доцент кафедри алгебри і методики навчання математики",
        "c_phone_2": "(067) 215-15-71, (063) 153-04-67",
        "footer_rights": "© 2025 Yasinskyi Geometry Olympiad. Всі права захищено.",
        # Admin / Login
        "admin_area_title": "Викладацька",
        "tab_login": "Вхід",
        "tab_register": "Реєстрація",
        "lbl_username": "Логін",
        "lbl_password": "Пароль",
        "lbl_confirm_pass": "Підтвердіть пароль",
        "btn_login": "Увійти",
        "btn_register": "Зареєструватися",
        "btn_logout": "Вийти з акаунту",
        "msg_login_success": "Успішний вхід!",
        "msg_login_fail": "Невірний логін або пароль.",
        "msg_reg_success": "Акаунт створено! Тепер увійдіть.",
        "msg_reg_exists": "Такий користувач вже існує.",
        "msg_pass_mismatch": "Паролі не співпадають.",
        "admin_welcome": "Вітаємо в панелі керування!",
        "admin_save": "Зберегти налаштування",
        "admin_success": "Дані оновлено!"
    },
    "en": {
        "uni_name": "Vinnytsia Mykhailo Kotsiubynskyi<br>State Pedagogical University",
        "faculty_name": "Faculty of Mathematics, Physics and Computer Science",
        "dept_name": "Department of Algebra and Methods of Teaching Mathematics",
        "nav_title": "Navigation Menu",
        "menu_items": {
            "home": "🏠 About the Olympiad",
            "current": "📝 Current Olympiad",
            "archive": "📚 Problem Archive",
            "history": "📊 History & Results",
            "contacts": "📞 Contacts",
            "method": "🎓 Methodological Cabinet",
            "admin": "⚙️ Admin Panel"
        },
        "banner_title": "Yasinskyi Geometry Olympiad",
        "tab_general": "ℹ️ General Info",
        "tab_bio": "👤 Bio of V. Yasinskyi",
        "tab_faq": "❓ FAQ",
        "about_desc": "**The Yasinskyi Geometry Olympiad** is an annual competition...",
        "rules_list": ["👥 **Participants:** Grades 8-11.", "💻 **Format:** Online.", "🧩 **Tasks:** 5 problems.", "⏳ **Duration:** 4 hours.", "⚖️ **Grading:** 0-7 points."],
        "math_beauty_title": "Geometry Aesthetics",
        "math_beauty_desc": "Geometry is the art of correct reasoning on incorrect figures. (G. Polya)",
        "bio_title": "Vyacheslav Andriyovych Yasinskyi (1957-2015)",
        "bio_text": "Outstanding Ukrainian educator, associate professor...",
        "current_title": "Current Olympiad",
        "next_date_label": "Next Event Date:",
        "reg_title": "Registration and Submission",
        "reg_form_header": "Participant Form",
        "success_msg": "Submitted successfully!",
        "archive_title": "Materials Library (2017–2025)",
        "hist_title": "Statistics and Hall of Fame",
        "contact_page_title": "📞 Contacts",
        "contact_title": "Contact Organizers",
        "contact_address_val": "21100, Vinnytsia, Ostrozkoho Str., 32<br>Building 3, 5th Floor.",
        "c_person_1": "**Konoshevskyi Oleh Leonidovych**",
        "c_role_1": "Associate Professor",
        "c_phone_1": "+38 (067) 29-010-78",
        "c_person_2": "**Panasenko Oleksii Borysovych**",
        "c_role_2": "Associate Professor",
        "c_phone_2": "+38 (067) 215-15-71, +38 (063) 153-04-67",
        "footer_rights": "© 2025 Yasinskyi Geometry Olympiad. All rights reserved.",
        # Admin / Login
        "admin_area_title": "Lecturer Area",
        "tab_login": "Login",
        "tab_register": "Register",
        "lbl_username": "Username",
        "lbl_password": "Password",
        "lbl_confirm_pass": "Confirm Password",
        "btn_login": "Log In",
        "btn_register": "Sign Up",
        "btn_logout": "Log Out",
        "msg_login_success": "Login successful!",
        "msg_login_fail": "Invalid username or password.",
        "msg_reg_success": "Account created! Please log in.",
        "msg_reg_exists": "User already exists.",
        "msg_pass_mismatch": "Passwords do not match.",
        "admin_welcome": "Welcome to Control Panel!",
        "admin_save": "Save Settings",
        "admin_success": "Settings updated!"
    }
}

# --- 5. Змінні ---
PHOTO_YASINSKYI = "yasinskyi.png" 
LOGO_FILE = "logo.png"            
TARGET_URL = "https://yasinskyi-geometry-olympiad.com/"

@st.cache_data(ttl=3600)
def get_live_pdf_links():
    try:
        r = requests.get(TARGET_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        return [{"name": unquote(a['href'].split('/')[-1]), "url": urljoin(TARGET_URL, a['href'])} 
                for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]
    except: return []

# --- 6. Сайдбар та Система Входу/Реєстрації ---
with st.sidebar:
    lang_sel = st.selectbox("Language / Мова", ["UA", "ENG"])
    lang = "ua" if lang_sel == "UA" else "en"
    t = TRANSLATIONS[lang]
    st.markdown("---")
    st.title(t["nav_title"])
    
    # Меню
    options = list(t["menu_items"].values())
    if "is_admin" not in st.session_state: st.session_state["is_admin"] = False
    
    # Приховуємо адмінку для гостей
    if not st.session_state["is_admin"]:
        admin_key = "⚙️ Адмін-панель" if lang == "ua" else "⚙️ Admin Panel"
        if admin_key in options: options.remove(admin_key)
    
    selected_item = st.radio("Go to:", options, label_visibility="collapsed")
    current_page = [k for k, v in t["menu_items"].items() if v == selected_item][0]
    
    st.markdown("---")
    
    # Блок Авторизації (Login/Register)
    if not st.session_state["is_admin"]:
        with st.expander(t["admin_area_title"], expanded=False):
            auth_tab1, auth_tab2 = st.tabs([t["tab_login"], t["tab_register"]])
            
            # ВХІД
            with auth_tab1:
                with st.form("login_form"):
                    u_login = st.text_input(t["lbl_username"], key="login_user")
                    p_login = st.text_input(t["lbl_password"], type="password", key="login_pass")
                    if st.form_submit_button(t["btn_login"]):
                        if authenticate(u_login, p_login):
                            st.session_state["is_admin"] = True
                            st.session_state["current_user"] = u_login
                            st.success(t["msg_login_success"])
                            st.rerun()
                        else:
                            st.error(t["msg_login_fail"])
            
            # РЕЄСТРАЦІЯ
            with auth_tab2:
                with st.form("reg_form"):
                    u_reg = st.text_input(t["lbl_username"], key="reg_user")
                    p_reg = st.text_input(t["lbl_password"], type="password", key="reg_pass")
                    p_reg_conf = st.text_input(t["lbl_confirm_pass"], type="password", key="reg_pass_conf")
                    
                    if st.form_submit_button(t["btn_register"]):
                        if p_reg != p_reg_conf:
                            st.error(t["msg_pass_mismatch"])
                        elif len(p_reg) < 4:
                            st.warning("Password too short.")
                        else:
                            if register_user(u_reg, p_reg):
                                st.success(t["msg_reg_success"])
                            else:
                                st.error(t["msg_reg_exists"])

    else:
        st.write(f"👤 **{st.session_state.get('current_user', 'Admin')}**")
        if st.button(t["btn_logout"]):
            st.session_state["is_admin"] = False
            st.rerun()

    st.markdown("---")
    st.caption(t["uni_name"].replace("<br>", " "))

# --- 7. Шапка ---
col_l, col_c, col_r = st.columns([1, 6, 1])
with col_l:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=90)
    else: st.write("🏛️") 
with col_c:
    st.markdown(f'<h2 class="header-university">{t["uni_name"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-faculty">{t["faculty_name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-dept">{t["dept_name"]}</div>', unsafe_allow_html=True)

# --- 8. КОНТЕНТ ---

# === ADMIN PANEL ===
if current_page == "admin" and st.session_state["is_admin"]:
    st.title(t["menu_items"]["admin"])
    st.markdown(f'<div class="admin-box"><h3>{t["admin_welcome"]}</h3>', unsafe_allow_html=True)
    
    with st.form("admin_config"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Налаштування (UA)**")
            new_date_ua = st.text_input("Дата олімпіади (UA)", site_config["next_event_date_ua"])
            new_news_ua = st.text_area("Важливе оголошення (UA)", site_config["news_ua"])
        with col2:
            st.markdown("**Settings (EN)**")
            new_date_en = st.text_input("Event Date (EN)", site_config["next_event_date_en"])
            new_news_en = st.text_area("Important Announcement (EN)", site_config["news_en"])
        reg_open = st.checkbox("Відкрити реєстрацію?", site_config["is_registration_open"])
        
        if st.form_submit_button(t["admin_save"]):
            site_config["next_event_date_ua"] = new_date_ua
            site_config["next_event_date_en"] = new_date_en
            site_config["news_ua"] = new_news_ua
            site_config["news_en"] = new_news_en
            site_config["is_registration_open"] = reg_open
            save_config(site_config)
            st.success(t["admin_success"])
    st.markdown('</div>', unsafe_allow_html=True)

# === HOME ===
elif current_page == "home":
    st.title(t["banner_title"])
    news_text = site_config["news_ua"] if lang == "ua" else site_config["news_en"]
    if news_text: st.warning(f"📢 **News:** {news_text}")

    tab_gen, tab_bio, tab_faq = st.tabs([t["tab_general"], t["tab_bio"], t["tab_faq"]])
    
    with tab_gen:
        col1, col2 = st.columns([1, 2])
        with col1:
            if os.path.exists(PHOTO_YASINSKYI): st.image(PHOTO_YASINSKYI, caption="В. А. Ясінський", use_container_width=True)
            else: st.image("https://via.placeholder.com/300x400", use_container_width=True)
        with col2:
            st.markdown(t["about_desc"])
            st.markdown(f"### {t['rules_title']}")
            st.markdown('<div class="rules-card">', unsafe_allow_html=True)
            for rule in t["rules_list"]: st.markdown(f"{rule}")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("📐 " + t["math_beauty_title"])
        st.latex(r"\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C} = 2R")

    with tab_bio:
        st.markdown(f"### {t['bio_title']}")
        c_bio_img, c_bio_txt = st.columns([1, 3])
        with c_bio_img:
            if os.path.exists(PHOTO_YASINSKYI): st.image(PHOTO_YASINSKYI, use_container_width=True)
        with c_bio_txt:
            st.markdown(f'<div class="bio-card">{t["bio_text"]}</div>', unsafe_allow_html=True)

    with tab_faq:
        st.subheader("FAQ")
        st.info("Розділ в розробці...")

# === CURRENT ===
elif current_page == "current":
    st.title(t["current_title"])
    display_date = site_config["next_event_date_ua"] if lang == "ua" else site_config["next_event_date_en"]
    col1, col2 = st.columns(2)
    with col1: st.metric(label=t["next_date_label"], value=display_date)
    with col2: 
        if site_config["is_registration_open"]: st.success("Status: **Open**")
        else: st.info("Status: **Planned**")
    
    st.markdown("---")
    st.subheader(t["reg_title"])
    if site_config["is_registration_open"]:
        with st.form("registration_form"):
            st.markdown(f"**{t['reg_form_header']}**")
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Name")
                st.selectbox("Grade", ["8", "9", "10", "11"])
            with c2:
                st.text_input("Surname")
                st.file_uploader("PDF", type=["pdf"])
            if st.form_submit_button("Submit"):
                st.success(t["success_msg"])
    else:
        st.warning("⚠️ Registration closed.")

# === ARCHIVE ===
elif current_page == "archive":
    st.title(t["archive_title"])
    if st.button("🚀 Download Archive"): pass 
    st.write("Список задач...")

# === HISTORY ===
elif current_page == "history":
    st.title(t["hist_title"])
    st.bar_chart({"2024": 58, "2025": 139})

# === CONTACTS ===
elif current_page == "contacts":
    st.title(t["contact_page_title"])
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown(f"**{t['contact_address_val']}**", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"""<div class="contact-card">{t['c_person_1']}<br><span style="color:grey;">{t['c_role_1']}</span><br>📞 <b>{t['c_phone_1']}</b></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="contact-card">{t['c_person_2']}<br><span style="color:grey;">{t['c_role_2']}</span><br>📞 <b>{t['c_phone_2']}</b></div>""", unsafe_allow_html=True)

# === METHODOLOGICAL ===
elif current_page == "method":
    st.title(t["menu_items"]["method"])
    st.info("Розділ для студентів кафедри.")

# --- Footer ---
st.markdown("---")
st.markdown(f"<div style='text-align:center; color:grey; padding: 20px;'><p>{t['footer_rights']}</p></div>", unsafe_allow_html=True)
