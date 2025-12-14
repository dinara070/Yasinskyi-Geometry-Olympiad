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
    page_title="Портал Кафедри алгебри і методики навчання математики",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS та Брендування ВДПУ ---
st.markdown("""
    <style>
    /* Стилі для заголовків та кольорів університету (бордовий/червоний відтінок) */
    .header-university {
        color: #800000;
        font-family: 'Times New Roman', serif;
        text-align: center;
        margin-bottom: 0px;
    }
    .header-faculty {
        color: #2c3e50;
        font-family: sans-serif;
        text-align: center;
        font-size: 1.2rem;
        margin-top: 0px;
        font-weight: bold;
    }
    .header-dept {
        color: #555;
        text-align: center;
        font-style: italic;
        margin-bottom: 20px;
        border-bottom: 2px solid #800000;
        padding-bottom: 10px;
    }
    .info-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        border-left: 5px solid #800000;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #800000;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #a00000;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Змінні ---
PHOTO_YASINSKYI = "yasinskyi.png"
LOGO_FILE = "logo.png"  # Потрібно додати файл логотипу ВДПУ

# --- 4. Функції ---
def fetch_pdf_links(target_url):
    """Парсинг PDF посилань"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        pdf_links = []
        for link in links:
            href = link['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(target_url, href)
                pdf_links.append(full_url)
        return pdf_links
    except Exception as e:
        st.error(f"Помилка з'єднання: {e}")
        return []

# --- 5. Шапка (Header) ---
col_l, col_c, col_r = st.columns([1, 6, 1])
with col_l:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, width=100)
    else:
        st.write("🏛️") # Заглушка, якщо немає лого

with col_c:
    st.markdown('<h2 class="header-university">Вінницький державний педагогічний університет<br>імені Михайла Коцюбинського</h2>', unsafe_allow_html=True)
    st.markdown('<div class="header-faculty">Факультет математики, фізики і комп\'ютерних наук</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-dept">Кафедра алгебри і методики навчання математики</div>', unsafe_allow_html=True)

# --- 6. Навігація ---
with st.sidebar:
    st.title("Навігація")
    menu = st.radio(
        "Оберіть розділ:",
        ["🏠 Головна кафедри", "📐 Олімпіада ім. В. Ясінського", "📝 Методичний кабінет", "📞 Контакти"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.info("Розроблено для підтримки навчального процесу та олімпіадного руху.")

# --- 7. Логіка розділів ---

# === ГОЛОВНА СТОРІНКА КАФЕДРИ ===
if menu == "🏠 Головна кафедри":
    st.subheader("Вітаємо на цифровому порталі кафедри!")
    
    st.markdown("""
    <div class="info-card">
    Цей ресурс створено для студентів, викладачів та вчителів математики. Тут ви знайдете:
    <ul>
        <li>Матеріали для підготовки до олімпіад.</li>
        <li>Інструменти для створення методичних карток.</li>
        <li>Архіви задач та наукових робіт.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📢 Останні новини")
        st.info(f"📅 **{datetime.now().strftime('%d.%m.%Y')}**: Оновлено базу олімпіадних задач.")
        st.write("🔹 Розпочато підготовку до наукової конференції.")
        st.write("🔹 Засідання методичного семінару відбудеться у середу.")
        
    with col2:
        st.markdown("### 🔬 Наукова робота")
        st.write("Пріоритетні напрямки досліджень кафедри:")
        st.progress(85, text="Методика навчання алгебри")
        st.progress(70, text="Комп'ютерно-орієнтовані системи")
        st.progress(60, text="Олімпіадна математика")

# === ОЛІМПІАДА ЯСІНСЬКОГО (Ваш попередній код) ===
elif menu == "📐 Олімпіада ім. В. Ясінського":
    st.markdown("### 🏆 Геометрична олімпіада імені В'ячеслава Ясінського")
    
    tab1, tab2, tab3 = st.tabs(["ℹ️ Про олімпіаду", "📚 Архів задач", "📊 Статистика"])
    
    with tab1:
        c1, c2 = st.columns([1, 3])
        with c1:
            if os.path.exists(PHOTO_YASINSKYI):
                st.image(PHOTO_YASINSKYI, use_container_width=True)
                st.caption("В'ячеслав Андрійович Ясінський")
            else:
                st.warning("Фото відсутнє")
        with c2:
            st.write("""
            **В'ячеслав Андрійович Ясінський** — видатний педагог, доцент нашої кафедри, який зробив неоціненний внесок у розвиток олімпіадного руху.
            Ця олімпіада є даниною пам'яті Маестро геометрії.
            """)
            st.info("Наступна олімпіада: **Листопад 2026 року**")

    with tab2:
        st.write("Автоматизований модуль для завантаження методичних матеріалів олімпіади.")
        if st.button("🚀 Завантажити повний архів задач (PDF)"):
            with st.spinner("З'єднання з сервером олімпіади..."):
                pdf_links = fetch_pdf_links("https://yasinskyi-geometry-olympiad.com/")
                if pdf_links:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zf:
                        for i, url in enumerate(pdf_links):
                            try:
                                r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                                fname = unquote(url.split('/')[-1])
                                zf.writestr(fname, r.content)
                            except: pass
                    zip_buffer.seek(0)
                    st.success("Архівація завершена!")
                    st.download_button("💾 Зберегти ZIP", zip_buffer, "yasinskyi_full_archive.zip", "application/zip")
                else:
                    st.error("Помилка доступу до джерела.")

    with tab3:
        # Статистика
        data = {'Рік': ['2021', '2022', '2023', '2024', '2025'], 'Учасники': [169, 145, 100, 58, 139]}
        st.bar_chart(pd.DataFrame(data).set_index('Рік'))

# === МЕТОДИЧНИЙ КАБІНЕТ (Новий функціонал для кафедри) ===
elif menu == "📝 Методичний кабінет":
    st.markdown("### 🛠️ Генератор методичної картки уроку")
    st.write("Інструмент для студентів-практикантів та вчителів.")
    
    with st.form("lesson_plan"):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("Тема уроку", "Квадратні рівняння")
            grade = st.selectbox("Клас", ["7 клас", "8 клас", "9 клас", "10 клас", "11 клас"])
        with col2:
            goal = st.text_area("Мета уроку", "Сформувати навички розв'язування...")
            type_lesson = st.selectbox("Тип уроку", ["Засвоєння нових знань", "Узагальнення і систематизація", "Комбінований"])
        
        submitted = st.form_submit_button("🖨️ Згенерувати картку")
    
    if submitted:
        st.success("Картка успішно згенерована!")
        st.markdown(f"""
        <div style="border: 1px solid #ccc; padding: 20px; background-color: white;">
            <h3 style="text-align: center;">ПЛАН-КОНСПЕКТ УРОКУ АЛГЕБРИ</h3>
            <p><strong>Клас:</strong> {grade}</p>
            <p><strong>Тема:</strong> {topic}</p>
            <p><strong>Тип уроку:</strong> {type_lesson}</p>
            <p><strong>Мета:</strong> {goal}</p>
            <hr>
            <p><em>Згенеровано системою методичного супроводу ФМФКН ВДПУ</em></p>
        </div>
        """, unsafe_allow_html=True)

# === КОНТАКТИ ===
elif menu == "📞 Контакти":
    st.markdown("### 📍 Наша адреса")
    st.write("21100, м. Вінниця, вул. Острозького, 32")
    st.write("**Факультет математики, фізики і комп'ютерних наук**")
    st.write("Корпус 3, поверх 2.")
    
    st.markdown("### 📧 Зв'язок")
    st.write("Email кафедри: `math.vspu@gmail.com` (приклад)")
    st.write("Телефон деканату: `(0432) XX-XX-XX`")
    
    st.map(pd.DataFrame({'lat': [49.2325], 'lon': [28.4833]})) # Координати ВДПУ (приблизні)

# --- Підвал ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>© 2025 ВДПУ ім. М. Коцюбинського | Кафедра алгебри і методики навчання математики</div>", unsafe_allow_html=True)
