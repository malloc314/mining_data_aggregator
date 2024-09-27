from library import make_api_request, read_json_file, write_json_file
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

# Wczytywanie zmiennych środowiskowych z pliku .env
load_dotenv()

def main():
    url = os.environ.get('API_URL_WORKERS')
    if not url:
        print("Wartość nie został określona w pliku .env (zmienna 'API_URL_WORKERS').")
        return

    hashrate_dir = os.environ.get('HASHRATE_DIR')
    if not hashrate_dir:
        print("Wartość nie został określona w pliku .env (zmienna 'HASHRATE_DIR').")
        return
    
    data = make_api_request(url)
    if data is None:
        return
    
    # Przechodzenie przez wszystkie urządzenia
    for worker in data['workers']:
        # Ścieżka pliku na podstawie nazwy urządzenia
        file_name = f"{worker['name']}.json"
        directory_path = os.path.join(hashrate_dir)
        file_path = os.path.join(directory_path, file_name)

        # Tworzenie katalogu, jeśli nie istnieje
        os.makedirs(directory_path, exist_ok=True)
        
        # Odczytywanie istniejących danych
        existing_data = read_json_file(file_path)
        
        # Konwersja timestampu na czytelną datę UTC
        last_share_time_utc = datetime.fromtimestamp(worker["last_share_time"], timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        
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
    
    print("Dane zapisane/zaktualizowane w plikach JSON.")

# Wykonanie funkcji
if __name__ == "__main__":
    main()
