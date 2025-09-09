# squatspotter/cli.py
import argparse
import sys
from datetime import datetime
from colorama import Fore, Style, init

# Imports depuis nos propres modules
from .core import lancer_scan_initial, lancer_surveillance, verifier_domaine
from .reporting import sauvegarder_resultats

# Initialisation de colorama
init(autoreset=True)

def main():
    """Fonction principale du script."""
    parser = argparse.ArgumentParser(
        description="Outil de génération et de vérification de typosquatting.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # --- Arguments Restaurés ---
    parser.add_argument("domaine", nargs='?', default=None, help="Le domaine cible pour un NOUVEAU scan.")
    
    # Options de Scan
    parser.add_argument("-w", "--wordlist", default="dict/french.dict", help="Wordlist de sous-domaines.\n(défaut: french.dict)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Affiche des informations détaillées.")
    parser.add_argument("--workers", type=int, default=50, help="Nombre de threads pour la vérification DNS.\n(défaut: 50)")

    # Options de Sortie
    parser.add_argument("-o", "--output", help="Fichier de sortie pour les résultats.")
    parser.add_argument("-f", "--format", choices=['csv', 'json', 'xml', 'txt'], default='csv', help="Format du fichier de sortie.\n(défaut: csv)")

    # Options pour désactiver des fonctionnalités
    parser.add_argument("--no-bruteforce", action="store_true", help="Désactive le bruteforce de sous-domaines.")
    parser.add_argument("--no-dns-check", action="store_true", help="Désactive la vérification DNS.")

    # Options du Mode Surveillance
    parser.add_argument("--surveillance", help="Lance le mode surveillance sur un fichier CSV existant.")
    parser.add_argument("--send-email", action="store_true", help="Active l'envoi d'email en mode surveillance.")

    args = parser.parse_args()

    if args.surveillance:
        if not args.domaine:
            print(f"{Fore.RED}Erreur: Le mode --surveillance requiert le nom du domaine cible pour les alertes.{Style.RESET_ALL}")
            sys.exit(1)
        lancer_surveillance(args.surveillance, args.domaine, workers=args.workers, verbose=args.verbose, send_email=args.send_email)
        sys.exit(0)

    if not args.domaine:
        parser.print_help()
        sys.exit(1)

    # --- Lancement du scan initial via le module core ---
    resultats_analyses = lancer_scan_initial(args)

    # --- Affichage du résumé ---
    print(f"\n{Fore.GREEN}Traitement terminé !{Style.RESET_ALL}")
    
    # Affichage des résultats en direct
    cat_complet = 0
    cat_vide = 0
    for resultat in resultats_analyses:
        categorie = resultat["categorie"]
        if categorie == "repond_infos_completes":
            cat_complet += 1
            print(f"{Fore.GREEN}[+] Domaine avec infos DNS : {resultat['domaine']}{Style.RESET_ALL}")
        elif categorie == "repond_mais_vide":
            cat_vide += 1
            print(f"{Fore.YELLOW}[-] Domaine répond mais sans NS/MX : {resultat['domaine']}{Style.RESET_ALL}")
    
    # Affichage du résumé statistique
    cat_inactif = len(resultats_analyses) - cat_complet - cat_vide
    
    print("\n--- Résumé de l'analyse ---")
    print(f"{Fore.GREEN}Domaines avec infos complètes : {cat_complet}")
    print(f"{Fore.YELLOW}Domaines qui répondent (sans NS/MX) : {cat_vide}")
    if args.verbose:
        print(f"{Fore.RED}Domaines inactifs (inclus dans le rapport) : {cat_inactif}")


    # --- Gestion de la sauvegarde via le module reporting ---
    output_file = args.output
    if not args.surveillance and not output_file:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        safe_domain_name = args.domaine.replace('.', '_')
        output_file = f"scan_{safe_domain_name}_{timestamp}.{args.format}"
        print(f"\n{Fore.YELLOW}Aucun fichier de sortie spécifié. Utilisation du nom par défaut : {output_file}{Style.RESET_ALL}")

    if output_file:
        sauvegarder_resultats(resultats_analyses, output_file, args.format)

if __name__ == "__main__":
    main()