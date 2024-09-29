import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Wczytywanie zmiennych środowiskowych z pliku .env
load_dotenv()

def make_api_request(url):
    """Wysyła zapytanie GET do podanego URL i zwraca dane JSON."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Nie udało się połączyć z API: {e}")
        return None

def read_json_file(file_path):
    """Odczytuje dane JSON z pliku i zwraca je jako obiekt Python."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Błąd dekodowania JSON z pliku: {file_path}")
            return []
        except Exception as e:
            print(f"Nie udało się otworzyć pliku {file_path}: {e}")
            return []
    else:
        return []

def write_json_file(file_path, data):
    """Zapisuje dane JSON do pliku."""
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Nie udało się zapisać danych do pliku {file_path}: {e}")

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
            print(f"Błąd dekodowania JSON w pliku: {file_path}")
            return None
        except Exception as e:
            print(f"Nie udało się otworzyć pliku {file_path}: {e}")
            return None
    else:
        print(f"Plik {file_path} nie istnieje.")
        return None
    
def get_environ(env_name):
    """Wczytuje dane z pliku env."""
    value = os.environ.get(env_name)
    if not value:
        print(f"Wartość nie został określona w pliku .env (zmienna {env_name}).")
        return None
    
    return value

def replace_placeholders(html_content, placeholders):
    """Zamienia symbole zastępcze "placeholders" na rzeczywiste dane"""
    for key, value in placeholders.items():
        html_content = html_content.replace(f"[[[{key}]]]", value)
    return html_content
