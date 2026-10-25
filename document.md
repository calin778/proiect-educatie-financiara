# Proiectul 2 — Educație financiară personală

## Tema

Educația financiară nu se predă în școală, deși fiecare adult ia decizii
financiare importante: cum își împarte salariul, cât pune deoparte, ce credit
alege, dacă și cum investește, ce înseamnă pensia pe care o va primi. Multe
greșeli costisitoare (o datorie pe card care crește ani de zile, un credit ales
după rata lunară, bani ținuți „la saltea” în timp ce inflația îi mănâncă) vin
din necunoașterea câtorva noțiuni de bază.

**Educație financiară personală** este o bibliotecă de lecții scurte despre
bani, cu un **profesor AI** care explică noțiunile pe înțelesul oricui și le
aplică pe situația utilizatorului — **doar pe baza lecțiilor**, cu sursa
fiecărui răspuns.

## Cui se adresează

Adulților de 25–40 de ani care câștigă bani, plătesc chirie sau rate și vor să
înțeleagă ce fac cu ei: buget, economii, credite, investiții, pensie. Nu e
nevoie de cunoștințe financiare anterioare.

## Ce face aplicația

1. **Păstrează lecțiile** într-o bază de date MySQL — fiecare lecție are titlu,
   categorie și conținut.
2. **Permite adăugarea și ștergerea lecțiilor** dintr-o interfață web. O lecție
   nouă devine imediat cautabilă.
3. **Caută după sens**: întrebarea „de ce valorează banii mei mai puțin în
   fiecare an?” găsește lecția *Inflația și puterea de cumpărare*, deși cuvântul
   „inflație” lipsește.
4. **Explică ca un profesor**: asistentul AI caută lecțiile potrivite, le citește
   și explică noțiunea cu un exemplu, aplicat pe situația utilizatorului — și
   spune din ce lecție a luat informația.
5. **Are limite clare**: nu inventează, nu recomandă acțiuni, fonduri sau bănci
   concrete și nu promite câștiguri. Pentru decizii personale trimite la un
   consultant autorizat.

## Paginile aplicației

| Pagină | Ce face | Ce parte din RAG |
|---|---|---|
| 📚 **Lecții** | lista lecțiilor, filtru pe categorie, conținutul fiecărei lecții, ștergere | — (date) |
| ➕ **Adaugă lecție** | formular: titlu, categorie, conținut; lecția e salvată și indexată | — (date) |
| 🔎 **Căutare** | caută lecțiile după sens și arată distanța; **fără** modelul de chat | doar **R** |
| 🎓 **Profesor AI** | chat cu profesorul; sub fiecare răspuns, sursele folosite | **R + A + G** (RAG complet) |

## Cum funcționează

```
              ┌──────── MySQL ────────┐
  Lecții ───► │ tabela s50_lectie     │  ← sursa de adevăr
              └───────────────────────┘
                         │ la pornire + la fiecare adăugare/ștergere
                         ▼
              ┌──────── Chroma ───────┐
              │ aceleași lecții,      │  ← indexul pentru căutare după sens
              │ cu embedding-uri      │
              └───────────────────────┘
                         ▲
  Profesor AI ── /chat ── agent ── cauta_in_lectii  →  modelul scrie răspunsul
  Căutare ────── /cauta ───────────┘                    (doar rezultatele căutării)
```

## Lecțiile inițiale

Aplicația pornește cu 8 lecții (folderul `lectii_initiale/`):

| Lecție | Categorie |
|---|---|
| Bugetul personal și regula 50/30/20 | Buget |
| Fondul de urgență | Economii |
| Dobânda compusă | Economii |
| Inflația și puterea de cumpărare | Economii |
| Creditele: DAE, dobânda fixă și dobânda variabilă | Credite |
| Cardul de credit și datoriile scumpe | Credite |
| Investiții pentru începători: ETF-uri și diversificare | Investiții |
| Pensia în România: Pilonul I, Pilonul II și Pilonul III | Pensie |

Citiți-le — sunt noțiuni pe care le veți folosi toată viața, nu doar în aplicație.

## Exemple de întrebări

| Întrebare | Comportament așteptat |
|---|---|
| „Cheltuiesc 4000 de lei pe lună. Cât ar trebui să am pus deoparte pentru urgențe?” | 12.000–24.000 lei (3–6 luni), cu explicație; sursa *Fondul de urgență* |
| „Ce e DAE și de ce contează când iau un credit?” | explicația din *Creditele: DAE…*; compară ofertele după DAE, nu după dobândă |
| „Am o datorie pe card și 2000 de lei în plus. Plătesc datoria sau investesc?” | plătește întâi datoria scumpă; sursa *Cardul de credit…* |
| „Ce înseamnă regula lui 72?” | estimarea dublării banilor; sursa *Dobânda compusă* |
| „Ce acțiuni să cumpăr mâine ca să fac bani repede?” | **nu recomandă** acțiuni concrete; explică riscul și trimite la un consultant |

## Cerințe

**Obligatorii** (vezi `s50_plan.md`, pașii 1–7):
- [ ] baza de date cu lecțiile și funcțiile CRUD
- [ ] validarea datelor cu Pydantic (`LectieIn`)
- [ ] indexul Chroma: adăugare, ștergere, căutare
- [ ] profesorul AI cu tool-ul `cauta_in_lectii`
- [ ] API-ul FastAPI: `/lectii`, `/cauta`, `/chat`
- [ ] cele 4 pagini Streamlit
- [ ] testul final din plan trece

**Extinderi opționale** (după ce merg cerințele obligatorii):
- [ ] adăugați 2–3 lecții noi, scrise de voi (ex: *Asigurările de locuință și de
  viață*, *Cum citești un fluturaș de salariu: brut și net*, *Înșelătoriile financiare frecvente*)
- [ ] un al doilea tool pentru agent, `calculeaza_dobanda_compusa(suma, procent, ani)`,
  care face calculul **în Python** — un LLM greșește des la calcule
- [ ] o pagină „Calculator de buget”: utilizatorul introduce venitul net și vede
  împărțirea 50/30/20 (fără AI, doar Python și Streamlit)
- [ ] în pagina Căutare, colorați distanța: verde sub un prag, roșu peste

## Atenție

Lecțiile au scop **exclusiv educativ** și nu reprezintă consultanță financiară,
fiscală sau de investiții. Valorile legale (procente de contribuție, limite de
deducere, plafoane de garantare) se schimbă prin lege — verificați întotdeauna
valorile în vigoare. Pentru decizii personale, consultați un specialist autorizat.
