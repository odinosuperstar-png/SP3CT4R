"""
routes/checkout.py
====================
Pagina di checkout e integrazione con Stripe per il pagamento.

FLUSSO DI PAGAMENTO IMPLEMENTATO (Stripe Payment Intents API):
1. L'utente arriva su /checkout e vede il riepilogo del proprio carrello.
2. Quando raggiunge lo Step 3, il frontend chiama POST /create-payment-intent:
   il server calcola l'importo esatto (prodotti + spedizione) e crea un
   PaymentIntent con Stripe, restituendo un "client_secret" al browser.
3. Il frontend usa Stripe.js (stripe.confirmCardPayment) per confermare il
   pagamento DIRETTAMENTE con Stripe: i dati della carta di credito non
   transitano mai dal nostro server, garantendo la conformità PCI-DSS.
4. In caso di successo, l'utente viene reindirizzato a /checkout/success.
5. In parallelo, l'endpoint /stripe/webhook riceve la conferma asincrona e
   affidabile da Stripe stesso: è il punto in cui, in produzione, si
   aggiornerebbe lo stato dell'ordine nel database.

IMPORTANTE: l'importo del pagamento viene SEMPRE ricalcolato sul server a
partire dal carrello salvato in sessione. Il client non decide mai quanto
pagare: questo previene manipolazioni lato browser dell'importo finale.
"""

from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for, current_app
import stripe

from data import get_prodotto_by_id

checkout_bp = Blueprint("checkout", __name__)


def _calcola_totale_carrello():
    """Ricalcola il totale del carrello (in euro) leggendo i prezzi dal catalogo."""
    carrello = session.get("carrello", {})
    totale = 0.0

    for id_come_stringa, quantita in carrello.items():
        prodotto = get_prodotto_by_id(int(id_come_stringa))
        if prodotto:
            totale += prodotto["prezzo"] * quantita

    return round(totale, 2)


def _calcola_costo_spedizione(metodo_spedizione, totale_prodotti):
    """Determina il costo di spedizione in base al metodo scelto e alla soglia gratuita."""
    if metodo_spedizione == "express":
        return current_app.config["COSTO_SPEDIZIONE_EXPRESS"]

    # Spedizione standard: gratuita oltre la soglia configurata
    if totale_prodotti >= current_app.config["SOGLIA_SPEDIZIONE_GRATUITA"]:
        return 0.0
    return current_app.config["COSTO_SPEDIZIONE_STANDARD"]


@checkout_bp.route("/checkout")
def checkout():
    """Renderizza la pagina di checkout con il riepilogo dell'ordine corrente."""
    carrello = session.get("carrello", {})

    # Non ha senso mostrare un checkout vuoto: si torna al catalogo
    if not carrello:
        return redirect(url_for("main.shop"))

    articoli = []
    for id_come_stringa, quantita in carrello.items():
        prodotto = get_prodotto_by_id(int(id_come_stringa))
        if prodotto:
            articoli.append({
                **prodotto,
                "quantita": quantita,
                "subtotale": round(prodotto["prezzo"] * quantita, 2),
            })

    totale_prodotti = _calcola_totale_carrello()

    return render_template(
        "checkout.html",
        articoli=articoli,
        totale=totale_prodotti,
        spedizione_standard=_calcola_costo_spedizione("standard", totale_prodotti),
        spedizione_express=_calcola_costo_spedizione("express", totale_prodotti),
    )


@checkout_bp.route("/create-payment-intent", methods=["POST"])
def crea_payment_intent():
    """
    Crea un PaymentIntent lato server e ne restituisce il client_secret.

    Questo è l'unico punto in cui il nostro backend "parla" con Stripe per
    avviare il pagamento: tutto il resto avviene tra il browser dell'utente
    e i server di Stripe, tramite Stripe.js.
    """
    dati_richiesta = request.get_json(silent=True) or {}
    metodo_spedizione = dati_richiesta.get("metodo_spedizione", "standard")

    totale_prodotti = _calcola_totale_carrello()
    if totale_prodotti <= 0:
        return jsonify({"errore": "Il carrello è vuoto."}), 400

    costo_spedizione = _calcola_costo_spedizione(metodo_spedizione, totale_prodotti)
    totale_finale = round(totale_prodotti + costo_spedizione, 2)

    # Stripe richiede l'importo espresso nella unità minima della valuta:
    # per l'Euro corrisponde ai centesimi (es. 49,90 € diventa 4990)
    importo_in_centesimi = int(round(totale_finale * 100))

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=importo_in_centesimi,
            currency=current_app.config["CURRENCY"],
            # Abilita automaticamente tutti i metodi di pagamento attivati
            # sulla Dashboard Stripe (carta, Apple Pay, Google Pay, Klarna, ecc.)
            automatic_payment_methods={"enabled": True},
            metadata={
                "carrello": str(session.get("carrello", {})),
                "metodo_spedizione": metodo_spedizione,
            },
        )
    except stripe.error.StripeError as errore_stripe:
        current_app.logger.error(f"Errore nella creazione del PaymentIntent: {errore_stripe}")
        return jsonify({"errore": "Impossibile inizializzare il pagamento. Riprova più tardi."}), 400

    return jsonify({
        "client_secret": payment_intent.client_secret,
        "importo_totale_centesimi": importo_in_centesimi,
    })


@checkout_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    """
    Endpoint che riceve le notifiche asincrone (webhook) da Stripe.

    È il modo più AFFIDABILE per sapere con certezza che un pagamento è
    andato a buon fine, perché funziona anche se l'utente chiude il browser
    subito dopo aver pagato, prima del redirect a /checkout/success.

    Per testarlo in locale, installa la Stripe CLI ed esegui:
        stripe listen --forward-to localhost:5000/stripe/webhook
    """
    payload = request.data
    firma_ricevuta = request.headers.get("Stripe-Signature", "")
    webhook_secret = current_app.config["STRIPE_WEBHOOK_SECRET"]

    try:
        evento = stripe.Webhook.construct_event(payload, firma_ricevuta, webhook_secret)
    except ValueError:
        # Payload malformato
        return jsonify({"errore": "Payload non valido."}), 400
    except stripe.error.SignatureVerificationError:
        # La firma non corrisponde: la richiesta potrebbe non provenire da Stripe
        return jsonify({"errore": "Firma del webhook non valida."}), 400

    if evento["type"] == "payment_intent.succeeded":
        payment_intent = evento["data"]["object"]
        # TODO produzione: qui si aggiornerebbe lo stato dell'ordine nel database
        # (es. da "in attesa di pagamento" a "pagato") e si invierebbe l'email
        # di conferma d'ordine al cliente.
        current_app.logger.info(f"Pagamento riuscito — PaymentIntent: {payment_intent['id']}")

    elif evento["type"] == "payment_intent.payment_failed":
        payment_intent = evento["data"]["object"]
        current_app.logger.warning(f"Pagamento fallito — PaymentIntent: {payment_intent['id']}")

    return jsonify({"ricevuto": True})


@checkout_bp.route("/checkout/success")
def checkout_successo():
    """Pagina mostrata dopo un pagamento completato con successo."""
    # Il carrello è stato acquistato: lo svuotiamo dalla sessione
    session.pop("carrello", None)
    return render_template("success.html")


@checkout_bp.route("/checkout/cancel")
def checkout_annullato():
    """Pagina mostrata quando il pagamento viene annullato o fallisce."""
    return render_template("cancel.html")
