# -*- coding: utf-8 -*-
"""
Template de CV "Classique" pour MonCV.sn
Reproduit la mise en page: bandeau gris à gauche (photo, coordonnées, langues)
+ colonne principale à droite (profil, compétences, parcours, formation, perso)

Utilisation: remplir le dict CV_DATA plus bas puis lancer le script.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw
import os

# ---------- Palette ----------
SIDEBAR_BG   = HexColor("#E4E4E4")
SIDEBAR_DARK = HexColor("#3B3B3B")
TEXT_DARK    = HexColor("#1B1B1B")
TEXT_GRAY    = HexColor("#5A5A5A")
ACCENT       = HexColor("#2B2B2B")
WHITE        = HexColor("#FFFFFF")

PAGE_W, PAGE_H = A4
SIDEBAR_W = 62 * mm

# ---------- Data (à remplacer par les réponses du formulaire) ----------
CV_DATA = {
    "nom": "Pape Lo",
    "titre": "ETUDIANT",
    "photo": "/home/claude/photo_extracted.png",
    "coordonnees": {
        "adresse": "Château d'Eau Nord, Relais, Mbour",
        "tel": "+221 76 380 45 57",
        "email": "papel5823@gmail.com",
    },
    "langues": [
        {"langue": "Français", "niveau": "C2"},
        {"langue": "Espagnol", "niveau": "A1"},
        {"langue": "Wolof", "niveau": "C2"},
    ],
    "profil": ("Etudiant en Informatique Appliquée à la Gestion des Entreprises à l'ISM Mbour. "
               "Doté de sens de l'organisation et d'une grande capacité à rechercher des opportunités "
               "pour développer mes compétences et acquérir de l'expérience."),
    "competences": ["Gestion du temps", "Travail d'équipe", "Ponctualité", "Sens de l'écoute",
                     "Réseaux sociaux", "Capacité d'apprentissage rapide", "Tableaux dynamiques Excel",
                     "Microsoft Office", "Conception graphique", "Programmation Python", "Tri de documents"],
    "parcours": [
        {
            "poste": "Étudiant informatique appliquée à la gestion des entreprises",
            "structure": "Niang & frère, Mbour",
            "taches": [
                "Travaux en groupe avec d'autres élèves : répartition des tâches, confrontation des idées, production des livrables (exposés, présentations).",
                "Prise de notes durant les cours, mise en forme et classement des différents documents.",
                "Réalisation des travaux demandés conformément aux consignes et remise dans le respect des délais fixés.",
                "Assistance des professeurs dans leurs différents travaux.",
            ],
        }
    ],
    "formation": [
        {"diplome": "Baccalauréat", "detail": "LYCEE DEMBA DIOP, 01/2025"},
        {"diplome": "BFEM", "detail": "CEM Serigne Amadou Wade, 01/2021"},
        {"diplome": "LICENCE", "detail": "Informatique appliquée à la gestion des entreprises — ISM, Mbour"},
    ],
    "personnalise": ["Basket-ball", "Jeux vidéos", "Culture wolof"],
    "projets": [
        {"titre": "Portfolio personnel",
         "description": "Site vitrine HTML/CSS/JS présentant profil, compétences et projets."},
    ],
}

NIVEAUX_ORDRE = ["A1", "A2", "B1", "B2", "C1", "C2"]


def circular_photo(src_path, size_px=500, bg_hex="#E4E4E4"):
    """Renvoie un chemin vers une version rognée en cercle de la photo,
    composée sur un fond opaque (pas de canal alpha -> évite les bugs de mask PDF)."""
    img = Image.open(src_path).convert("RGB")
    side = min(img.size)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((size_px, size_px))

    mask = Image.new("L", (size_px, size_px), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size_px, size_px), fill=255)

    bg_rgb = tuple(int(bg_hex.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    out = Image.new("RGB", (size_px, size_px), bg_rgb)
    out.paste(img, (0, 0), mask)
    out_path = "/home/claude/_photo_circle.png"
    out.save(out_path)
    return out_path


def wrap_text(c, text, font, size, max_width):
    """Retourne une liste de lignes qui tiennent dans max_width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def section_header(c, x, y, title):
    """Icône ronde + titre de section, colonne principale."""
    r = 8
    c.setFillColor(ACCENT)
    c.circle(x + r, y - r + 3, r, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x + r, y - r, "•")
    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(x + 2 * r + 8, y - r + 1, title.upper())
    return y - 2 * r - 6


def bullet_list(c, x, y, items, max_width, font="Helvetica", size=9.2, leading=12.5, bullet="•"):
    c.setFont(font, size)
    c.setFillColor(TEXT_DARK)
    for item in items:
        lines = wrap_text(c, item, font, size, max_width - 12)
        c.setFont(font, size)
        c.drawString(x, y, bullet)
        c.drawString(x + 10, y, lines[0])
        y -= leading
        for extra in lines[1:]:
            c.drawString(x + 10, y, extra)
            y -= leading
        y -= 2
    return y


def build_pdf(data, out_path, watermark=False):
    c = canvas.Canvas(out_path, pagesize=A4)

    # ---------- Sidebar background ----------
    c.setFillColor(SIDEBAR_BG)
    c.rect(0, 0, SIDEBAR_W, PAGE_H, fill=1, stroke=0)

    # ---------- Photo ----------
    photo_y_top = PAGE_H - 20 * mm
    photo_d = 34 * mm
    if data.get("photo") and os.path.exists(data["photo"]):
        circ = circular_photo(data["photo"])
        c.drawImage(ImageReader(circ),
                    (SIDEBAR_W - photo_d) / 2, photo_y_top - photo_d,
                    width=photo_d, height=photo_d)
    else:
        c.setFillColor(SIDEBAR_DARK)
        c.circle(SIDEBAR_W / 2, photo_y_top - photo_d / 2, photo_d / 2, fill=1, stroke=0)

    y = photo_y_top - photo_d - 14 * mm

    # ---------- Coordonnées ----------
    left_margin = 8 * mm
    sidebar_text_w = SIDEBAR_W - 2 * left_margin

    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(left_margin, y, "COORDONNÉES")
    y -= 5
    c.setStrokeColor(TEXT_GRAY)
    c.setDash(2, 2)
    c.line(left_margin, y, SIDEBAR_W - left_margin, y)
    c.setDash()
    y -= 12

    c.setFont("Helvetica", 8.3)
    coord = data["coordonnees"]
    for line in wrap_text(c, coord["adresse"], "Helvetica", 8.3, sidebar_text_w):
        c.drawString(left_margin, y, line)
        y -= 11
    y -= 3
    c.drawString(left_margin, y, coord["tel"])
    y -= 11
    for line in wrap_text(c, coord["email"], "Helvetica", 8.3, sidebar_text_w):
        c.drawString(left_margin, y, line)
        y -= 11

    y -= 14
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(left_margin, y, "LANGUES")
    y -= 5
    c.setStrokeColor(TEXT_GRAY)
    c.setDash(2, 2)
    c.line(left_margin, y, SIDEBAR_W - left_margin, y)
    c.setDash()
    y -= 14

    bar_w = sidebar_text_w
    bar_h = 3.6
    seg_gap = 1.4
    n_seg = len(NIVEAUX_ORDRE)
    seg_w = (bar_w - seg_gap * (n_seg - 1)) / n_seg

    for lang in data["langues"]:
        niveau = lang.get("niveau", "B1")
        filled = NIVEAUX_ORDRE.index(niveau) + 1 if niveau in NIVEAUX_ORDRE else 3

        c.setFont("Helvetica-Bold", 8.6)
        c.setFillColor(TEXT_DARK)
        c.drawString(left_margin, y, lang["langue"])
        c.setFont("Helvetica", 7.6)
        c.setFillColor(TEXT_GRAY)
        c.drawRightString(SIDEBAR_W - left_margin, y, niveau)
        y -= 8

        for i in range(n_seg):
            seg_x = left_margin + i * (seg_w + seg_gap)
            c.setFillColor(SIDEBAR_DARK if i < filled else HexColor("#C7C7C7"))
            c.rect(seg_x, y - bar_h, seg_w, bar_h, fill=1, stroke=0)
        y -= 16

    # ---------- Main column ----------
    mx = SIDEBAR_W + 10 * mm
    main_w = PAGE_W - mx - 12 * mm
    y = PAGE_H - 18 * mm

    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(mx, y, data["nom"])
    y -= 15
    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT_GRAY)
    c.drawString(mx, y, data["titre"])
    y -= 22

    # Profil
    y = section_header(c, mx, y, "Profil professionnel")
    y -= 4
    c.setFont("Helvetica", 9.2)
    c.setFillColor(TEXT_DARK)
    for line in wrap_text(c, data["profil"], "Helvetica", 9.2, main_w - 4):
        c.drawString(mx + 4, y, line)
        y -= 12.5
    y -= 14

    # Compétences (2 colonnes)
    y = section_header(c, mx, y, "Compétences")
    y -= 4
    col_w = (main_w - 4) / 2
    half = (len(data["competences"]) + 1) // 2
    left_items, right_items = data["competences"][:half], data["competences"][half:]
    y_before = y
    y_left = bullet_list(c, mx + 4, y, left_items, col_w)
    y_right = bullet_list(c, mx + 4 + col_w, y_before, right_items, col_w)
    y = min(y_left, y_right) - 10

    # Parcours professionnel
    y = section_header(c, mx, y, "Parcours professionnel")
    y -= 4
    for exp in data["parcours"]:
        c.setFont("Helvetica-Bold", 9.4)
        c.setFillColor(TEXT_DARK)
        c.drawString(mx + 4, y, exp["poste"])
        y -= 12
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_GRAY)
        c.drawString(mx + 4, y, exp["structure"])
        y -= 13
        y = bullet_list(c, mx + 4, y, exp["taches"], main_w - 4)
    y -= 8

    # Formation
    y = section_header(c, mx, y, "Formation")
    y -= 4
    for f in data["formation"]:
        c.setFont("Helvetica-Bold", 9.4)
        c.setFillColor(TEXT_DARK)
        c.drawString(mx + 4, y, f["diplome"])
        y -= 12
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_GRAY)
        for line in wrap_text(c, f["detail"], "Helvetica", 9, main_w - 4):
            c.drawString(mx + 4, y, line)
            y -= 12
        y -= 6

    # Projets réalisés
    if data.get("projets"):
        y = section_header(c, mx, y, "Projets réalisés")
        y -= 4
        for p in data["projets"]:
            item = f"{p['titre']} — {p['description']}" if p.get("description") else p["titre"]
            y = bullet_list(c, mx + 4, y, [item], main_w - 4)
        y -= 6

    # Personnalisé (centres d'intérêt)
    y = section_header(c, mx, y, "Personnalisé")
    y -= 4
    y = bullet_list(c, mx + 4, y, data["personnalise"], main_w - 4)

    # ---------- Filigrane (aperçu avant paiement) ----------
    if watermark:
        c.saveState()
        try:
            c.setFillAlpha(0.14)
        except Exception:
            pass
        c.setFillColor(HexColor("#1B1B1B"))
        c.setFont("Helvetica-Bold", 44)
        c.translate(PAGE_W / 2, PAGE_H / 2)
        c.rotate(35)
        c.drawCentredString(0, 40, "APERÇU")
        c.drawCentredString(0, -40, "ESCO-CV.sn")
        c.restoreState()

    c.showPage()
    c.save()


if __name__ == "__main__":
    build_pdf(CV_DATA, "/mnt/user-data/outputs/Pape_Lo_CV.pdf")
    print("OK")
    