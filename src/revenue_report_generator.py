from helper import get_json_files, parse_date_from_filename, compute_statistics, load_data, write_json_file, get_environ, get_datetime_utc, get_revenue60m_data
from datetime import datetime, timezone
import sys
import os

def main():
    try:
        # Sprawdzenie, czy argument został przekazany
        if len(sys.argv) < 2:
            raise ValueError("Nie podano indeksu jako argumentu.")
        
        # Interwał czasowy w dniach
        days_arg = sys.argv[1]

        # Próba konwersji argumentu na integer
        days_index = int(days_arg)
        
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
        datetime_utc, date_utc_string, datetime_utc_string = get_datetime_utc()
        
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

        # Sprawdzenie, czy indeks jest w zakresie listy
        if days_index < 0 or days_index >= len(dated_files):
            raise IndexError(f"Indeks {days_index} jest poza zakresem listy.")

        # Pliki archiwalne - pobranie wszystkich plików z wyjątkiem bieżących
        archival_files = dated_files[:-days_index]
        archival_start_date, _ = archival_files[0]
        archival_start_date = archival_start_date.strftime("%Y-%m-%d")
        archival_end_date, _ = archival_files[-1]
        archival_end_date = archival_end_date.strftime("%Y-%m-%d")
        
        # Plik bieżące - pobranie bieżących plików z wyjątkiem archiwalnych
        current_files = dated_files[-days_index:]
        current_start_date, _ = current_files[0]
        current_start_date = current_start_date.strftime("%Y-%m-%d")
        current_end_date, _ = current_files[-1]
        current_end_date = current_end_date.strftime("%Y-%m-%d")

        # Wczytywanie danych z archiwalnych plików
        combined_archival_data = []
        for archival_file in archival_files:
            _, archival_file_name = archival_file
            data = load_data(os.path.join(revenue_path, archival_file_name))
            if data is not None:
                combined_archival_data.extend(data)
            else:
                print(f"{datetime_utc_string}(UTC) - Nie można wczytać danych z pliku: {archival_file_name}")

        # Sprawdzanie, czy dane znajdują się w plikach
        if not combined_archival_data:
            print(f"{datetime_utc_string}(UTC) - Brak danych w plikach archiwalnych")
            return

        # Wczytywanie danych z bieżących plików
        combined_current_data = []
        for current_file in current_files:
            _, current_file_name = current_file
            data = load_data(os.path.join(revenue_path, current_file_name))
            if data is not None:
                combined_current_data.extend(data)
            else:
                print(f"{datetime_utc_string}(UTC) - Nie można wczytać danych z pliku: {current_file_name}")

        # Sprawdzanie, czy dane znajdują się w plikach
        if not combined_current_data:
            print(f"{datetime_utc_string}(UTC) - Brak danych w plikach bieżących")
            return

        # Obliczanie statystyk dla danych archiwalnych
        archive_min, archive_max, archive_avg = compute_statistics(combined_archival_data)
        # Obliczanie statystyk dla danych bieżących
        current_min, current_max, current_avg = compute_statistics(combined_current_data)

        # Sprawdzanie, czy obliczone dane są poprawne
        if None in [archive_min, archive_max, archive_avg, current_min, current_max, current_avg]:
            print(f"{datetime_utc_string}(UTC) - Błąd w obliczaniu statystyk. Upewnij się, że dane są poprawne")
            return

        def calculate_percentage_change(current, archival):
            if archival != 0:
                return ((current - archival) / archival) * 100
            else:
                return 0
            
        # Obliczenie procentowej zmiany
        percent_min = calculate_percentage_change(current_min, archive_min)
        percent_max = calculate_percentage_change(current_max, archive_max)
        percent_avg = calculate_percentage_change(current_avg, archive_avg)

        # Przygotowanie danych do raportu
        report_data = {
            "archival": {
                "start_date": archival_start_date,
                "end_date": archival_end_date,
                "min_revenue60m": round(archive_min, 6),
                "max_revenue60m": round(archive_max, 6),
                "avg_revenue60m": round(archive_avg, 6)
            },
            "current": {
                "start_date": current_start_date,
                "end_date": current_end_date,
                "min_revenue60m": round(current_min, 6),
                "max_revenue60m": round(current_max, 6),
                "avg_revenue60m": round(current_avg, 6)
            },
            "percentage_change": {
                "min_percent": round(percent_min, 2),
                "max_percent": round(percent_max, 2),
                "avg_percent": round(percent_avg, 2)
            }
        }

        # Ścieżka do pliku raportu
        file_name = f"{date_utc_string}.json"
        file_path = os.path.join(report_path, file_name)

        # Tworzenie katalogu na raport, jeśli nie istnieje
        os.makedirs(report_path, exist_ok=True)

        # Zapisywanie raportu
        write_json_file(file_path, report_data)

        # Generowanie raportu powiodło się
        print(f"{datetime_utc_string}(UTC) - Dane zapisane do pliku: {file_path}")
    except ValueError as ve:
        print(f"Błąd wartości: {ve}")
    except IndexError as ie:
        print(f"Błąd indeksu: {ie}")
    except Exception as e:
        print(f"Niespodziewany błąd: {e}")

if __name__ == "__main__":
    main()
