from library import make_api_request, read_json_file, write_json_file
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

# Wczytywanie zmiennych środowiskowych z pliku .env
load_dotenv()

def main():
    url = os.environ.get('API_URL_BASE')
    if not url:
        print("Wartość nie został określona w pliku .env (zmienna 'API_URL_BASE').")
        return

    revenue_dir = os.environ.get('REVENUE_DIR')
    if not revenue_dir:
        print("Wartość nie został określona w pliku .env (zmienna 'REVENUE_DIR').")
        return

    # Aktualna data i czas UTC
    datetime_utc = datetime.now(timezone.utc)
    date_utc_string = datetime_utc.strftime('%Y-%m-%d')
    datetime_utc_string = datetime_utc.strftime('%Y-%m-%d %H:%M:%S')

    # Ścieżka pliku
    file_name = f"{date_utc_string}.json"
    directory_path = os.path.join(revenue_dir)
    file_path = os.path.join(directory_path, file_name)
    
    # Tworzenie katalogu, jeśli nie istnieje
    os.makedirs(directory_path, exist_ok=True)

    data = make_api_request(url)
    if data is None:
        return
    
    # Nagroda za 1h
    try:
        revenue60m = data['revenue']['revenue60m']
    except KeyError:
        print("Nie można znaleźć 'revenue60m' w danych API.")
        return

    # Odczytywanie istniejących danych
    existing_data = read_json_file(file_path)

    # Dodawanie nowych danych
    new_data = {
        "revenue60m": revenue60m,
        "datetime_utc": datetime_utc_string
    }
    existing_data.append(new_data)

    # Zapisywanie zaktualizowanych danych do pliku
    write_json_file(file_path, existing_data)

    print(f"{datetime_utc_string} - Dane zapisane do pliku: {file_path}")

# Wykonanie funkcji
if __name__ == "__main__":
    main()
