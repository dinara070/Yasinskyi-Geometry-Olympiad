import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import io
import zipfile
import pandas as pd
import os # Додано для перевірки наявності файлу фото

# --- 1. Налаштування сторінки ---
st.set_page_config(
    page_title="Геометрична олімпіада ім. В. Ясінського",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS Стилізація ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3 { font-family: 'Helvetica', sans-serif; color: #2c3e50; }
    .info-card { padding: 20px; border-radius: 10px; background-color: #f8f9fa; border: 1px solid #e9ecef; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    /* Стиль для підпису під фото */
    .caption-text { text-align: center; font-style: italic; color: #666; margin-top: -10px;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. Константи та змінні ---
IMAGE_FILE = "yasinskyi.png" # Ім'я файлу з вашим фото

# --- 4. Функції ---
def fetch_pdf_links(target_url):
    """Парсинг PDF посилань з сайту"""
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

# --- 5. Навігація (Sidebar) ---
with st.sidebar:
    # ВИКОРИСТАННЯ ФОТО ЯК ЛОГОТИПУ
    if os.path.exists(IMAGE_FILE):
        # Відображаємо локальний файл
        st.image(IMAGE_FILE, width=120)
    else:
        # Якщо файлу немає, показуємо заглушку або текст
        st.warning(f"Файл {IMAGE_FILE} не знайдено.")
        st.image("https://via.placeholder.com/120x150.png?text=Foto", width=120)

    st.title("Меню")
    
    page = st.radio(
        "Перейти до:",
        ["Про олімпіаду", "Олімпіада 2025", "Задачі (Архів)", "Історія", "Контакти"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("Developed with Python & Streamlit")

# --- 6. Логіка сторінок ---

# === СТОРІНКА: ПРО ОЛІМПІАДУ ===
if page == "Про олімпіаду":
    col1, col2 = st.columns([1, 2])
    with col1:
         # ВИКОРИСТАННЯ ФОТО НА ГОЛОВНІЙ СТОРІНЦІ
        if os.path.exists(IMAGE_FILE):
            st.image(IMAGE_FILE, use_container_width=True)
            st.markdown('<p class="caption-text">В\'ячеслав Ясінський</p>', unsafe_allow_html=True)
        else:
             st.info(f"Будь ласка, завантажте файл **{IMAGE_FILE}** у папку проекту, щоб побачити фото.")
             st.image("https://via.placeholder.com/300x400.png?text=Place+yasinskyi.png+here", use_container_width=True)

    with col2:
        st.title("Геометрична олімпіада імені В'ячеслава Ясінського")
        st.markdown("""
        **Геометрична олімпіада імені В'ячеслава Ясінського** — це щорічне змагання, яке об'єднує поціновувачів геометричних задач. 
        Вперше вона була проведена у **2017 році**.
        
        Олімпіада названа на честь **В'ячеслава Андрійовича Ясінського** — відомого українського вчителя математики, доцента, заслуженого вчителя України, майстра створення красивих олімпіадних задач.
        """)

    st.markdown("---")
    
    st.subheader("Деталі олімпіади")
    st.info("""
    Олімпіада надає чудову можливість перевірити свої навички розв'язування олімпіадних геометричних задач. 
    Складність запропонованих задач відповідає рівню національних олімпіад.
    """)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🎯 **Для кого**")
        st.write("Учні 8, 9 та 10-11 класів")
    with c2:
        st.markdown("### 💻 **Формат**")
        st.write("Онлайн (дистанційно)")
    with c3:
        st.markdown("### ⏳ **Тривалість**")
        st.write("4 години")

# === СТОРІНКА: ОЛІМПІАДА 2025 ===
elif page == "Олімпіада 2025":
    st.title("IX Геометрична олімпіада (2025/2026)")
    st.warning("⚠️ **Зверніть увагу:** Наступна олімпіада відбудеться у **листопаді 2026 року**.")
    st.markdown("### Правила участі")
    st.markdown("""
    <div class="info-card">
    <ul>
        <li>Пропонується для розв'язання <b>5 геометричних задач</b>.</li>
        <li>Кожна задача оцінюється від <b>0 до 7 балів</b>.</li>
        <li>Завдання розраховані на учнів останніх чотирьох класів загальноосвітньої школи.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("Реєстрація")
    st.write("Попередня реєстрація **не потрібна**. Форма відкриється в день олімпіади.")

# === СТОРІНКА: ЗАДАЧІ (АРХІВ) ===
elif page == "Задачі (Архів)":
    st.title("📚 Архів задач")
    st.write("Запрошуємо переглянути задачі та розв'язки минулих олімпіад.")
    target_url = "https://yasinskyi-geometry-olympiad.com/"
    
    st.markdown("### Доступні матеріали на сайті")
    years = range(2025, 2016, -1)
    col1, col2 = st.columns(2)
    with col1:
        for year in years: st.write(f"🔹 {year} рік")
    with col2:
        for year in years: st.caption("Умови + Розв'язки")

    st.markdown("---")
    st.subheader("📥 Автоматичне завантаження")
    if st.button("🚀 Знайти та завантажити всі PDF (ZIP)"):
        status_container = st.container()
        progress_bar = st.progress(0)
        with status_container:
            st.info("Сканування сайту...")
            pdf_links = fetch_pdf_links(target_url)
            if pdf_links:
                st.success(f"Знайдено {len(pdf_links)} файлів. Завантаження...")
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for i, file_url in enumerate(pdf_links):
                        file_name = unquote(file_url.split('/')[-1])
                        try:
                            r = requests.get(file_url, headers={"User-Agent": "Mozilla/5.0"})
                            zf.writestr(file_name, r.content)
                        except: pass
                        progress_bar.progress((i + 1) / len(pdf_links))
                zip_buffer.seek(0)
                st.download_button(label="💾 Зберегти ZIP-архів", data=zip_buffer, file_name="yasinskyi_olympiad_archive.zip", mime="application/zip", type="primary")
            else:
                st.error("Не вдалося знайти файли.")

# === СТОРІНКА: ІСТОРІЯ ===
elif page == "Історія":
    st.title("📊 Статистика та результати")
    data = {
        'Рік': ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'],
        'Учасники': [58, 76, 129, 136, 169, 145, 100, 58, 139],
        'Країни': [1, 1, 1, 1, 1, 2, 3, 6, 7]
    }
    df = pd.DataFrame(data)
    st.subheader("Динаміка кількості учасників")
    st.bar_chart(df.set_index('Рік')['Учасники'], color="#3498db")
    st.subheader("Географія")
    st.line_chart(df.set_index('Рік')['Країни'], color="#e74c3c")

# === СТОРІНКА: КОНТАКТИ ===
elif page == "Контакти":
    st.title("📬 Контакти")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Ми завжди шукаємо оригінальні та цікаві геометричні задачі.")
        st.info("📧 **Email:** yasinskyi.geometry.olympiad@gmail.com")
    with col2:
        st.text_input("Ваше ім'я")
        st.text_area("Повідомлення")
        st.button("Надіслати (Демо)")
