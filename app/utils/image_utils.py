from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Tuple


def generate_countdown_image(
    time_remaining_seconds: int, width: int = 200, height: int = 60
) -> bytes:
    """
    Génère une image PNG affichant un compte à rebours.

    Args:
        time_remaining_seconds (int): Le temps restant en secondes.
        width (int): Largeur de l'image.
        height (int): Hauteur de l'image.

    Returns:
        bytes: Les données binaires de l'image PNG.
    """
    # Crée une image blanche
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Détermine le texte du compte à rebours
    if time_remaining_seconds <= 0:
        countdown_text = "00:00"
        text_color = (255, 0, 0)  # Rouge pour expiré
    else:
        minutes = time_remaining_seconds // 60
        seconds = time_remaining_seconds % 60
        countdown_text = f"{minutes:02}:{seconds:02}"
        text_color = (0, 0, 0)  # Noir par défaut

    # Tente de charger une police de caractères. Utilise la police par défaut si non trouvée.
    try:
        # Chemin vers une police TrueType (vous devrez peut-être ajuster ce chemin)
        # Pour les systèmes Windows, vous pouvez essayer "arial.ttf" ou "consola.ttf"
        # Pour Linux/macOS, "DejaVuSans-Bold.ttf" ou "Arial.ttf" si installé
        font = ImageFont.truetype(
            "arial.ttf", 30
        )  # Essayez une police système courante
    except IOError:
        # Fallback vers la police par défaut si la police spécifiée n'est pas trouvée
        font = ImageFont.load_default()
        print(
            "Avertissement: Police 'arial.ttf' non trouvée, utilisation de la police par défaut."
        )

    # Calcule la taille du texte
    bbox = d.textbbox((0, 0), countdown_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calcule la position pour centrer le texte
    x = (width - text_width) / 2
    y = (height - text_height) / 2 - 5  # Ajustement léger pour le centrage visuel

    # Dessine le texte
    d.text((x, y), countdown_text, fill=text_color, font=font)

    # Sauvegarde l'image en mémoire sous forme de bytes (PNG)
    byte_io = BytesIO()
    img.save(byte_io, "PNG")
    byte_io.seek(0)
    return byte_io.getvalue()
