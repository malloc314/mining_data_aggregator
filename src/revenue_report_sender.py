import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from helper import get_environ, replace_placeholders, get_html_template, get_revenue60m_data, set_bg_color, set_html_entity, get_datetime_utc

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
    msg_organization = get_environ("MSG_ORGANIZATION")
    if not msg_organization: msg_organization = "This is organization"
    from_email = get_environ("FROM_EMAIL")
    if not from_email: return
    to_emails = get_environ("TO_EMAILS")
    if not to_emails: return

    # Parsowanie listy adresów email
    to_emails = [email.strip() for email in to_emails.split(",")]

    # Aktualna data i czas UTC
    datetime_utc, date_utc_string, datetime_utc_string = get_datetime_utc()

    # Tworzenie wiadomości
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Raport finansowy - {msg_organization}"
    msg["From"] = from_email

    # Odczytywanie szablonu HTML z pliku
    html_template = get_html_template(template_dir, template_file_name)
    if not html_template: return

    # Odczytywanie danych z raportu
    (
        start_date_archival, end_date_archival, min_revenue_archival, max_revenue_archival, avg_revenue_archival, 
        start_date_current, end_date_current, min_revenue_current, max_revenue_current, avg_revenue_current, 
        min_revenue_percent, max_revenue_percent, avg_revenue_percent
    ) = get_revenue60m_data(data_dir, report_dir)

    # Przygotowanie danych do zastąpienia
    placeholders = {
        "DATE-TIME-NOW": str(date_utc_string),
        "ORGANIZATION": str(msg_organization),
        "SUBJECT": "Raport finansowy",
        "START_DATE_ARCHIVAL": start_date_archival,
        "END_DATE_ARCHIVAL": end_date_archival,
        "START_DATE_CURRENT": start_date_current,
        "END_DATE_CURRENT": end_date_current,
        # MIN
        "MIN-REVENUE-ARCHIVAL": str(min_revenue_archival),
        "MIN-REVENUE-CURRENT": str(min_revenue_current),
        "MIN-REVENUE-PERCENT": str(min_revenue_percent),
        "MIN-BG-COLOR": set_bg_color(min_revenue_percent),
        "MIN-HTML-ENTITY": set_html_entity(min_revenue_percent),
        # MAX
        "MAX-REVENUE-ARCHIVAL": str(max_revenue_archival),
        "MAX-REVENUE-CURRENT": str(max_revenue_current),
        "MAX-REVENUE-PERCENT": str(max_revenue_percent),
        "MAX-BG-COLOR": set_bg_color(max_revenue_percent),
        "MAX-HTML-ENTITY": set_html_entity(max_revenue_percent),
        # AVG
        "AVG-REVENUE-ARCHIVAL": str(avg_revenue_archival),
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
