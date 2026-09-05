# -*- coding: utf-8 -*-
"""Protège la promesse de la caméra — avant toute mesure.

    python tools/verif_camera.py     échoue si la promesse n'est plus tenue

POURQUOI CE FICHIER EXISTE
--------------------------
`wout.html` ouvre la caméra du visiteur, et la page lui promet deux choses :

  1. **la vidéo ne quitte pas l'appareil** ;
  2. **on ne la note pas** — ni le visage, ni la posture, ni la « confiance ».

La première est une promesse technique : un jour, quelqu'un ajoutera « juste
un envoi pour analyser », et la page continuera d'afficher la phrase. La
seconde est une promesse morale, et c'est la plus facile à trahir sans le
vouloir : noter le « contact visuel » paraît utile, et personne ne remarquera
que ça revient à mesurer l'écart d'un immigrant à une norme américaine.

Un contrôle automatique est le seul moyen de faire tenir une promesse qui
survit à celui qui l'a faite.

CE QU'IL VÉRIFIE
  · aucun envoi ne transporte le blob, le flux ou l'élément vidéo ;
  · aucune trace de notation du visage, de la posture ou de la confiance ;
  · la promesse est écrite dans les quatre langues, pas seulement en français ;
  · le flux est bien coupé quand on quitte la page.

⚠️ CE CONTRÔLE A ÉTÉ PROUVÉ PAR LA PANNE : on injecte la fuite, il tombe ; on
la retire, il passe. Un contrôle qu'on n'a jamais vu échouer ne prouve rien.
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "wout.html"

# Les noms que porte la vidéo dans ce fichier. Si l'un d'eux entre dans un
# envoi, la promesse est rompue.
VIDEO = r"(?:blob|morceaux|chunks|url|flux|stream|cam-?video|recorded)"
ENVOI = re.compile(
    r"(?:fetch|sendBeacon|XMLHttpRequest|\.send|new\s+WebSocket|FormData)"
    r"[^;\n]{0,160}" + VIDEO, re.I)

# La notation qu'on refuse. `posture` et `confidence` en toutes lettres, plus
# les API qui ne servent qu'à ça.
NOTATION = re.compile(
    r"FaceDetector|FaceMesh|faceapi|face-api|BlazeFace|"
    r"eye\s*contact|eyeContact|posture(?:Score|Rating)|"
    r"confidence(?:Score|Rating)|scorePosture|scoreFace", re.I)

# La promesse, dans les quatre langues.
PROMESSE = [
    ("fr", "pas un jury"),
    ("ht", "pa yon jiri"),
    ("en", "not a jury"),
    ("es", "no un jurado"),
]


def main():
    p = os.path.join(RACINE, PAGE)
    if not os.path.exists(p):
        print("     %s introuvable" % PAGE)
        return 1
    s = io.open(p, encoding="utf-8").read()

    if "getUserMedia" not in s:
        print("     Camera : la page n'ouvre pas la camera — rien a proteger.")
        return 0

    fautes = []

    m = ENVOI.search(s)
    if m:
        fautes.append("un envoi transporte la video : « %s »"
                      % " ".join(m.group(0).split())[:90])

    m = NOTATION.search(s)
    if m:
        fautes.append("notation du visage / de la posture / de la confiance : « %s »"
                      % m.group(0))

    manque = [lg for lg, mot in PROMESSE if mot not in s]
    if manque:
        fautes.append("la promesse n'est pas ecrite en : %s" % " ".join(manque))

    if "pagehide" not in s or "getTracks" not in s:
        fautes.append("le flux n'est pas coupe en quittant la page "
                      "(une diode qui reste allumee est une promesse trahie)")

    if fautes:
        print("     Camera : %d manquement(s) a la promesse" % len(fautes))
        for f in fautes:
            print("       - %s" % f)
        return 1

    print("     Camera : la video ne part pas, rien n'est note, "
          "la promesse est ecrite en 4 langues.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
