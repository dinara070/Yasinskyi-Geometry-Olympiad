import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

def download_pdf_files(url, output_folder="yasinskyi_tasks"):
    """
    Завантажує всі PDF-файли з вказаної сторінки.
    """
    # Створюємо папку для збереження, якщо вона не існує
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"[INFO] Створено папку: {output_folder}")

    # Заголовки, щоб сайт не блокував запит (імітуємо браузер)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        print(f"[INFO] Підключення до {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Перевірка на помилки (наприклад, 404)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Знаходимо всі посилання (теги <a>)
        links = soup.find_all('a', href=True)
        
        pdf_links = []
        for link in links:
            href = link['href']
            # Перевіряємо, чи посилання веде на PDF (ігноруємо регістр)
            if href.lower().endswith('.pdf'):
                full_url = urljoin(url, href) # Робимо посилання абсолютним
                pdf_links.append(full_url)

        if not pdf_links:
            print("[WARN] PDF-файлів на сторінці не знайдено.")
            return

        print(f"[INFO] Знайдено {len(pdf_links)} PDF-файлів. Починаємо завантаження...")

        for i, file_url in enumerate(pdf_links, 1):
            try:
                # Отримуємо ім'я файлу з URL
                file_name = unquote(file_url.split('/')[-1])
                file_path = os.path.join(output_folder, file_name)

                print(f"[{i}/{len(pdf_links)}] Завантаження: {file_name}")
                
                # Завантажуємо сам файл
                file_response = requests.get(file_url, headers=headers)
                file_response.raise_for_status()

                with open(file_path, 'wb') as f:
                    f.write(file_response.content)
                
            except Exception as e:
                print(f"[ERROR] Не вдалося завантажити {file_url}: {e}")

        print("\n[SUCCESS] Робота завершена! Перевірте папку:", output_folder)

    except requests.exceptions.RequestException as e:
        print(f"[CRITICAL] Помилка при доступі до сайту: {e}")

if __name__ == "__main__":
    TARGET_URL = "https://yasinskyi-geometry-olympiad.com/"
    download_pdf_files(TARGET_URL)
