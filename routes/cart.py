"""
routes/cart.py
================
Gestione del carrello tramite chiamate AJAX (fetch) dal frontend.

Il carrello viene salvato nella sessione Flask (lato server, firmata con la
SECRET_KEY) come dizionario {"id_prodotto_come_stringa": quantita}. Questo
evita di dover gestire un database per una funzionalità che, per sua natura,
è temporanea e legata alla sessione del visitatore.

Tutte le rotte rispondono in JSON e vengono consumate da static/js/cart.js.
"""

from flask import Blueprint, session, jsonify, request

from data import get_prodotto_by_id

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


def _leggi_carrello():
    """Recupera il carrello dalla sessione, creandolo vuoto se non esiste ancora."""
    return session.setdefault("carrello", {})


def _riepilogo_carrello(carrello):
    """
    Trasforma il carrello grezzo (id -> quantità) in una struttura completa
    con nome, prezzo, immagine e subtotali, pronta per essere serializzata in JSON
    e renderizzata dal frontend.
    """
    articoli = []
    totale = 0.0
    quantita_totale = 0

    for id_come_stringa, quantita in carrello.items():
        prodotto = get_prodotto_by_id(int(id_come_stringa))

        # Se un prodotto è stato rimosso dal catalogo ma è ancora in una vecchia
        # sessione, lo ignoriamo silenziosamente invece di far crashare la richiesta
        if prodotto is None:
            continue

        subtotale = round(prodotto["prezzo"] * quantita, 2)
        totale += subtotale
        quantita_totale += quantita

        articoli.append({
            "id": prodotto["id"],
            "nome": prodotto["nome"],
            "prezzo": prodotto["prezzo"],
            "immagine": prodotto["immagine"],
            "quantita": quantita,
            "subtotale": subtotale,
        })

    return {
        "articoli": articoli,
        "totale": round(totale, 2),
        "quantita_totale": quantita_totale,
    }


@cart_bp.route("/data")
def dati_carrello():
    """Restituisce lo stato attuale del carrello. Usata al caricamento di ogni pagina."""
    return jsonify(_riepilogo_carrello(_leggi_carrello()))


@cart_bp.route("/add", methods=["POST"])
def aggiungi_al_carrello():
    """Aggiunge un prodotto al carrello (o ne incrementa la quantità se già presente)."""
    dati_richiesta = request.get_json(silent=True) or {}

    try:
        id_prodotto = int(dati_richiesta.get("id_prodotto"))
        quantita = int(dati_richiesta.get("quantita", 1))
    except (TypeError, ValueError):
        return jsonify({"errore": "Dati della richiesta non validi."}), 400

    if get_prodotto_by_id(id_prodotto) is None:
        return jsonify({"errore": "Prodotto non trovato."}), 404

    if quantita < 1:
        return jsonify({"errore": "La quantità deve essere almeno 1."}), 400

    carrello = _leggi_carrello()
    chiave = str(id_prodotto)
    carrello[chiave] = carrello.get(chiave, 0) + quantita

    # Necessario perché Flask non rileva automaticamente le modifiche
    # a strutture dati mutabili (dict) annidate nella sessione
    session.modified = True

    return jsonify(_riepilogo_carrello(carrello))


@cart_bp.route("/update", methods=["POST"])
def aggiorna_quantita():
    """Imposta una nuova quantità per un articolo già nel carrello (pulsanti +/-)."""
    dati_richiesta = request.get_json(silent=True) or {}

    try:
        id_prodotto = int(dati_richiesta.get("id_prodotto"))
        nuova_quantita = int(dati_richiesta.get("quantita", 1))
    except (TypeError, ValueError):
        return jsonify({"errore": "Dati della richiesta non validi."}), 400

    carrello = _leggi_carrello()
    chiave = str(id_prodotto)

    if chiave in carrello:
        if nuova_quantita <= 0:
            # Una quantità a zero o negativa equivale a rimuovere l'articolo
            del carrello[chiave]
        else:
            carrello[chiave] = nuova_quantita
        session.modified = True

    return jsonify(_riepilogo_carrello(carrello))


@cart_bp.route("/remove", methods=["POST"])
def rimuovi_dal_carrello():
    """Rimuove completamente un articolo dal carrello."""
    dati_richiesta = request.get_json(silent=True) or {}
    chiave = str(dati_richiesta.get("id_prodotto"))

    carrello = _leggi_carrello()
    if chiave in carrello:
        del carrello[chiave]
        session.modified = True

    return jsonify(_riepilogo_carrello(carrello))
