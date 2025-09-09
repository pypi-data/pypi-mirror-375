# squatspotter/reporting.py
import csv
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from colorama import Fore, Style

def _sauvegarder_csv(resultats, nom_fichier):
    with open(nom_fichier, "w", newline="", encoding='utf-8') as f:
        fieldnames = ["domaine", "ns", "mx", "registered", "categorie", "error_message"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(resultats)

def _sauvegarder_json(resultats, nom_fichier):
    with open(nom_fichier, "w", encoding='utf-8') as f:
        json.dump(resultats, f, indent=4, ensure_ascii=False)

def _sauvegarder_txt(resultats, nom_fichier):
    with open(nom_fichier, "w", encoding='utf-8') as f:
        f.write(f"Rapport d'analyse Typosquatting - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        domaines_actifs = [r for r in resultats if r['categorie'] in ['repond_infos_completes', 'repond_mais_vide']]
        for res in domaines_actifs:
            f.write(f"Domaine    : {res['domaine']}\n")
            f.write(f"Catégorie  : {res['categorie']}\n")
            f.write(f"NS Records : {res.get('ns', 'N/A')}\n")
            f.write(f"MX Records : {res.get('mx', 'N/A')}\n")
            f.write("-" * 50 + "\n")

def _sauvegarder_xml(resultats, nom_fichier):
    root = ET.Element("ScanResultats")
    for res in resultats:
        domaine_elem = ET.SubElement(root, "Domaine")
        for cle, valeur in res.items():
            child = ET.SubElement(domaine_elem, cle.capitalize())
            child.text = str(valeur)
    xml_str = ET.tostring(root, 'utf-8')
    parsed_str = minidom.parseString(xml_str)
    pretty_xml_str = parsed_str.toprettyxml(indent="  ")
    with open(nom_fichier, "w", encoding='utf-8') as f:
        f.write(pretty_xml_str)

def sauvegarder_resultats(resultats, nom_fichier, format_sortie):
    """Fonction principale qui appelle la bonne méthode de sauvegarde."""
    print(f"\nSauvegarde de {len(resultats)} résultats dans le fichier '{nom_fichier}' au format {format_sortie.upper()}...")
    try:
        if format_sortie == 'csv':
            _sauvegarder_csv(resultats, nom_fichier)
        elif format_sortie == 'json':
            _sauvegarder_json(resultats, nom_fichier)
        elif format_sortie == 'xml':
            _sauvegarder_xml(resultats, nom_fichier)
        elif format_sortie == 'txt':
            _sauvegarder_txt(resultats, nom_fichier)
        print(f"{Fore.GREEN}Sauvegarde terminée avec succès.{Style.RESET_ALL}")
    except IOError as e:
        print(f"{Fore.RED}Erreur lors de l'écriture du fichier : {e}{Style.RESET_ALL}")