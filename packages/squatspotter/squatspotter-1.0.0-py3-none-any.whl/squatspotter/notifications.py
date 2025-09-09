# squatspotter/notifications.py
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from colorama import Fore, Style
import dotenv

# On charge les variables d'environnement une seule fois ici
dotenv.load_dotenv()

def envoyer_email_alerte(changements, domaine_cible):
    """Envoie un email si des changements sont détectés."""
    smtp_server, smtp_port, smtp_user, smtp_password, email_from, email_to = (
        os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT"), os.getenv("SMTP_USER"),
        os.getenv("SMTP_PASSWORD"), os.getenv("EMAIL_FROM"), os.getenv("EMAIL_TO")
    )

    if not all([smtp_server, smtp_port, smtp_user, smtp_password, email_from, email_to]):
        print(f"{Fore.RED}Erreur: Variables d'environnement pour l'email manquantes dans le fichier .env.{Style.RESET_ALL}")
        return

    print(f"Préparation de l'alerte email pour {email_to}...")
    date_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sujet = f"Alerte Typosquatting pour {domaine_cible} - {date_scan}"
    corps_html = f"""
    <html><body>
        <h2>Rapport de surveillance Typosquatting pour {domaine_cible}</h2>
        <p><strong>Date du scan :</strong> {date_scan}</p>
        <p>Les changements suivants ont été détectés :</p>
        <ul>{''.join([f'<li>{c}</li>' for c in changements])}</ul>
    </body></html>
    """
    msg = MIMEText(corps_html, 'html')
    msg['Subject'] = sujet
    msg['From'] = email_from
    msg['To'] = email_to

    try:
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(email_from, email_to, msg.as_string())
        print(f"{Fore.GREEN}Email d'alerte envoyé avec succès.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Échec de l'envoi de l'email : {e}{Style.RESET_ALL}")