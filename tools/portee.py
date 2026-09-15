# -*- coding: utf-8 -*-
"""Le périmètre de Driver360 — UN SEUL interrupteur pour tout le site.

DÉCISION DU 15/09/2026 (l'utilisateur, la veille de la rencontre avec Ryan
Rappoport, Amazon DSP DA Services Partner) :

  « Pour le moment, Driver360 sera mis en œuvre SEULEMENT pour les DSP
    d'Amazon. Mettez en pause les postes qui concernent les autres types de
    chauffeurs. Orientez le coach vers l'amélioration de la carrière des
    chauffeurs. »

  Précisé dans la foulée : « Le site fera toujours le Driver Pool (DSP
  ready), le portail des DSP employeurs et le coach driver. »

POURQUOI UN MODULE PLUTÔT QUE DES SUPPRESSIONS
----------------------------------------------
« En pause » veut dire en pause. Les 19 employeurs hors DSP, le 7D Pro, les
exercices du test de route : tout reste dans le code, vérifié, daté, prêt à
revenir. Supprimer aurait détruit des semaines de vérification pour une
décision que l'utilisateur a lui-même qualifiée de provisoire (« pour le
moment »).

Et un seul interrupteur, parce qu'un périmètre éparpillé dans six fichiers se
défait mal : on rallume la page des offres et on oublie le menu, ou
l'inverse. Ici, `PORTEE = "tous"` rétablit tout d'un coup.

⚠️ CE QUE CE MODULE NE DÉCIDE PAS : le contenu de la présentation à Ryan
(Driver360_Professional_Continuity_Ryan.pptx) décrit un dossier portable, une
pause et un retour, un échange d'expérience modéré. **Rien de cela n'est
construit.** Le site ne doit pas le laisser croire — la présentation elle-même
le classe en « proposed development ».
"""

# "dsp"  : Amazon Delivery Service Partners uniquement (décidé le 15/09/2026)
# "tous" : le périmètre d'avant — tout le Massachusetts, sept types de postes
PORTEE = "dsp"


def dsp():
    return PORTEE == "dsp"


# ---- Page des offres : les sections qui s'affichent -------------------------
# Les autres ne sont PAS supprimées d'`emplois.py` : elles ne sont pas rendues.
SECTIONS_DSP = {"dsp"}


def section_active(genre):
    return (not dsp()) or genre in SECTIONS_DSP


# ---- Les pages mises en pause -----------------------------------------------
# 7D Pro prépare au certificat de transport d'écoliers : hors du périmètre DSP.
# La page reste construite et joignable — un inscrit qui a un code SETD- ne
# doit pas tomber sur une erreur — mais elle ne figure plus dans aucun menu,
# aucun plan de site, et elle demande aux moteurs de ne pas l'indexer.
PAGES_EN_PAUSE = {"setdi.html"} if PORTEE == "dsp" else set()


def en_pause(page):
    return page in PAGES_EN_PAUSE
