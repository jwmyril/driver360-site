# -*- coding: utf-8 -*-
"""
Fabrique le logo Driver360 et toutes ses déclinaisons.

    python tools/gen_logo.py            écrit les fichiers
    python tools/gen_logo.py --apercu   écrit en plus un aperçu 512 px

D'OÙ VIENT CE DESSIN
--------------------
Il dérive du logo **actuel** d'Atmart (`atmart-logo-transparent.png`) : une
boucle-ruban qui part d'un sombre profond, se déploie vers la droite et se
divise en filaments terminés par des points, sur un dégradé sombre → turquoise.

⚠️ PREMIÈRE VERSION JETÉE. J'avais dérivé d'`atmart-mark-site.svg` (cercle +
lettre A, juillet), que l'utilisateur a écarté : ce n'est plus la marque de la
maison. La leçon vaut d'être écrite — quand plusieurs logos cohabitent dans un
dossier, le plus récent n'est pas celui dont le nom est le plus évident.
Regarder les dates, et demander plutôt que supposer.

CE QUI EST REPRIS, ET CE QUI CHANGE
  · LA BOUCLE — reprise. Chez Atmart elle dit l'infini ; ici elle dit le nom :
    une boucle fermée, c'est 360°. Même geste, donc famille reconnaissable.
  · LES FILAMENTS À POINTS — repris. Chez Atmart ce sont des flux de données ;
    pour un produit de conduite ils se lisent comme des trajets qui partent
    vers leurs destinations.
  · LE DÉGRADÉ sombre → turquoise — repris, mais il aboutit au turquoise du
    site Driver360 (#2ec4b6) plutôt qu'au bleu d'Atmart. Seule liberté prise,
    et elle raccorde la marque à ses pages.

POURQUOI C'EST DESSINÉ EN PYTHON
--------------------------------
Aucun convertisseur SVG→PNG n'est installé (ni cairosvg ni cairocffi —
vérifié), et le dessin a un dégradé : le rendre à la main dans Pillow donne un
contrôle exact à chaque taille sans ajouter de dépendance. On rend à 4× puis on
réduit en Lanczos. Le SVG est écrit à côté comme source vectorielle.
"""
import io
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARQUE = os.path.join(RACINE, "assets", "brand")

SOMBRE = (17, 45, 66)        # #112d42
TURQUOISE = (46, 196, 182)   # #2ec4b6 — l'accent de Driver360

U = 120.0                    # repère de dessin, comme les autres marques

# --- géométrie ------------------------------------------------------------
# LA BOUCLE. Anneau elliptique dont l'intérieur est décalé vers le bas-gauche :
# l'épaisseur croît vers le haut-droite, là où le ruban s'échappe. C'est ce
# décalage qui donne le mouvement — un anneau d'épaisseur constante ferait un
# beignet, pas un ruban.
EXT = (6.0, 30.0, 64.0, 88.0)      # boîte du bord extérieur
INT = (12.0, 40.0, 55.0, 83.0)     # boîte du bord intérieur

# Le ruban part du bord EXTÉRIEUR de la boucle et s'affine jusqu'à une pointe.
# ⚠️ Ses deux attaches doivent être SUR cet arc. La première version refermait
# le polygone en ligne droite : elle traversait le vide central et y laissait
# une encoche en coin, bien visible.
ATTACHE_HAUT = -128.0               # degrés, sur l'ellipse extérieure
ATTACHE_BAS = -6.0
POINTE = (80.0, 51.0)

# Les filaments partent de la pointe et s'ouvrent en éventail.
# (fin_x, fin_y, tirage) — le tirage courbe plus ou moins le trait.
FILAMENTS = [
    (112, 31, -11), (117, 42, -8), (116, 53, -3),
    (112, 63, 1), (115, 74, -2), (104, 73, 5), (101, 84, 7),
]


def bezier(pts, n=90):
    """Échantillonne une Bézier cubique (4 points) ou quadratique (3)."""
    out = []
    for i in range(n + 1):
        t = i / float(n)
        u = 1 - t
        if len(pts) == 4:
            p0, p1, p2, p3 = pts
            x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
            y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        else:
            p0, p1, p2 = pts
            x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
            y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        out.append((x, y))
    return out


def arc_ext(a0, a1, n=48):
    """Points de l'ellipse extérieure entre deux angles, en degrés."""
    cx, cy = (EXT[0] + EXT[2]) / 2.0, (EXT[1] + EXT[3]) / 2.0
    rx, ry = (EXT[2] - EXT[0]) / 2.0, (EXT[3] - EXT[1]) / 2.0
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / float(n))),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / float(n))))
            for i in range(n + 1)]


def point_ext(a):
    """Un seul point de l'ellipse exterieure, a l'angle donne."""
    cx, cy = (EXT[0] + EXT[2]) / 2.0, (EXT[1] + EXT[3]) / 2.0
    rx, ry = (EXT[2] - EXT[0]) / 2.0, (EXT[3] - EXT[1]) / 2.0
    return (cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))


def degrade(n):
    """Dégradé horizontal, sombre à gauche, turquoise à droite.

    La transition suit une courbe douce plutôt qu'une droite : le turquoise
    doit dominer la moitié droite, comme chez Atmart, sinon la marque paraît
    terne aux petites tailles.
    """
    g = Image.new("RGB", (n, 1))
    px = g.load()
    for x in range(n):
        t = (x / float(n - 1)) ** 0.72
        px[x, 0] = tuple(int(round(SOMBRE[i] + (TURQUOISE[i] - SOMBRE[i]) * t))
                         for i in range(3))
    return g.resize((n, n))


def dessiner(taille, fond=None):
    SUR = 4
    n = int(taille * SUR)
    k = n / U
    masque = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(masque)
    E = lambda x, y: (x * k, y * k)

    # 1. la boucle, pleine
    d.ellipse([EXT[0] * k, EXT[1] * k, EXT[2] * k, EXT[3] * k], fill=255)

    # 2. le ruban, refermé le long de l'arc extérieur
    h0, b0 = point_ext(ATTACHE_HAUT), point_ext(ATTACHE_BAS)
    contour = (bezier([h0, (34, 19), (62, 25), POINTE])
               + bezier([POINTE, (74, 51), (69, 53), b0])
               + arc_ext(ATTACHE_BAS, ATTACHE_HAUT))
    d.polygon([E(x, y) for x, y in contour], fill=255)

    # 3. le vide central, évidé EN DERNIER pour rester net
    d.ellipse([INT[0] * k, INT[1] * k, INT[2] * k, INT[3] * k], fill=0)

    # 4. les filaments.
    #    ⚠️ EN DESSOUS DE 64 px ON EN GARDE QUATRE, plus epais. A 32 px les
    #    sept traits d'origine se rejoignaient en une bouillie : un logo doit
    #    survivre a sa plus PETITE taille, c'est la qu'on le voit le plus
    #    souvent (onglet, ecran d'accueil, liste d'applications).
    petit = taille < 64
    fils = FILAMENTS[0::2] if petit else FILAMENTS
    ep = max(1, int(round((2.6 if petit else 1.7) * k)))
    for fx, fy, tir in fils:
        mx, my = (POINTE[0] + fx) / 2.0, (POINTE[1] + fy) / 2.0 + tir
        d.line([E(x, y) for x, y in bezier([POINTE, (mx, my), (fx, fy)])],
               fill=255, width=ep, joint="curve")
        r = (3.6 if petit else 2.8) * k
        d.ellipse([fx * k - r, fy * k - r, fx * k + r, fy * k + r], fill=255)

    # Un dixième de pixel de flou avant réduction : les traits fins gardent
    # leur densité au lieu de se hacher.
    masque = masque.filter(ImageFilter.GaussianBlur(k * 0.10))

    img = Image.composite(degrade(n).convert("RGBA"),
                          Image.new("RGBA", (n, n), (0, 0, 0, 0)), masque)
    if fond:
        img = Image.alpha_composite(Image.new("RGBA", (n, n), fond), img)
    return img.resize((taille, taille), Image.LANCZOS)


def svg():
    fils = []
    for fx, fy, tir in FILAMENTS:
        mx, my = (POINTE[0] + fx) / 2.0, (POINTE[1] + fy) / 2.0 + tir
        fils.append('  <path d="M%g %g Q%g %g %g %g" fill="none" stroke="url(#g)" '
                    'stroke-width="1.7" stroke-linecap="round"/>\n'
                    '  <circle cx="%g" cy="%g" r="2.8" fill="url(#g)"/>'
                    % (POINTE[0], POINTE[1], mx, my, fx, fy, fx, fy))
    cx, cy = (EXT[0] + EXT[2]) / 2.0, (EXT[1] + EXT[3]) / 2.0
    rx, ry = (EXT[2] - EXT[0]) / 2.0, (EXT[3] - EXT[1]) / 2.0
    icx, icy = (INT[0] + INT[2]) / 2.0, (INT[1] + INT[3]) / 2.0
    irx, iry = (INT[2] - INT[0]) / 2.0, (INT[3] - INT[1]) / 2.0
    h = (cx + rx * math.cos(math.radians(ATTACHE_HAUT)),
         cy + ry * math.sin(math.radians(ATTACHE_HAUT)))
    b = (cx + rx * math.cos(math.radians(ATTACHE_BAS)),
         cy + ry * math.sin(math.radians(ATTACHE_BAS)))
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" role="img" aria-label="Driver360">
  <!-- Marque Driver360 — derivee du logo actuel d'Atmart : la boucle-ruban qui
       se deploie en filaments. Ici la boucle porte le sens du nom : 360 degres.
       Le degrade aboutit au turquoise du site (#2ec4b6). -->
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#112d42"/>
      <stop offset="0.55" stop-color="#1c8a93"/>
      <stop offset="1" stop-color="#2ec4b6"/>
    </linearGradient>
  </defs>
  <path fill="url(#g)" fill-rule="evenodd"
        d="M%(cx)g %(t)g A%(rx)g %(ry)g 0 1 0 %(cx)g %(b)g A%(rx)g %(ry)g 0 1 0 %(cx)g %(t)g Z
           M%(icx)g %(it)g A%(irx)g %(iry)g 0 1 1 %(icx)g %(ib)g A%(irx)g %(iry)g 0 1 1 %(icx)g %(it)g Z"/>
  <path fill="url(#g)" d="M%(hx)g %(hy)g C34 19 62 25 %(px)g %(py)g C74 51 69 53 %(bx)g %(by)g Z"/>
%(fils)s
</svg>
""" % dict(cx=cx, t=EXT[1], b=EXT[3], rx=rx, ry=ry,
           icx=icx, it=INT[1], ib=INT[3], irx=irx, iry=iry,
           hx=h[0], hy=h[1], bx=b[0], by=b[1], px=POINTE[0], py=POINTE[1],
           fils="\n".join(fils))



# --------------------------------------------------------------------------
# L'image de partage.
#
# ⚠️ SANS ELLE, OPEN GRAPH NE SERT A RIEN. Le canal du produit est WhatsApp :
# un lien colle dans une conversation s'affiche en texte nu tant que la page
# n'annonce pas de vignette — et le plus grand fichier de la marque faisait
# 512 px carre, c'est-a-dire une icone d'application, pas une vignette.
#
# 1200 x 630 est le format que lisent WhatsApp, Facebook et LinkedIn. On la
# dessine ICI plutot que de la deposer a la main : elle suit la marque, et le
# jour ou le logo change, elle change avec lui.
CARTE = (1200, 630)


def police(px, gras=True):
    """Une police du systeme, ou celle de PIL si la machine n'en a aucune."""
    for nom in (("segoeuib.ttf", "arialbd.ttf") if gras
                else ("segoeui.ttf", "arial.ttf")):
        for base in (r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu"):
            p = os.path.join(base, nom)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, px)
                except Exception:
                    pass
    return ImageFont.load_default()


def carte_sociale():
    im = Image.new("RGBA", CARTE, (14, 34, 64, 255))
    d = ImageDraw.Draw(im)

    # une bande d'accent en bas : elle donne le ton meme en miniature
    d.rectangle([0, CARTE[1] - 10, CARTE[0], CARTE[1]], fill=(46, 196, 182, 255))

    marque = dessiner(360)
    im.alpha_composite(marque, (96, (CARTE[1] - 360) // 2 - 10))

    x = 96 + 360 + 64
    d.text((x, 214), "Driver360", font=police(92), fill=(255, 255, 255, 255))
    d.text((x, 322), "Driving jobs in Massachusetts",
           font=police(38, False), fill=(200, 216, 232, 255))
    d.text((x, 378), "Class D \u00b7 7D \u00b7 CDL \u2014 free driver pool",
           font=police(34, False), fill=(46, 196, 182, 255))
    return im.convert("RGB")

def main():
    with io.open(os.path.join(MARQUE, "driver360-mark.svg"), "w",
                 encoding="utf-8", newline="\n") as f:
        f.write(svg())

    for nom, taille, fond in [
        ("logo-32.png", 32, None),
        ("logo-dark-96.png", 96, None),
        ("icon-192.png", 192, None),
        ("icon-512.png", 512, None),
        # iOS refuse la transparence : sans fond, le systeme la remplit de noir.
        ("apple-touch-icon.png", 180, (14, 34, 64, 255)),
    ]:
        dessiner(taille, fond).save(os.path.join(MARQUE, nom), "PNG", optimize=True)
        print("  %-24s %d px" % (nom, taille))

    carte_sociale().save(os.path.join(MARQUE, "share-1200x630.jpg"),
                         "JPEG", quality=86, optimize=True)
    print("  %-24s 1200x630" % "share-1200x630.jpg")

    dessiner(64).save(os.path.join(MARQUE, "favicon.ico"),
                      sizes=[(16, 16), (32, 32), (48, 48)])
    print("  %-24s 16/32/48" % "favicon.ico")

    if "--apercu" in sys.argv:
        ap = os.path.join(os.environ.get("TEMP", "."), "driver360-apercu.png")
        Image.alpha_composite(Image.new("RGBA", (512, 512), (14, 34, 64, 255)),
                              dessiner(512)).save(ap)
        print("  apercu : %s" % ap)


if __name__ == "__main__":
    main()
