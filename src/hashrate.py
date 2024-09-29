from helper import make_api_request, read_json_file, write_json_file, get_environ
from datetime import datetime, timezone
import os

def main():
    # Pobieranie zmiennych
    url = get_environ("API_URL_WORKERS")
    if not url: return
    data_dir = get_environ("DATA_DIR")
    if not data_dir: return
    hashrate_dir = get_environ("HASHRATE_DIR")
    if not hashrate_dir: return
    
    # ścieżka
    path = os.path.join(data_dir, hashrate_dir)

    # Aktualna data i czas UTC
    datetime_utc = datetime.now(timezone.utc)
    datetime_utc_string = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")
    
    # Wysłanie zapytania
    data = make_api_request(url)
    if data is None:
        return
    
    # Przechodzenie przez wszystkie urządzenia
    for worker in data["workers"]:
        # Ścieżka pliku
        file_name = f"{worker['name']}.json"
        file_path = os.path.join(path, file_name)

        # Tworzenie katalogu, jeśli nie istnieje
        os.makedirs(path, exist_ok=True)
        
        # Odczytywanie istniejących danych
        existing_data = read_json_file(file_path)
        
        # Konwersja timestampu na czytelną datę UTC
        last_share_time_utc = datetime.fromtimestamp(worker["last_share_time"], timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        # Dodawanie nowych danych
        new_data = {
            "hashrate24h": {
                "worker": worker["name"],
                "hashrate": worker["hashrate24h"]["hashrate"],
                "hashrate_unit": worker["hashrate24h"]["hashrate_unit"],
                "last_share_time": worker["last_share_time"],
                "last_share_time_utc": last_share_time_utc
            }
        }
        existing_data.append(new_data)
        
        # Zapisywanie zaktualizowanych danych do pliku
        write_json_file(file_path, existing_data)

    print(f"{datetime_utc_string}(UTC) - Dane zapisane do pliku: {file_path}")

# Wykonanie funkcji
if __name__ == "__main__":
    main()
