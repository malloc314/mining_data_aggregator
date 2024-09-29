from helper import get_json_files, parse_date_from_filename, compute_statistics, load_data, write_json_file, get_environ
from datetime import datetime, timezone
import os

def main():
    # Pobieranie zmiennych
    data_dir = get_environ("DATA_DIR")
    if not data_dir: return
    report_dir = get_environ("REPORT_DIR")
    if not report_dir: return
    revenue_dir = get_environ("REVENUE_DIR")
    if not revenue_dir: return

    # Ścieżki
    report_path = os.path.join(data_dir, report_dir)
    revenue_path = os.path.join(data_dir, revenue_dir)

    # Aktualna data i czas UTC
    datetime_utc = datetime.now(timezone.utc)
    datetime_utc_string = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")
    
    # Sprawdzenie, czy katalog z danymi istnieje
    if not os.path.isdir(revenue_path):
        print(f"{datetime_utc_string}(UTC) - Katalog {revenue_path} nie istnieje")
        return

    # Pobranie listy plików JSON
    json_files = get_json_files(revenue_path)
    if not json_files:
        print(f"{datetime_utc_string}(UTC) - Brak plików JSON w katalogu {revenue_path}")
        return

    # Parsowanie dat z nazw plików i filtrowanie poprawnych
    dated_files = []
    for file in json_files:
        file_date = parse_date_from_filename(file)
        if file_date:
            dated_files.append((file_date, file))
        else:
            print(f"{datetime_utc_string}(UTC) - Pomijanie pliku z niepoprawnym formatem daty: {file}")

    if not dated_files:
        print(f"{datetime_utc_string}(UTC) - Nie znaleziono żadnych plików z poprawnym formatem daty")
        return

    # Sortowanie plików według daty
    dated_files.sort(key=lambda x: x[0])

    # Plik genesis (najwcześniejszy) i current (najpóźniejszy)
    genesis_date, genesis_file = dated_files[0]
    current_date, current_file = dated_files[-1]

    genesis_date_str = genesis_date.strftime("%Y-%m-%d")
    current_date_str = current_date.strftime("%Y-%m-%d")

    # Wczytywanie danych z plików
    genesis_data = load_data(os.path.join(revenue_path, genesis_file))
    current_data = load_data(os.path.join(revenue_path, current_file))

    if genesis_data is None or current_data is None:
        print(f"{datetime_utc_string}(UTC) - Nie można wczytać danych z plików. Przerywam działanie skryptu")
        return
    
    # Obliczanie statystyk
    genesis_min, genesis_max, genesis_avg = compute_statistics(genesis_data)
    current_min, current_max, current_avg = compute_statistics(current_data)

    if None in [genesis_min, genesis_max, genesis_avg, current_min, current_max, current_avg]:
        print(f"{datetime_utc_string}(UTC) - Błąd w obliczaniu statystyk. Upewnij się, że dane są poprawne")
        return

    # Przygotowanie danych do raportu
    report_data = {
        "genesis": {
            "date": genesis_date_str,
            "min_revenue60m": genesis_min,
            "max_revenue60m": genesis_max,
            "avg_revenue60m": genesis_avg
        },
        "current": {
            "date": current_date_str,
            "min_revenue60m": current_min,
            "max_revenue60m": current_max,
            "avg_revenue60m": current_avg
        }
    }

    # Ścieżka do pliku raportu
    file_name = f"{current_date_str}.json"
    file_path = os.path.join(report_path, file_name)

    # Tworzenie katalogu na raport, jeśli nie istnieje
    os.makedirs(report_path, exist_ok=True)

    # Zapisywanie raportu
    write_json_file(file_path, report_data)

    print(f"{datetime_utc_string}(UTC) - Dane zapisane do pliku: {file_path}")

if __name__ == "__main__":
    main()
