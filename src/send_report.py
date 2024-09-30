import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from helper import get_environ, replace_placeholders, read_json_file

def main():
    # Pobieranie zmiennych
    data_dir = get_environ("DATA_DIR")
    if not data_dir: return
    report_dir = get_environ("REPORT_DIR")
    if not report_dir: return
    template_dir = get_environ("TEMPLATE_DIR")
    if not template_dir: return
    template_file_name = get_environ("TEMPLATE_FILE_NAME")
    if not template_file_name: return
    smtp_server = get_environ("SMTP_SERVER")
    if not smtp_server: return
    smtp_port = get_environ("SMTP_PORT")
    if not smtp_port: return
    smtp_username = get_environ("SMTP_USERNAME")
    if not smtp_username: return
    smtp_password = get_environ("SMTP_PASSWORD")
    if not smtp_password: return
    msg_subject = get_environ("MSG_SUBJECT")
    if not msg_subject: msg_subject = "This is subject"
    msg_organization = get_environ("MSG_ORGANIZATION")
    if not msg_organization: msg_organization = "This is organization"
    from_email = get_environ("FROM_EMAIL")
    if not from_email: return
    to_emails = get_environ("TO_EMAILS")
    if not to_emails: return

    # Parsowanie listy adresów email
    to_emails = [email.strip() for email in to_emails.split(",")]

    # Aktualna data i czas UTC
    datetime_utc = datetime.now(timezone.utc)
    date_utc_string = datetime_utc.strftime("%Y-%m-%d")
    datetime_utc_string = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")

    # Tworzenie wiadomości
    msg = MIMEMultipart("alternative")
    msg["Subject"] = msg_subject
    msg["From"] = from_email

    # Odczytywanie szablonu HTML z pliku
    template_file_path = os.path.join(template_dir, template_file_name)
    try:
        with open(template_file_path, "r", encoding="utf-8") as file:
            html_template = file.read()
    except Exception as e:
        print(f"{datetime_utc_string}(UTC) - Wystąpił błąd podczas wczytywania szablonu HTML: {e}")
        return
    
    # Odczytywanie istniejących danych
    report_path = os.path.join(data_dir, report_dir)
    report_file_name = f"{date_utc_string}.json"
    report_file_path = os.path.join(report_path, report_file_name)
    report_data = read_json_file(report_file_path)

    if not report_data:
        print(f"{datetime_utc_string}(UTC) - Brak raportu z dnia {date_utc_string}")
        return

    # Pobieranie danych z raportu
    min_revenue_history = report_data["history"]["min_revenue60m"]
    max_revenue_history = report_data["history"]["max_revenue60m"]
    avg_revenue_history = report_data["history"]["avg_revenue60m"]
    min_revenue_current = report_data["current"]["min_revenue60m"]
    max_revenue_current = report_data["current"]["max_revenue60m"]
    avg_revenue_current = report_data["current"]["avg_revenue60m"]
    
    # Obliczenie procentowej zmiany
    def calculate_percentage_change(current, history):
        if history != 0:
            return ((current - history) / history) * 100
        else:
            return 0

    min_revenue_percent = calculate_percentage_change(min_revenue_current, min_revenue_history)
    max_revenue_percent = calculate_percentage_change(max_revenue_current, max_revenue_history)
    avg_revenue_percent = calculate_percentage_change(avg_revenue_current, avg_revenue_history)

    # Zaokrąglanie wyników do dwóch miejsc po przecinku
    min_revenue_percent = round(min_revenue_percent, 2)
    max_revenue_percent = round(max_revenue_percent, 2)
    avg_revenue_percent = round(avg_revenue_percent, 2)

    # Ustawienie koloru tła "Badge"
    # #70C7BA if revenue_percent > 0
    # #c76f6f if revenue_percent < 0
    # #c7c7c7 if revenue_percent == 0
    def set_bg_color(revenue_percent):
        if revenue_percent > 0:
            return "#70C7BA"
        elif revenue_percent < 0:
            return "#c76f6f"
        elif revenue_percent == 0:
            return "#c7c7c7"
    
    # Ustawienie encji HTML "<", ">", "="
    # &gt; if revenue_percent > 0
    # &lt; if revenue_percent < 0
    # &equals; if revenue_percent == 0
    def set_html_entity(revenue_percent):
        if revenue_percent > 0:
            return "&gt;"
        elif revenue_percent < 0:
            return "&lt;"
        elif revenue_percent == 0:
            return "&equals;"

    # Przygotowanie danych do zastąpienia
    placeholders = {
        "DATE-TIME-NOW": str(date_utc_string),
        "ORGANIZATION": str(msg_organization),
        # MIN
        "MIN-REVENUE-HISTORY": str(min_revenue_history),
        "MIN-REVENUE-CURRENT": str(min_revenue_current),
        "MIN-REVENUE-PERCENT": str(min_revenue_percent),
        "MIN-BG-COLOR": set_bg_color(min_revenue_percent),
        "MIN-HTML-ENTITY": set_html_entity(min_revenue_percent),
        # MAX
        "MAX-REVENUE-HISTORY": str(max_revenue_history),
        "MAX-REVENUE-CURRENT": str(max_revenue_current),
        "MAX-REVENUE-PERCENT": str(max_revenue_percent),
        "MAX-BG-COLOR": set_bg_color(max_revenue_percent),
        "MAX-HTML-ENTITY": set_html_entity(max_revenue_percent),
        # AVG
        "AVG-REVENUE-HISTORY": str(avg_revenue_history),
        "AVG-REVENUE-CURRENT": str(avg_revenue_current),
        "AVG-REVENUE-PERCENT": str(avg_revenue_percent),
        "AVG-BG-COLOR": set_bg_color(avg_revenue_percent),
        "AVG-HTML-ENTITY": set_html_entity(avg_revenue_percent)
    }

    # Treść wiadomości w HTML
    html_content = replace_placeholders(html_template, placeholders)

    # Dodawanie treści do wiadomości
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)

    # Inicjalizacja połączenia SMTP
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Inicjowanie szyfrowania TLS
        server.login(smtp_username, smtp_password)
    except Exception as e:
        print(f"{datetime_utc_string}(UTC) - Wystąpił błąd podczas łączenia z serwerem SMTP: {e}")
        return

    # Wysyłanie wiadomości do każdego odbiorcy
    for to_email in to_emails:
        try:
            # Aktualizacja pola "To"
            msg["To"] = to_email

            # Wysłanie wiadomości
            server.sendmail(from_email, to_email, msg.as_string())
            print(f"{datetime_utc_string}(UTC) - Wiadomość została wysłana do {to_email}")
        except Exception as e:
            print(f"{datetime_utc_string}(UTC) - Wystąpił błąd podczas wysyłania do {to_email}: {e}")

    # Zamknięcie połączenia SMTP
    server.quit()

# Wykonanie funkcji
if __name__ == "__main__":
    main()
