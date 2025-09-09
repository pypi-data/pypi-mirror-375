# squatspotter/utils.py
def strip_html(text):
    """Nettoie les balises HTML simples pour l'affichage console."""
    return text.replace('<strong>', '').replace('</strong>', '').replace('<em>', '').replace('</em>', '')