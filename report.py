from library import get_json_files, parse_date_from_filename, compute_statistics, load_data, write_json_file
from dotenv import load_dotenv
import os

# Wczytywanie zmiennych środowiskowych z pliku .env
load_dotenv()

def main():
    revenue_dir = os.environ.get('REVENUE_DIR')
    if not revenue_dir:
        print("Wartość nie został określona w pliku .env (zmienna 'REVENUE_DIR').")
        return

    report_dir = os.environ.get('REPORT_DIR')
    if not report_dir:
        print("Wartość nie został określona w pliku .env (zmienna 'REPORT_DIR').")
        return

    # Sprawdzenie, czy katalog z danymi istnieje
    if not os.path.isdir(revenue_dir):
        print(f"Katalog '{revenue_dir}' nie istnieje.")
        return

    # Pobranie listy plików JSON
    json_files = get_json_files(revenue_dir)
    if not json_files:
        print(f"Brak plików JSON w katalogu '{revenue_dir}'.")
        return

    # Parsowanie dat z nazw plików i filtrowanie poprawnych
    dated_files = []
    for file in json_files:
        file_date = parse_date_from_filename(file)
        if file_date:
            dated_files.append((file_date, file))
        else:
            print(f"Pomijanie pliku z niepoprawnym formatem daty: {file}")

    if not dated_files:
        print("Nie znaleziono żadnych plików z poprawnym formatem daty.")
        return

    # Sortowanie plików według daty
    dated_files.sort(key=lambda x: x[0])

    # Plik genesis (najwcześniejszy) i current (najpóźniejszy)
    genesis_date, genesis_file = dated_files[0]
    current_date, current_file = dated_files[-1]

    print(f"Plik genesis: {genesis_file} ({genesis_date.strftime('%Y-%m-%d')})")
    print(f"Plik current: {current_file} ({current_date.strftime('%Y-%m-%d')})")

    # Wczytywanie danych z plików
    genesis_data = load_data(os.path.join(revenue_dir, genesis_file))
    current_data = load_data(os.path.join(revenue_dir, current_file))

    if genesis_data is None or current_data is None:
        print("Nie można wczytać danych z plików. Przerywam działanie skryptu.")
        return

    # Obliczanie statystyk
    genesis_min, genesis_max, genesis_avg = compute_statistics(genesis_data)
    current_min, current_max, current_avg = compute_statistics(current_data)

    if None in [genesis_min, genesis_max, genesis_avg, current_min, current_max, current_avg]:
        print("Błąd w obliczaniu statystyk. Upewnij się, że dane są poprawne.")
        return

    # Przygotowanie danych do raportu
    report_data = {
        "genesis": {
            "date": genesis_date.strftime('%Y-%m-%d'),
            "min_revenue60m": genesis_min,
            "max_revenue60m": genesis_max,
            "avg_revenue60m": genesis_avg
        },
        "current": {
            "date": current_date.strftime('%Y-%m-%d'),
            "min_revenue60m": current_min,
            "max_revenue60m": current_max,
            "avg_revenue60m": current_avg
        }
    }

    # Tworzenie katalogu na raport, jeśli nie istnieje
    os.makedirs(report_dir, exist_ok=True)

    # Ścieżka do pliku raportu
    report_filename = f"{current_date.strftime('%Y-%m-%d')}.json"
    report_path = os.path.join(report_dir, report_filename)

    # Zapisywanie raportu
    write_json_file(report_path, report_data)

if __name__ == "__main__":
    main()
