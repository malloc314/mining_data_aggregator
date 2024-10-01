import requests
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Wczytywanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Aktualna data i czas UTC
datetime_utc = datetime.now(timezone.utc)
date_utc_string = datetime_utc.strftime("%Y-%m-%d")
datetime_utc_string = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")

def get_datetime_utc():
    """Aktualna data i czas UTC"""
    datetime_utc = datetime.now(timezone.utc)
    date_utc_string = datetime_utc.strftime("%Y-%m-%d")
    datetime_utc_string = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")
    return datetime_utc, date_utc_string, datetime_utc_string

def make_api_request(url):
    """Wysyła zapytanie GET do podanego URL i zwraca dane JSON."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{datetime_utc_string}(UTC) - Nie udało się połączyć z API: {e}")
        return None

def read_json_file(file_path):
    """Odczytuje dane JSON z pliku i zwraca je jako obiekt Python."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"{datetime_utc_string}(UTC) - Błąd dekodowania JSON z pliku: {file_path}")
            return []
        except Exception as e:
            print(f"{datetime_utc_string}(UTC) - Nie udało się otworzyć pliku {file_path}: {e}")
            return []
    else:
        return []

def write_json_file(file_path, data):
    """Zapisuje dane JSON do pliku."""
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"{datetime_utc_string}(UTC) - Nie udało się zapisać danych do pliku {file_path}: {e}")

def append_data_to_json_file(file_path, new_data):
    """Dodaje nowe dane do istniejącego pliku JSON."""
    existing_data = read_json_file(file_path)
    existing_data.append(new_data)
    write_json_file(file_path, existing_data)

def get_json_files(directory):
    """Zwraca listę plików JSON w danym katalogu."""
    return [f for f in os.listdir(directory) if f.endswith(".json")]

def parse_date_from_filename(filename):
    """Ekstrahuje datę z nazwy pliku w formacie YYYY-MM-DD.json."""
    try:
        date_str = os.path.splitext(filename)[0]
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def compute_statistics(data):
    """Oblicza minimalną, maksymalną i średnią wartość "revenue60m" w danych."""
    revenues = [entry["revenue60m"] for entry in data if "revenue60m" in entry]
    if not revenues:
        return None, None, None
    min_revenue = min(revenues)
    max_revenue = max(revenues)
    avg_revenue = sum(revenues) / len(revenues)
    return min_revenue, max_revenue, avg_revenue

def load_data(file_path):
    """Wczytuje dane JSON z pliku."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"{datetime_utc_string}(UTC) - Błąd dekodowania JSON w pliku: {file_path}")
            return None
        except Exception as e:
            print(f"{datetime_utc_string}(UTC) - Nie udało się otworzyć pliku {file_path}: {e}")
            return None
    else:
        print(f"{datetime_utc_string}(UTC) - Plik {file_path} nie istnieje.")
        return None
    
def get_environ(env_name):
    """Wczytuje dane z pliku env."""
    value = os.environ.get(env_name)
    if not value:
        print(f"{datetime_utc_string}(UTC) - Wartość nie został określona w pliku .env (zmienna {env_name}).")
        return None
    
    return value

def replace_placeholders(html_content, placeholders):
    """Zamienia symbole zastępcze "placeholders" na rzeczywiste dane"""
    for key, value in placeholders.items():
        html_content = html_content.replace(f"[[[{key}]]]", value)
    return html_content

def get_html_template(template_dir, template_file_name):
    """Wczytuje szablon HTML z pliku"""
    template_file_path = os.path.join(template_dir, template_file_name)
    try:
        with open(template_file_path, "r", encoding="utf-8") as file:
            html_template = file.read()
            return html_template
    except Exception as e:
        print(f"{datetime_utc_string}(UTC) - Wystąpił błąd podczas wczytywania szablonu HTML: {e}")
        return

def get_revenue60m_data(data_dir, report_dir):
    """Wczytuje dane z plików revenue60m"""
    report_path = os.path.join(data_dir, report_dir)
    report_file_name = f"{date_utc_string}.json"
    report_file_path = os.path.join(report_path, report_file_name)
    
    report_data = read_json_file(report_file_path)

    if not report_data:
        print(f"{datetime_utc_string}(UTC) - Brak raportu z dnia {date_utc_string}")
        return
    
    def calculate_percentage_change(current, history):
        if history != 0:
            return ((current - history) / history) * 100
        else:
            return 0
    
    # Pobieranie danych z raportu
    min_revenue_history = report_data["history"]["min_revenue60m"]
    max_revenue_history = report_data["history"]["max_revenue60m"]
    avg_revenue_history = report_data["history"]["avg_revenue60m"]
    min_revenue_current = report_data["current"]["min_revenue60m"]
    max_revenue_current = report_data["current"]["max_revenue60m"]
    avg_revenue_current = report_data["current"]["avg_revenue60m"]

    # Obliczenie procentowej zmiany
    min_revenue_percent = calculate_percentage_change(min_revenue_current, min_revenue_history)
    max_revenue_percent = calculate_percentage_change(max_revenue_current, max_revenue_history)
    avg_revenue_percent = calculate_percentage_change(avg_revenue_current, avg_revenue_history)

    # Zaokrąglanie wyników do dwóch miejsc po przecinku
    min_revenue_percent = round(min_revenue_percent, 2)
    max_revenue_percent = round(max_revenue_percent, 2)
    avg_revenue_percent = round(avg_revenue_percent, 2)

    return (min_revenue_history, max_revenue_history, avg_revenue_history, min_revenue_current, max_revenue_current, avg_revenue_current, min_revenue_percent, max_revenue_percent, avg_revenue_percent)

def set_bg_color(revenue_percent):
    """
    Ustawienie koloru tła "Badge"
    #70C7BA if revenue_percent > 0
    #c76f6f if revenue_percent < 0
    #c7c7c7 if revenue_percent == 0
    """
    if revenue_percent > 0:
        return "#70C7BA"
    elif revenue_percent < 0:
        return "#c76f6f"
    elif revenue_percent == 0:
        return "#c7c7c7"

def set_html_entity(revenue_percent):
    """
    Ustawienie encji HTML "<", ">", "="
    &gt; if revenue_percent > 0
    &lt; if revenue_percent < 0
    &equals; if revenue_percent == 0
    """
    if revenue_percent > 0:
        return "&gt;"
    elif revenue_percent < 0:
        return "&lt;"
    elif revenue_percent == 0:
        return "&equals;"