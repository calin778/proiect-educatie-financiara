import os
from datetime import date
from typing import Optional
from sqlalchemy import create_engine, String, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


# #############################################################
# PARTEA 0 - CONEXIUNEA LA MySQL  (plan: 1.1)
# #############################################################
# Aceeasi conexiune ca la s49. Schimbati userul si parola cu ale voastre.

user = 'root'
password = 'admin'
engine = create_engine(f"mysql+pymysql://{user}:{password}@localhost:3306/curs")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# #############################################################
# PARTEA 1 - MODELUL: Lectie  (plan: 1.2)
# #############################################################
# O singura tabela: lectiile de educatie financiara. MySQL este SURSA DE
# ADEVAR - aici stau lectiile, intregi. Chroma (s50_rag.py) este doar un
# INDEX pentru cautarea dupa sens si se umple din MySQL la fiecare pornire.


# TODO 1.2: clasa Lectie (mosteneste Base)
#   O lectie = un subiect de finante personale, ex: "Fondul de urgenta".
#
#   1. __tablename__ = "s50_lectie"
#   2. coloanele:
#        id         int    cheie primara, autoincrement=True
#        titlu      str    String(200), unique=True
#        categorie  str    String(30)   ex: "Buget", "Credite"
#        continut   str    mapped_column(Text)  - o lectie are mii de caractere
#        data       date   (fara mapped_column - ajunge Mapped[date])
#   3. metoda __str__(self) - textul afisat cand faci print(lectie):
#          Lectie #3: Fondul de urgenta (Economii, 1720 caractere)

class Lectie(Base):
    __tablename__ = "s50_lectie"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titlu: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    categorie: Mapped[str] = mapped_column(String(30), nullable=False)
    continut: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[date] = mapped_column(default=date.today)

    def __str__(self) -> str:
        return f"Lectie #{self.id}: {self.titlu} ({self.categorie}, {len(self.continut)} caractere)"


# #############################################################
# PARTEA 1b - PORNIREA BAZEI DE DATE  (plan: 1.3)
# #############################################################


def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


# Lectiile initiale sunt fisierele din folderul lectii_initiale/.
# Prima linie a fiecarui fisier este titlul; restul este continutul.
FOLDER_LECTII_INITIALE = "lectii_initiale"

CATEGORIE_PE_FISIER = {
    "buget_personal.txt":   "Buget",
    "fond_de_urgenta.txt":  "Economii",
    "dobanda_compusa.txt":  "Economii",
    "inflatia.txt":         "Economii",
    "credite_dae.txt":      "Credite",
    "card_de_credit.txt":   "Credite",
    "investitii_etf.txt":   "Investitii",
    "pensii_piloni.txt":    "Pensie",
}


def adauga_date_initiale(s):
    if s.scalars(select(Lectie)).all():
        return

    for nume_fisier in sorted(os.listdir(FOLDER_LECTII_INITIALE)):
        cale = os.path.join(FOLDER_LECTII_INITIALE, nume_fisier)
        with open(cale, encoding="utf-8") as f:
            text = f.read()

        prima_linie, rest = text.split("\n", 1)
        categorie = CATEGORIE_PE_FISIER.get(nume_fisier, "Altele")
        s.add(Lectie(titlu=prima_linie.strip(), categorie=categorie,
                     continut=rest.strip(), data=date.today()))
    s.commit()


def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        adauga_date_initiale(s)


# #############################################################
# PARTEA 2 - CRUD Lectie  (plan: 1.4)
# #############################################################


# TODO 1.4a: adauga_lectie(s, titlu, categorie, continut)
#   1. l = Lectie(titlu=..., categorie=..., continut=..., data=date.today())
#   2. s.add(l), s.commit()
#   3. return l      -> obiectul, acum cu id
def adauga_lectie(s, titlu: str, categorie: str, continut: str) -> Lectie:
    lectie = Lectie(titlu=titlu, categorie=categorie, continut=continut, data=date.today())
    s.add(lectie)
    s.commit()
    s.refresh(lectie)
    return lectie


# TODO 1.4b: toate_lectiile(s, categorie=None)
#   Intoarce LISTA lectiilor, ordonate alfabetic dupa titlu.
#   Filtrul categorie e optional: daca e None, nu se aplica.
#
#   1. query = select(Lectie)
#   2. if categorie: query = query.where(Lectie.categorie == categorie)
#   3. query = query.order_by(Lectie.titlu)
#   4. return s.scalars(query).all()
def toate_lectiile(s, categorie: Optional[str] = None) -> list[Lectie]:
    query = select(Lectie)
    if categorie:
        query = query.where(Lectie.categorie == categorie)
    query = query.order_by(Lectie.titlu)
    return list(s.scalars(query).all())


# TODO 1.4c: gaseste_lectie_dupa_titlu(s, titlu)
#   Intoarce lectia cu titlul dat, sau None.
#   Ruta POST /lectii o foloseste ca sa verifice titlul duplicat INAINTE
#   de salvare (coloana titlu e unique).
#   return s.scalar(select(Lectie).where(Lectie.titlu == titlu))
def gaseste_lectie_dupa_titlu(s, titlu: str) -> Optional[Lectie]:
    return s.scalar(select(Lectie).where(Lectie.titlu == titlu))

# TODO 1.4d: sterge_lectie(s, lectie_id)
#   Intoarce True daca a sters lectia, False daca nu exista.
#   1. l = s.get(Lectie, lectie_id)
#   2. daca l este None -> return False
#   3. altfel: s.delete(l), s.commit(), return True
def sterge_lectie(s, lectie_id: int) -> bool:
    lectie = s.get(Lectie, lectie_id)
    if lectie is None:
        return False
    s.delete(lectie)
    s.commit()
    return True

# #############################################################
# PARTEA 3 - get_db()
# #############################################################


def get_db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
