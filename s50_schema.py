from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

# Fisierul asta contine REGULILE pentru datele care vin din exterior:
# din formularele Streamlit (prin s50_app.py). Pydantic verifica fiecare
# camp; daca o regula nu e respectata, FastAPI raspunde singur cu 422.


# #############################################################
# PARTEA 1 - LECTIE  (plan: 2.1)
# #############################################################


# TODO 2.1a: clasa Categorie(str, Enum) - categoriile permise
#       BUGET      = "Buget"
#       ECONOMII   = "Economii"
#       CREDITE    = "Credite"
#       INVESTITII = "Investitii"
#       PENSIE     = "Pensie"
#       ALTELE     = "Altele"
class Categorie(str, Enum):
    BUGET = "Buget"
    ECONOMII = "Economii"
    CREDITE = "Credite"
    INVESTITII = "Investitii"
    PENSIE = "Pensie"
    ALTELE = "Altele"


# TODO 2.1b: clasa LectieIn(BaseModel) - o lectie NOUA (POST /lectii)
#   Nu are id si nici data - le pun MySQL si s50_model.
#
#   camp        tip         regula (cu Field)
#   titlu       str         min_length=3, max_length=200
#   categorie   Categorie   (enum-ul de la 2.1a, fara Field)
#   continut    str         min_length=50
#
#   Exemple:
#     LectieIn(titlu="Asigurarea locuintei", categorie="Altele", continut="...50+ caractere...")
#         -> OK
#     LectieIn(titlu="Asigurarea locuintei", categorie="Asigurari", continut="...")
#         -> ValidationError: "Asigurari" nu e o categorie permisa
class LectieIn(BaseModel):
    titlu: str = Field(min_length=3, max_length=200)
    categorie: Categorie
    continut: str = Field(min_length=50)


# #############################################################
# PARTEA 2 - CHAT CU PROFESORUL  (plan: 2.2)
# #############################################################
# Identic cu s49: serverul NU tine minte conversatia - Streamlit trimite
# de fiecare data tot istoricul.
#
#   cerere:   {"mesaj": "Ce este DAE?", "istoric": [...]}
#   raspuns:  {"raspuns": "DAE este costul total al unui credit...",
#              "apeluri": [{"tool": "cauta_in_lectii",
#                           "rezultat": "[Creditele: DAE, ...]\n..."}]}


# TODO 2.2a: clasa MesajChat(BaseModel)
#   role      Literal["user", "assistant"]
#   content   str
class MesajChat(BaseModel):
    role: Literal["user", "assistant"]
    content: str


# TODO 2.2b: clasa ChatIn(BaseModel)
#   mesaj     str               Field(min_length=1)
#   istoric   list[MesajChat]   implicit lista goala: = []
class ChatIn(BaseModel):
    mesaj: str = Field(min_length=1)
    istoric: list[MesajChat] = Field(default_factory=list)


# TODO 2.2c: clasa ApelTool(BaseModel) - UN tool apelat de agent
#   tool       str   - numele tool-ului, ex: "cauta_in_lectii"
#   rezultat   str   - ce a gasit tool-ul (lectiile = sursele raspunsului)
class ApelTool(BaseModel):
    tool: str
    rezultat: str


# TODO 2.2d: clasa ChatOut(BaseModel)
#   raspuns   str
#   apeluri   list[ApelTool]
class ChatOut(BaseModel):
    raspuns: str
    apeluri: list[ApelTool] = Field(default_factory=list)
