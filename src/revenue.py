from helper import make_api_request, read_json_file, write_json_file, get_environ
from datetime import datetime, timezone
import os

def main():
    # Pobieranie zmiennych
    url = get_environ("API_URL_BASE")
    if not url: return
    data_dir = get_environ("DATA_DIR")
    if not data_dir: return
    revenue_dir = get_environ("REVENUE_DIR")
    if not revenue_dir: return
    
    # Aktualna data i czas UTC
    datetime_utc = datetime.now(timezone.utc)
    date_utc_string = datetime_utc.strftime("%Y-%m-%d")
    datetime_utc_string = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")

    # Ścieżka pliku
    file_name = f"{date_utc_string}.json"
    path = os.path.join(data_dir, revenue_dir)
    file_path = os.path.join(path, file_name)

    # Wysłanie zapytania
    data = make_api_request(url)
    if data is None:
        return
    
    # Nagroda za 1h
    try:
        revenue60m = data["revenue"]["revenue60m"]
    except KeyError:
        print(f"{datetime_utc_string}(UTC) - Nie można znaleźć revenue60m w danych API.")
        return

    # Odczytywanie istniejących danych
    existing_data = read_json_file(file_path)

    # Dodawanie nowych danych
    new_data = {
        "revenue60m": revenue60m,
        "datetime_utc": datetime_utc_string
    }
    existing_data.append(new_data)

    # Tworzenie katalogu, jeśli nie istnieje
    os.makedirs(path, exist_ok=True)

    # Zapisywanie zaktualizowanych danych do pliku
    write_json_file(file_path, existing_data)

    print(f"{datetime_utc_string}(UTC) - Dane zapisane do pliku: {file_path}")

# Wykonanie funkcji
if __name__ == "__main__":
    main()
