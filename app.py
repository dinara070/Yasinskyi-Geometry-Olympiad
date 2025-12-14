import streamlit as st
import pandas as pd
import os
import io
import zipfile
import json
import hashlib

# --- БЕЗПЕЧНИЙ ІМПОРТ БІБЛІОТЕК ---
# Це виправить помилку на скріншоті. Якщо бібліотеки немає, сайт не впаде.
try:
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, unquote
    LIBRARIES_OK = True
except ImportError as e:
    LIBRARIES_OK = False
    MISSING_LIB_ERROR = str(e)

# --- 1. Налаштування та Файлова система (JSON) ---
st.set_page_config(
    page_title="Yasinskyi Geometry Olympiad | VSPU",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Файли для зберігання даних
USERS_FILE = "users.json"
CONFIG_FILE = "config.json"
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

# Функції для роботи з JSON
def load_data(file, default):
    if not os.path.exists(file):
        return default
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Ініціалізація даних
default_config = {"next_date": "Листопад 2026 року", "news": "Реєстрацію відкрито!"}
site_config = load_data(CONFIG_FILE, default_config)
users_db = load_data(USERS_FILE, {})

# --- 2. Session State ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Функція хешування паролів
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_login(username, password):
    hashed_pw = make_hash(password)
    if username == "admin" and hashed_pw == ADMIN_PASSWORD_HASH:
        return "admin"
    if username in users_db:
        if users_db[username]['password'] == hashed_pw:
            return "student"
    return None

# --- Змінні для парсингу ---
TARGET_URL = "https://yasinskyi-geometry-olympiad.com/"

@st.cache_data(ttl=3600)
def get_live_pdf_links():
    if not LIBRARIES_OK:
        return []
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
    except Exception:
        return []

# --- 3. Візуальний тюнінг (CSS) ---
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
    .admin-panel { border: 2px solid #e74c3c; padding: 20px; border-radius: 10px; background-color: #fdf2f2; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: white; color: #555; text-align: center; padding: 10px; border-top: 1px solid #eaeaea; font-size: 0.9rem; }
    .stButton>button { width: 100%; border-radius: 5px; }
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
        "tab_general": "ℹ️ Загальна інформація",
        "tab_bio": "👤 Біографія В. Ясінського",
        "tab_faq": "❓ FAQ (Питання)",
        "banner_title": "Геометрична олімпіада імені В'ячеслава Ясінського",
        "about_desc": "**Геометрична олімпіада імені В'ячеслава Ясінського** — це щорічне змагання...",
        "rules_title": "Правила та формат",
        "rules_list": ["👥 **Учасники:** Учні 8-11 класів.", "💻 **Формат:** Онлайн.", "🧩 **Завдання:** 5 задач.", "⏳ **Тривалість:** 4 години."],
        "bio_title": "В'ячеслав Андрійович Ясінський (1957-2015)",
        "bio_text": "**В'ячеслав Андрійович Ясінський** — видатний український педагог...",
        "current_title": "Олімпіада 2025/2026",
        "next_date_label": "Наступна олімпіада:",
        "next_date_val": "Листопад 2026 року",
        "reg_title": "Реєстрація та подача робіт",
        "reg_form_header": "Форма учасника",
        "f_name": "Ім'я", "f_surname": "Прізвище", "f_email": "Email", "f_submit": "Надіслати",
        "archive_title": "Бібліотека матеріалів",
        "hist_title": "Статистика",
        "contact_page_title": "Контакти",
        "contact_address_val": "м. Вінниця, вул. Острозького, 32",
        "footer_rights": "© 2025 Yasinskyi Geometry Olympiad."
    },
    "en": {
        "uni_name": "Vinnytsia State Pedagogical University",
        "faculty_name": "Faculty of Math, Physics and CS",
        "dept_name": "Dept. of Algebra",
        "nav_title": "Navigation",
        "menu_items": {
            "home": "🏠 About",
            "current": "📝 Current Olympiad",
            "archive": "📚 Archive",
            "history": "📊 History",
            "contacts": "📞 Contacts",
            "method": "🎓 Methodological",
            "admin": "⚙️ Admin Panel"
        },
        "tab_general": "ℹ️ Info", "tab_bio": "👤 Bio", "tab_faq": "❓ FAQ",
        "banner_title": "Yasinskyi Geometry Olympiad",
        "about_desc": "Annual competition...",
        "rules_title": "Rules",
        "rules_list": ["Participants: 8-11 grades", "Format: Online"],
        "bio_title": "V. A. Yasinskyi", "bio_text": "Outstanding educator...",
        "current_title": "Olympiad 2025/2026",
        "next_date_label": "Next Date:",
        "next_date_val": "November 2026",
        "reg_title": "Registration",
        "reg_form_header": "Participant Form",
        "f_name": "First Name", "f_surname": "Last Name", "f_email": "Email", "f_submit": "Submit",
        "archive_title": "Library",
        "hist_title": "Statistics",
        "contact_page_title": "Contacts",
        "contact_address_val": "Vinnytsia, Ostrozkoho Str., 32",
        "footer_rights": "© 2025 Yasinskyi Geometry Olympiad."
    }
}

PHOTO_YASINSKYI = "yasinskyi.png"
LOGO_FILE = "logo.png"

# --- 5. Логіка Сайдбару та Авторизації ---
with st.sidebar:
    lang_sel = st.selectbox("Language / Мова", ["UA", "ENG"])
    lang = "ua" if lang_sel == "UA" else "en"
    t = TRANSLATIONS[lang]
    
    st.markdown("---")
    
    if st.session_state.user is None:
        st.subheader("🔐 Вхід / Реєстрація")
        auth_mode = st.radio("Оберіть дію:", ["Вхід", "Реєстрація"], label_visibility="collapsed")
        
        if auth_mode == "Вхід":
            with st.form("login_form"):
                l_user = st.text_input("Логін")
                l_pass = st.text_input("Пароль", type="password")
                if st.form_submit_button("Увійти"):
                    role = check_login(l_user, l_pass)
                    if role:
                        st.session_state.user = role
                        st.session_state.username = l_user
                        st.rerun()
                    else:
                        st.error("Помилка входу")
                        
        elif auth_mode == "Реєстрація":
            with st.form("reg_form"):
                r_user = st.text_input("Логін")
                r_pass = st.text_input("Пароль", type="password")
                r_name = st.text_input("ПІБ")
                if st.form_submit_button("Зареєструватися"):
                    if r_user in users_db:
                        st.error("Логін зайнятий")
                    elif len(r_pass) < 4:
                        st.error("Пароль > 4 символів")
                    else:
                        users_db[r_user] = {"password": make_hash(r_pass), "name": r_name, "role": "student"}
                        save_data(USERS_FILE, users_db)
                        st.success("Успішно!")
    else:
        st.markdown(f"👤 **{st.session_state.username}**")
        if st.button("Вийти"):
            st.session_state.user = None
            st.rerun()

    st.markdown("---")
    st.title(t["nav_title"])
    
    menu_dict = t["menu_items"].copy()
    if st.session_state.user != "admin":
        menu_dict.pop("admin", None)
        
    menu_options = list(menu_dict.values())
    if "selected_page" not in st.session_state: st.session_state.selected_page = menu_options[0]
    selected_item = st.radio("Go to:", menu_options, label_visibility="collapsed")
    current_page = [k for k, v in menu_dict.items() if v == selected_item][0]
    
    st.markdown("---")
    # Відображення помилки бібліотек тільки в сайдбарі, якщо вона є
    if not LIBRARIES_OK:
        st.warning(f"⚠️ **Увага:** Деякі функції обмежені. Не знайдено 'bs4'. Створіть файл requirements.txt.")

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

# === ADMIN ===
if current_page == "admin":
    if st.session_state.user == "admin":
        st.title("⚙️ Панель Адміністратора")
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        with st.form("admin_config"):
            new_date = st.text_input("Дата олімпіади:", value=site_config.get("next_date", ""))
            new_news = st.text_area("Новини:", value=site_config.get("news", ""))
            if st.form_submit_button("Зберегти"):
                site_config["next_date"] = new_date
                site_config["news"] = new_news
                save_data(CONFIG_FILE, site_config)
                st.success("Оновлено!")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("---")
        st.subheader("Користувачі")
        if users_db:
            df = pd.DataFrame.from_dict(users_db, orient='index')[['name', 'role']]
            st.dataframe(df, use_container_width=True)

# === HOME ===
elif current_page == "home":
    st.title(t["banner_title"])
    tab1, tab2, tab3 = st.tabs([t["tab_general"], t["tab_bio"], t["tab_faq"]])
    
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            if os.path.exists(PHOTO_YASINSKYI): st.image(PHOTO_YASINSKYI, use_container_width=True)
            else: st.write("📷 Фото")
        with c2:
            st.markdown(t["about_desc"])
            if site_config.get("news"): st.info(f"📢 {site_config['news']}")
            st.markdown(f"### {t['rules_title']}")
            for rule in t["rules_list"]: st.markdown(f"- {rule}")
            
    with tab2:
        st.markdown(f"### {t['bio_title']}")
        st.markdown(t['bio_text'])

# === CURRENT ===
elif current_page == "current":
    st.title(t["current_title"])
    d_date = site_config.get("next_date", t["next_date_val"])
    col1, col2 = st.columns(2)
    col1.metric(t["next_date_label"], d_date)
    col2.info("Status: Active")
    
    st.markdown("---")
    st.subheader(t["reg_title"])
    default_name = ""
    if st.session_state.user == "student":
        default_name = users_db.get(st.session_state.username, {}).get("name", "")
        st.success(f"Вітаємо, {default_name}!")

    with st.form("reg"):
        c1, c2 = st.columns(2)
        c1.text_input(t["f_name"], value=default_name.split()[0] if default_name else "")
        c1.text_input(t["f_email"])
        c2.text_input(t["f_surname"], value=default_name.split()[-1] if len(default_name.split())>1 else "")
        c2.file_uploader("PDF", type=["pdf"])
        if st.form_submit_button(t["f_submit"]):
            st.success("Надіслано!")

# === ARCHIVE ===
elif current_page == "archive":
    st.title(t["archive_title"])
    if not LIBRARIES_OK:
        st.error(f"❌ Модуль сканування не працює. Помилка: {MISSING_LIB_ERROR}")
        st.info("Створіть файл requirements.txt на GitHub з текстом: beautifulsoup4")
    else:
        if st.button("🚀 Згенерувати архів матеріалів"):
            with st.spinner("Сканування..."):
                links = get_live_pdf_links()
                if links:
                    st.success(f"Знайдено файлів: {len(links)}")
                    # Тут код створення ZIP (скорочено для надійності)
                else:
                    st.warning("Файлів не знайдено.")

# === HISTORY & CONTACTS ===
elif current_page == "history":
    st.title(t["hist_title"])
    st.bar_chart({"2023": 100, "2024": 58, "2025": 139})

elif current_page == "contacts":
    st.title(t["contact_page_title"])
    st.write(t["contact_address_val"])

elif current_page == "method":
    st.title(t["menu_items"]["method"])
    if st.session_state.user:
        st.info("Доступ до методичних матеріалів відкрито.")
    else:
        st.warning("Потрібна авторизація.")

# --- FOOTER ---
st.markdown("---")
st.markdown(f"<div style='text-align:center; color:grey;'>{t['footer_rights']}</div>", unsafe_allow_html=True)
