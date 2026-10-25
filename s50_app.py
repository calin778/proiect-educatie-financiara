from fastapi import Depends, FastAPI, HTTPException

import s50_model
import s50_rag
from s50_model import get_db, init_db
from s50_schema import Categorie, LectieIn, ChatIn, ChatOut
from s50_agent import ruleaza_agent


# La pornire: tabela + lectiile initiale in MySQL, apoi indexul RAG
# umplut cu TOATE lectiile din MySQL (vezi s50_rag.py).
init_db()
with s50_model.SessionLocal() as s:
    s50_rag.indexeaza_toate(s50_model.toate_lectiile(s))

app = FastAPI(title="Educatie financiara personala", version="1.0.0 (s50, RAG)")


def lectie_dict(l):
    return {"id": l.id, "titlu": l.titlu, "categorie": l.categorie,
            "continut": l.continut, "data": l.data.isoformat()}


# #############################################################
# PARTEA 1 - LECTII  (plan: 5.1)
# #############################################################
# Regula proiectului: orice modificare in MySQL se face si in Chroma.


# TODO 5.1a: GET /lectii?categorie= - lista lectiilor
#   1. categorie_text = None; daca categorie nu e None -> categorie.value
#   2. return o LISTA DE DICTIONARE: lectie_dict(l) pentru fiecare lectie din
#      s50_model.toate_lectiile(db, categorie_text)
@app.get("/lectii")
def lista_lectii(categorie: Categorie | None = None, db=Depends(get_db)):
    categorie_text = categorie.value if categorie is not None else None
    lectii = s50_model.toate_lectiile(db, categorie_text)
    return [lectie_dict(l) for l in lectii]


# TODO 5.1b: POST /lectii - adauga o lectie
#   1. Titlu duplicat? s50_model.gaseste_lectie_dupa_titlu(db, data.titlu)
#      gaseste ceva -> HTTPException(400, "lectia '...' exista deja")
#   2. l = s50_model.adauga_lectie(db, data.titlu, data.categorie.value, data.continut)
#   3. s50_rag.indexeaza_lectie(l)   <- lectia devine cautabila
#   4. return lectie_dict(l)
@app.post("/lectii", status_code=201)
def adauga_lectie(data: LectieIn, db=Depends(get_db)):
    if s50_model.gaseste_lectie_dupa_titlu(db, data.titlu):
        raise HTTPException(status_code=400, detail=f"lectia '{data.titlu}' exista deja")

    l = s50_model.adauga_lectie(db, data.titlu, data.categorie.value, data.continut)
    s50_rag.indexeaza_lectie(l)
    return lectie_dict(l)


# TODO 5.1c: DELETE /lectii/{lectie_id} - sterge o lectie
#   1. s50_model.sterge_lectie(db, lectie_id) -> False -> HTTPException(404, ...)
#   2. s50_rag.sterge_din_index(lectie_id)   <- dispare si din cautare
#   3. return {"sters": lectie_id}
@app.delete("/lectii/{lectie_id}")
def sterge_lectie(lectie_id: int, db=Depends(get_db)):
    sters = s50_model.sterge_lectie(db, lectie_id)
    if not sters:
        raise HTTPException(status_code=404, detail=f"Lectia cu id-ul {lectie_id} nu a fost gasita")

    s50_rag.sterge_din_index(lectie_id)
    return {"sters": lectie_id}


# #############################################################
# PARTEA 2 - CAUTARE  (plan: 5.2)
# #############################################################


# TODO 5.2: GET /cauta?intrebare=...&n=2 - doar cautarea, FARA model
#   1. Daca n < 1 sau n > 5 -> HTTPException(400, "n trebuie sa fie intre 1 si 5")
#   2. return s50_rag.cauta(intrebare, n)
@app.get("/cauta")
def cauta(intrebare: str, n: int = 2):
    if n < 1 or n > 5:
        raise HTTPException(status_code=400, detail="n trebuie sa fie intre 1 si 5")
    return s50_rag.cauta(intrebare, n_rezultate=n)


# #############################################################
# PARTEA 3 - /chat: PROFESORUL  (plan: 5.3 - dupa Pasul 4)
# #############################################################


# TODO 5.3: POST /chat - ca la s49
#   1. istoric = lista cu m.model_dump() pentru fiecare m din data.istoric
#   2. try: raspuns, apeluri = ruleaza_agent(data.mesaj, istoric)
#      except Exception as e: HTTPException(502, f"Eroare la modelul AI: {e}")
#   3. return ChatOut(raspuns=raspuns, apeluri=apeluri)
@app.post("/chat", response_model=ChatOut)
def chat(data: ChatIn):
    istoric = [m.model_dump() for m in data.istoric]
    try:
        raspuns, apeluri = ruleaza_agent(data.mesaj, istoric)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Eroare la modelul AI: {e}")
    return ChatOut(raspuns=raspuns, apeluri=apeluri)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)