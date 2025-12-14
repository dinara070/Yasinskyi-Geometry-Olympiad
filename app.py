import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import io
import zipfile

# Налаштування сторінки
st.set_page_config(page_title="Yasinskyi Olympiad Downloader", page_icon="📐")

st.title("📐 Завантажувач матеріалів олімпіади")
st.write("Цей додаток сканує сайт олімпіади ім. В. Ясінського та збирає всі умови і розв'язки в один архів.")

TARGET_URL = "https://yasinskyi-geometry-olympiad.com/"

# Кнопка запуску
if st.button("🔍 Знайти та підготувати файли"):
    status_text = st.empty() # Місце для тексту про статус
    progress_bar = st.progress(0)
    
    try:
        status_text.info(f"Підключення до {TARGET_URL}...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(TARGET_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        # Шукаємо PDF
        pdf_links = []
        for link in links:
            href = link['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(TARGET_URL, href)
                pdf_links.append(full_url)
        
        if not pdf_links:
            status_text.warning("PDF-файлів не знайдено.")
        else:
            status_text.success(f"Знайдено {len(pdf_links)} файлів. Завантажую в пам'ять...")
            
            # Створюємо ZIP-архів у пам'яті (RAM)
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i, file_url in enumerate(pdf_links):
                    file_name = unquote(file_url.split('/')[-1])
                    
                    # Завантажуємо файл
                    try:
                        file_response = requests.get(file_url, headers=headers)
                        file_response.raise_for_status()
                        # Записуємо файл в архів
                        zf.writestr(file_name, file_response.content)
                    except Exception as e:
                        st.error(f"Помилка з файлом {file_name}: {e}")
                    
                    # Оновлюємо прогрес бар
                    progress = (i + 1) / len(pdf_links)
                    progress_bar.progress(progress)

            # Завершуємо роботу з архівом
            zip_buffer.seek(0)
            
            status_text.success("✅ Готово! Натисніть кнопку нижче, щоб зберегти архів.")
            
            # Кнопка для скачування готового архіву
            st.download_button(
                label="📥 Завантажити ZIP-архів із завданнями",
                data=zip_buffer,
                file_name="yasinskyi_tasks.zip",
                mime="application/zip"
            )

    except Exception as e:
        status_text.error(f"Виникла помилка: {e}")
