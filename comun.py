import requests

API_URL = "http://127.0.0.1:8005"


# timeout: agentul de la /chat poate dura mai mult de 5 secunde,
# asa ca pagina Profesor AI trimite timeout=60 (ca la s49)
def api(metoda: str, cale: str, timeout: int = 5, **kwargs):
    try:
        r = requests.request(metoda, f"{API_URL}{cale}", timeout=timeout, **kwargs)
    except requests.exceptions.ConnectionError:
        return False, "Nu pot contacta API-ul. Ai pornit `python3 s50_app.py` intr-un alt terminal?"
    except requests.exceptions.Timeout:
        return False, "API-ul a raspuns prea greu (timeout)."

    if r.status_code >= 400:
        try:
            detaliu = r.json().get("detail", r.text)
        except ValueError:
            return False, r.text

        if isinstance(detaliu, list):
            mesaje = []
            for e in detaliu:
                camp = ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path"))
                mesaje.append(f"{camp}: {e['msg']}")
            return False, "; ".join(mesaje)
        return False, str(detaliu)

    return True, (r.json() if r.content else None)
