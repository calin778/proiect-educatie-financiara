# =============================================================
# RAG  -  indexul Chroma al lectiilor  (ca s49_rag.py)
# =============================================================
# Acest modul implementeaza componenta de cautare din RAG, la fel ca in
# 48.1 si 49:
#   - add()   -> salveaza lectiile in Chroma
#   - query() -> regaseste lectiile cu sensul cel mai apropiat de o intrebare
#
# Fiecare lectie din MySQL devine un document in Chroma, cu acelasi id.
# MySQL ramane sursa de adevar; Chroma este doar un index, pastrat in
# memorie si reconstruit din MySQL la fiecare pornire.
#
# De ce este nevoie de Chroma, pe langa MySQL:
#   MySQL cauta dupa potrivire de text (WHERE titlu = ..., LIKE '%inflatie%').
#   Utilizatorii formuleaza insa intrebarile in propriii termeni - de
#   exemplu "de ce valoreaza banii mei mai putin in fiecare an?", in timp
#   ce lectia relevanta vorbeste despre "inflatie" si "puterea de
#   cumparare". Chroma reprezinta fiecare text printr-un embedding (un
#   vector numeric care descrie sensul textului) si regaseste documentele
#   cu sens apropiat, chiar daca nu au cuvinte in comun cu intrebarea.
#
# Unde sunt folosite functiile din acest modul:
#   s50_app.py   -> la pornire:        indexeaza_toate(...)
#                -> POST /lectii:       indexeaza_lectie(l)
#                -> DELETE /lectii:     sterge_din_index(id)
#                -> GET /cauta:         cauta(intrebare, n)
#   s50_agent.py -> tool-ul cauta_in_lectii apeleaza cauta(intrebare)
#                   pentru a furniza modelului contextul din care raspunde.
#
# Setup: pip install chromadb openai
#        export OPENAI_API_KEY="sk-..."   (cheia NU se scrie in cod)
# =============================================================

import chromadb
from chromadb.utils import embedding_functions


# #############################################################
# PARTEA 0 - COLECTIA CHROMA  (gata scrisa)
# #############################################################
# O colectie Chroma este echivalentul unei tabele: contine toate lectiile.
# functie_embedding transforma textul in vectori. Chroma o apeleaza
# automat, atat la adaugare (add), cat si la cautare (query), deci
# functiilor de mai jos le transmitem doar text.
#
# api_key_env_var = NUMELE variabilei de mediu din care se citeste cheia
# (nu cheia insasi!).
functie_embedding = embedding_functions.OpenAIEmbeddingFunction(
    api_key_env_var="OPENAI_API_KEY",
    model_name="text-embedding-3-small",
)

# chromadb.Client() pastreaza datele doar in memorie: la oprirea
# serverului indexul se pierde. Din acest motiv, s50_app.py il
# reconstruieste din MySQL la fiecare pornire.
client = chromadb.Client()
colectie = client.create_collection(
    name="s50_lectii",
    embedding_function=functie_embedding,
)


# #############################################################
# PARTEA 1 - INDEXARE  (plan: 3.1)
# #############################################################
# Indexarea inseamna adaugarea unei lectii in Chroma, astfel incat sa poata
# fi regasita la cautare. O lectie prezenta in MySQL, dar absenta din index,
# nu va fi niciodata folosita de profesorul AI.


# TODO 3.1a: indexeaza_lectie(lectie)
#
#   Scop: adauga o singura lectie in Chroma.
#
#   De ce este necesara: este operatia de baza pe care se sprijina restul
#   indexarii. Este folosita in doua locuri:
#     - indexeaza_toate(), pentru fiecare lectie, la pornirea aplicatiei;
#     - POST /lectii din s50_app.py, imediat dupa salvarea lectiei noi
#       in MySQL. Fara acest pas, lectia noua nu ar aparea in rezultatele
#       cautarii pana la urmatoarea repornire a serverului.
#
#   Parametri: lectie - obiect Lectie (din s50_model.py), cu .id, .titlu, .continut
#   Returneaza: nimic
#
#   Implementare: un singur apel colectie.add(...), cu trei liste de cate
#   un element:
#     ids        [str(lectie.id)]            id-ul din MySQL, convertit la str
#                                            (Chroma accepta doar id-uri text).
#                                            Pastrarea aceluiasi id permite
#                                            ulterior stergerea exacta a lectiei.
#     documents  [lectie.continut]           textul pe baza caruia Chroma
#                                            calculeaza embedding-ul si in care
#                                            se face cautarea.
#     metadatas  [{"titlu": lectie.titlu}]   informatii asociate documentului,
#                                            care nu participa la cautare. Titlul
#                                            ne permite sa identificam sursa
#                                            fiecarui rezultat, pe care profesorul
#                                            o citeaza in raspuns.
#
#   Parametrii sunt liste deoarece add() poate primi mai multe documente
#   simultan; aici transmitem cate unul.
def indexeaza_lectie(lectie):
    colectie.add(
        ids=[str(lectie.id)],
        documents=[lectie.continut],
        metadatas=[{"titlu": lectie.titlu}],
    )


# TODO 3.1b: indexeaza_toate(lectii)
#
#   Scop: adauga in Chroma toate lectiile primite.
#
#   De ce este necesara: indexul este pastrat doar in memorie (vezi
#   PARTEA 0), deci la fiecare pornire colectia este goala. s50_app.py
#   citeste toate lectiile din MySQL si le transmite acestei functii,
#   pentru ca indexul sa reflecte din nou continutul bazei de date.
#
#   Parametri: lectii - lista de obiecte Lectie (rezultatul
#              s50_model.toate_lectiile)
#   Returneaza: nimic
#
#   Implementare:
#     1. for lectie in lectii:  indexeaza_lectie(lectie)
#        (reutilizam 3.1a, fara a duplica apelul colectie.add)
#     2. La final, afisati un mesaj de verificare:
#           print(f"Index RAG: {colectie.count()} lectii.")
#        colectie.count() intoarce numarul de documente din Chroma si ar
#        trebui sa coincida cu numarul de lectii din MySQL.
def indexeaza_toate(lectii):
    for lectie in lectii:
        indexeaza_lectie(lectie)
    print(f"Index RAG: {colectie.count()} lectii.")


# TODO 3.1c: sterge_din_index(lectie_id)
#
#   Scop: elimina o lectie din Chroma, pe baza id-ului.
#
#   De ce este necesara: MySQL si Chroma trebuie sa ramana sincronizate.
#   Daca o lectie ar fi stearsa doar din MySQL, textul ei ar ramane in index,
#   iar profesorul AI ar putea in continuare sa formuleze raspunsuri pe baza
#   unei lectii care nu mai exista. Functia este apelata de
#   DELETE /lectii/{lectie_id} din s50_app.py, dupa stergerea din MySQL.
#
#   Parametri: lectie_id - int, id-ul lectiei din MySQL
#   Returneaza: nimic
#
#   Implementare:
#       colectie.delete(ids=[str(lectie_id)])
#   Conversia la str este obligatorie: in 3.1a id-ul a fost salvat ca text,
#   iar un id numeric nu ar corespunde niciunui document.
def sterge_din_index(lectie_id):
    colectie.delete(ids=[str(lectie_id)])


# #############################################################
# PARTEA 2 - CAUTARE  (plan: 3.2)
# #############################################################
# Aceasta este etapa de Retrieval (regasire) din RAG: pentru o intrebare,
# identificam lectiile relevante. Modelul AI le primeste apoi ca context
# si isi construieste raspunsul exclusiv pe baza lor (Augmented Generation).


# TODO 3.2: cauta(intrebare, n_rezultate=2)
#
#   Scop: regaseste cele mai relevante n_rezultate lectii pentru intrebare,
#   pe baza similaritatii de sens.
#
#   De ce este necesara: este punctul comun prin care API-ul si agentul
#   acceseaza indexul:
#     - GET /cauta din s50_app.py o apeleaza direct (pagina "Cautare" din
#       UI afiseaza rezultatele fara model AI, util pentru verificarea
#       calitatii cautarii);
#     - tool-ul cauta_in_lectii din s50_agent.py o foloseste pentru a
#       furniza profesorului textele pe care isi bazeaza raspunsul.
#   Ambii consumatori au nevoie de un format simplu, nu de structura
#   imbricata returnata de Chroma; de aceea rezultatul este convertit
#   intr-o lista de dictionare.
#
#   Parametri: intrebare (str), n_rezultate (int, implicit 2)
#   Returneaza: o lista de dictionare, ordonata de la cea mai relevanta lectie:
#       [{"titlu": "Fondul de urgenta", "text": "...", "distanta": 0.58}, ...]
#   O distanta mai mica indica o lectie mai relevanta.
#
#   Implementare:
#     1. rezultat = colectie.query(query_texts=[intrebare], n_results=n_rezultate)
#        Chroma calculeaza embedding-ul intrebarii si il compara cu cele
#        ale lectiilor indexate.
#
#     2. rezultat este un dictionar ale carui valori sunt liste de liste -
#        cate o lista interioara pentru fiecare intrebare transmisa. Intrucat
#        transmitem o singura intrebare, folosim elementul [0]:
#           texte    = rezultat["documents"][0]    textele lectiilor gasite
#           metadate = rezultat["metadatas"][0]    dictionarele {"titlu": ...}
#           distante = rezultat["distances"][0]    distanta fata de intrebare
#        Cele trei liste sunt aliniate: pozitia i din fiecare corespunde
#        aceleiasi lectii.
#
#     3. lista = []
#        for i in range(len(texte)): adaugati in lista un dictionar cu
#          "titlu"    -> metadate[i]["titlu"]
#          "text"     -> texte[i]
#          "distanta" -> round(distante[i], 3)
#
#     4. return lista
#
#   Verificare (s50_plan.md, Pasul 3): pentru intrebarea "de ce valoreaza
#   banii mei mai putin in fiecare an?", primul rezultat trebuie sa fie
#   "Inflatia si puterea de cumparare".
def cauta(intrebare, n_rezultate=2):
    rezultat = colectie.query(query_texts=[intrebare], n_results=n_rezultate)
    texte = rezultat["documents"][0]
    metadate = rezultat["metadatas"][0]
    distante = rezultat["distances"][0]
    lista = []
    for i in range(len(texte)):
        lista.append({
            "titlu": metadate[i]["titlu"],
            "text": texte[i],
            "distanta": round(distante[i], 3),
        })
    return lista