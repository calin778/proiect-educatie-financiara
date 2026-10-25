# Proiectul 2 — Educație financiară personală (plan de lucru)

Ce face aplicația și de ce: vezi **`document.md`**. Aici sunt pașii de implementare.

Structura este **identică cu proiectul de la sesiunea 49** (Asistentul cursului):
se schimbă doar tema — *notițe* devin *lecții*, *capitol* devine *categorie*.
Dacă vă blocați, comparați cu fișierul corespunzător din `session49/proiect/`.

| s49 — Asistentul cursului | s50 — Educație financiară |
|---|---|
| tabela `s49_notita` | tabela `s50_lectie` |
| `capitol` | `categorie` |
| tool-ul `cauta_in_notite` | tool-ul `cauta_in_lectii` |
| pagina Asistent AI | pagina Profesor AI |

## Cum lucrați

- În fiecare fișier găsiți comentarii `# TODO`. Numărul lor (ex: `TODO 3.1a`)
  este același cu cel din acest plan — citiți TODO-ul din cod, apoi scrieți
  funcția sub el.
- Ce **nu** are TODO este deja scris: citiți-l, îl folosiți mai departe.
- În paginile Streamlit, sub TODO-uri există linii marcate `# TEMPORAR`, ca
  pagina să pornească și înainte să scrieți soluția.

## Ordinea de lucru

```
s50_model.py   ← baza de date (tabela Lectie + funcțiile CRUD)
     ↓
s50_schema.py  ← validarea datelor
     ↓
s50_rag.py     ← Chroma: add + query + delete
     ↓
s50_agent.py   ← profesorul AI
     ↓
s50_app.py     ← rutele HTTP
     ↓
s50_ui.py + comun.py   ← scheletul interfeței (gata scrise)
     ↓
s50_pages/*.py ← paginile
```

## Setup (o singură dată)

```
pip install sqlalchemy pymysql fastapi uvicorn streamlit requests chromadb langchain langchain-openai
export OPENAI_API_KEY="sk-..."        # Windows: setx OPENAI_API_KEY "sk-..."
```

Cheia **nu** se scrie în cod. Toate comenzile se rulează din folderul proiectului.

---

## Pasul 1 — `s50_model.py` (baza de date)

**Gata scris:** conexiunea (schimbați userul și parola MySQL), `reset_db`,
`adauga_date_initiale` (citește cele 8 fișiere din `lectii_initiale/` — prima
linie e titlul), `init_db`, `get_db`.

- [ ] **TODO 1.2** `Lectie` → tabela `s50_lectie`: `id`, `titlu` (**unique**),
  `categorie`, `continut` (**`Text`**), `data`; plus `__str__`
- [ ] **TODO 1.4a** `adauga_lectie(s, titlu, categorie, continut)`
- [ ] **TODO 1.4b** `toate_lectiile(s, categorie=None)` → ordonate după titlu
- [ ] **TODO 1.4c** `gaseste_lectie_dupa_titlu(s, titlu)` → lecția sau `None`
- [ ] **TODO 1.4d** `sterge_lectie(s, id)` → `True` / `False`

**Test:**
```python
import s50_model
s50_model.init_db()
with s50_model.SessionLocal() as s:
    for l in s50_model.toate_lectiile(s):
        print(l)
```
Apar cele 8 lecții inițiale.

---

## Pasul 2 — `s50_schema.py` (validarea datelor)

- [ ] **TODO 2.1a** `Categorie(str, Enum)`: `Buget`, `Economii`, `Credite`,
  `Investitii`, `Pensie`, `Altele`
- [ ] **TODO 2.1b** `LectieIn`: `titlu` 3–200 caractere, `categorie`, `continut` minim 50 caractere
- [ ] **TODO 2.2a–d** `MesajChat`, `ChatIn`, `ApelTool` (`tool` + `rezultat`), `ChatOut`

**Test:**
```python
from s50_schema import LectieIn
LectieIn(titlu="Test", categorie="Buget", continut="prea scurt")   # ValidationError
```

---

## Pasul 3 — `s50_rag.py` (Chroma)

**Gata scris:** colecția Chroma.

- [ ] **TODO 3.1a** `indexeaza_lectie(lectie)` →
  `colectie.add(ids=[str(lectie.id)], documents=[lectie.continut], metadatas=[{"titlu": lectie.titlu}])`
- [ ] **TODO 3.1b** `indexeaza_toate(lectii)` → un `for` cu `indexeaza_lectie`
- [ ] **TODO 3.1c** `sterge_din_index(lectie_id)` → `colectie.delete(ids=[str(lectie_id)])`
- [ ] **TODO 3.2** `cauta(intrebare, n_rezultate=2)` → listă `{"titlu", "text", "distanta"}`

**Test:**
```python
import s50_model, s50_rag
with s50_model.SessionLocal() as s:
    s50_rag.indexeaza_toate(s50_model.toate_lectiile(s))
for r in s50_rag.cauta("de ce valoreaza banii mei mai putin in fiecare an?"):
    print(r["distanta"], r["titlu"])
```
Primul rezultat: **Inflația și puterea de cumpărare**.

---

## Pasul 4 — `s50_agent.py` (profesorul AI)

**Gata scris:** `SYSTEM_PROMPT` (rolul profesorului și **limitele** lui — nu recomandă
produse concrete, nu promite câștiguri), `llm`, `agent`, testul.

- [ ] **TODO 4.1** tool-ul `cauta_in_lectii(intrebare)` → lecțiile găsite, fiecare cu
  titlul în față: `[Fondul de urgenta]` + textul
- [ ] **TODO 4.2** `ruleaza_agent(mesaj, istoric)` → `(raspuns, apeluri)`

**Test:** `python3 s50_agent.py` — două întrebări din lecții și una la care
profesorul trebuie să refuze recomandarea („ce acțiuni să cumpăr mâine?”).

---

## Pasul 5 — `s50_app.py` (API-ul FastAPI)

**Gata scris:** importurile, pornirea (`init_db` + `indexeaza_toate`), `lectie_dict`,
`uvicorn.run(...)` pe portul **8005**.

- [ ] **TODO 5.1a** `GET /lectii?categorie=`
- [ ] **TODO 5.1b** `POST /lectii` (201) — titlu duplicat → `400`; apoi **`indexeaza_lectie`**
- [ ] **TODO 5.1c** `DELETE /lectii/{id}` — `404`; apoi **`sterge_din_index`**
- [ ] **TODO 5.2** `GET /cauta?intrebare=&n=2` — `n` în afara 1–5 → `400`
- [ ] **TODO 5.3** `POST /chat` — eroare de la OpenAI → `502`

**Test:** `python3 s50_app.py` → http://127.0.0.1:8005/docs

---

## Pasul 6 — `comun.py` + `s50_ui.py` (gata scrise)

`api(metoda, cale, ...)` întoarce `(ok, rezultat)`; `s50_ui.py` face meniul cu
cele 4 pagini. `API_URL` din `comun.py` trebuie să aibă **același port** ca
`uvicorn.run(...)` din `s50_app.py`.

**Test:** API pornit + `streamlit run s50_ui.py`.

---

## Pasul 7 — `s50_pages/` (paginile)

- [ ] **`lectii.py`** — TODO 1: filtrul de categorie; TODO 2: butonul Șterge
- [ ] **`adauga.py`** — TODO: `POST /lectii` cu `timeout=30`
- [ ] **`cautare.py`** — TODO: afișarea fiecărei lecții găsite (titlu, distanță, text)
- [ ] **`profesor.py`** — TODO 1: istoricul; TODO 2: salvarea mesajelor în `st.session_state`

---

## Test final end-to-end

MySQL pornit → `export OPENAI_API_KEY=...` → `python3 s50_app.py` →
`streamlit run s50_ui.py`:

1. **Căutare:** „de ce valorează banii mei mai puțin în fiecare an?” → primul rezultat:
   *Inflația și puterea de cumpărare*
2. **Profesor AI:** „cheltuiesc 4000 de lei pe lună, cât să am pentru urgențe?” →
   12.000–24.000 lei + sursa *Fondul de urgență*
3. **Adaugă lecție:** „Asigurarea locuinței” → **Profesor AI:** „de ce să-mi asigur
   apartamentul?” → răspunsul vine din lecția nouă
4. **Lecții:** șterge „Asigurarea locuinței” → aceeași întrebare: profesorul spune că
   nu are informația
5. **Profesor AI:** „ce acțiuni să cumpăr mâine?” → nu recomandă nimic concret
