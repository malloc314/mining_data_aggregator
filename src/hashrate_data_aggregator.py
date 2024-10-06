from helper import make_api_request, read_json_file, write_json_file, get_environ, get_datetime_utc
import os

def main():
    # Pobieranie zmiennych
    url = get_environ("API_URL_WORKERS")
    if not url: return
    data_dir = get_environ("DATA_DIR")
    if not data_dir: return
    hashrate_dir = get_environ("HASHRATE_DIR")
    if not hashrate_dir: return

    # Wysłanie zapytania
    data = make_api_request(url)
    if data is None: return

    # Aktualna data i czas UTC
    datetime_utc, date_utc_string, datetime_utc_string = get_datetime_utc()
    
    # ścieżka
    path = os.path.join(data_dir, hashrate_dir)

    # Ścieżka pliku
    file_name = f"{date_utc_string}.json"
    file_path = os.path.join(path, file_name)
    
    # Tworzenie katalogu, jeśli nie istnieje
    os.makedirs(path, exist_ok=True)

    # Odczytywanie istniejących danych
    existing_data = read_json_file(file_path)

    # Dodawanie nowych danych
    existing_data.append(data)

    # Zapisywanie zaktualizowanych danych do pliku
    write_json_file(file_path, existing_data)

    print(f"{datetime_utc_string}(UTC) - Dane zapisane do pliku: {file_path}")

# Wykonanie funkcji
if __name__ == "__main__":
    main()
