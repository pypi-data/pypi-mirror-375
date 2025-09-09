# squatspotter/core.py
import os
import sys
import csv
import concurrent.futures
from tqdm import tqdm
from colorama import Fore, Style

# Imports depuis nos propres modules
from .dnschecker import get_dns_info
from .listMaker import generer_typosquatting, generer_bruteforce_sous_domaines
from .notifications import envoyer_email_alerte
from .utils import strip_html

def verifier_domaine(domain):
    """Vérifie un seul domaine et retourne son dictionnaire de résultat."""
    info = get_dns_info(domain)
    resultat = {"domaine": domain, "ns": "", "mx": "", "registered": False, "categorie": ""}

    if 'error' not in info:
        resultat["registered"] = True
        ns_records = "; ".join(info.get('ns', []))
        mx_data = info.get('mx', [])
        mx_records_list = [f"{rec.get('exchange', '')} (prio {rec.get('priority', 'N/A')})" for rec in mx_data]
        mx_records = "; ".join(mx_records_list)
        resultat["ns"] = ns_records
        resultat["mx"] = mx_records
        resultat["categorie"] = "repond_infos_completes" if (ns_records or mx_records) else "repond_mais_vide"
    else:
        resultat["categorie"] = "ne_repond_pas"
        resultat["error_message"] = info['error']

    return resultat

def lancer_scan_initial(args):
    """Orchestre un scan complet à partir des arguments CLI."""
    print(f"{Fore.CYAN}--- Étape 1: Génération des variations pour '{args.domaine}' ---{Style.RESET_ALL}")
    liste_typos = generer_typosquatting(args.domaine)
    print(f"{Fore.GREEN}▶ {len(liste_typos)} variations de base générées.{Style.RESET_ALL}")

    domaines_a_tester = set(liste_typos)
    temp_domaine_file = "typos_temp.txt"

    if not args.no_bruteforce:
        print(f"\n{Fore.CYAN}--- Étape 2: Bruteforce des sous-domaines avec '{args.wordlist}' ---{Style.RESET_ALL}")
        with open(temp_domaine_file, "w", encoding='utf-8') as f:
            for typo in liste_typos:
                f.write(typo + "\n")
        liste_bruteforce = generer_bruteforce_sous_domaines(temp_domaine_file, args.wordlist)
        if liste_bruteforce and not liste_bruteforce[0].startswith("Erreur:"):
            print(f"{Fore.GREEN}▶ {len(liste_bruteforce)} domaines supplémentaires générés.{Style.RESET_ALL}")
            domaines_a_tester.update(liste_bruteforce)
        else:
            print(f"{Fore.YELLOW}Avertissement: Le bruteforce n'a rien donné ou a rencontré une erreur.{Style.RESET_ALL}")
            if liste_bruteforce: print(f"{Fore.RED}{liste_bruteforce[0]}{Style.RESET_ALL}")
    
    if os.path.exists(temp_domaine_file):
        os.remove(temp_domaine_file)

    domaines_a_verifier = sorted(list(domaines_a_tester))
    print(f"\n{Fore.YELLOW}Total de {len(domaines_a_verifier)} domaines uniques générés.{Style.RESET_ALL}")
    
    resultats_analyses = []

    if not args.no_dns_check:
        print(f"\n{Fore.CYAN}--- Étape 3: Vérification DNS (mode multi-thread) ---{Style.RESET_ALL}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            resultats_map = executor.map(verifier_domaine, domaines_a_verifier)
            for resultat in tqdm(resultats_map, total=len(domaines_a_verifier), desc="Vérification DNS", unit="domaine"):
                resultats_analyses.append(resultat)
    else:
        #... (logique de no_dns_check)
        pass # La logique d'affichage et de résumé sera dans cli.py

    return resultats_analyses


def lancer_surveillance(fichier_csv, domaine_cible, workers=50, verbose=False, send_email=False):
    """Lit un fichier CSV, re-scanne les domaines et détecte les changements."""
    print(f"{Fore.CYAN}--- Lancement du mode surveillance sur '{fichier_csv}' ---{Style.RESET_ALL}")
    if not os.path.exists(fichier_csv):
        print(f"{Fore.RED}Erreur: Le fichier '{fichier_csv}' est introuvable.{Style.RESET_ALL}")
        return

    try:
        with open(fichier_csv, 'r', newline='', encoding='utf-8') as f:
            etat_precedent = {row['domaine']: row for row in csv.DictReader(f)}
    except Exception as e:
        print(f"{Fore.RED}Erreur lors de la lecture du fichier CSV : {e}{Style.RESET_ALL}")
        return

    domaines_a_scanner = list(etat_precedent.keys())
    print(f"{len(domaines_a_scanner)} domaines à re-scanner...")
    changements, resultats_actualises = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        resultats_map = executor.map(verifier_domaine, domaines_a_scanner)
        for etat_actuel in tqdm(resultats_map, total=len(domaines_a_scanner), desc="Surveillance", unit="domaine"):
            domain = etat_actuel["domaine"]
            ancien_etat = etat_precedent.get(domain, {})
            if ancien_etat.get('categorie') != etat_actuel['categorie']:
                msg = f"<strong>{domain}</strong> est passé de <em>{ancien_etat.get('categorie', 'inconnu')}</em> à <em>{etat_actuel['categorie']}</em>"
                changements.append(msg)
            # ... (autres vérifications de changement)
            resultats_actualises.append(etat_actuel)

    print(f"\nMise à jour du fichier de surveillance '{fichier_csv}'...")
    # La sauvegarde est gérée par le module reporting, mais ici on met à jour le fichier de base
    try:
        with open(fichier_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["domaine", "ns", "mx", "registered", "categorie", "error_message"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(resultats_actualises)
        print(f"{Fore.GREEN}Fichier mis à jour.{Style.RESET_ALL}")
    except IOError as e:
        print(f"{Fore.RED}Erreur lors de la mise à jour du fichier : {e}{Style.RESET_ALL}")
        
    print("\n--- Résumé de la surveillance ---")
    if changements:
        print(f"{Fore.YELLOW}{len(changements)} changement(s) détecté(s).{Style.RESET_ALL}")
        if verbose:
            print("Détails des changements :")
            for ch in changements:
                print(f"- {strip_html(ch)}")
    else:
        print(f"{Fore.GREEN}Aucun changement détecté.{Style.RESET_ALL}")
    
    if send_email and changements:
        envoyer_email_alerte(changements, domaine_cible)