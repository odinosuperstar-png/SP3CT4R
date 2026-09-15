"""
config.py
=========
Configurazione centrale dell'applicazione SP3CT4R.

Tutti i valori sensibili (chiavi Stripe, secret key) vengono letti dalle
variabili d'ambiente tramite python-dotenv, e MAI scritti direttamente
nel codice sorgente. Questo permette di tenere credenziali diverse per
sviluppo, staging e produzione senza modificare una sola riga di codice.
"""

import os
from dotenv import load_dotenv

# Carica le variabili definite nel file ".env" nella cartella del progetto
load_dotenv()


class Config:
    """Contenitore delle impostazioni dell'app, letto da app.config.from_object()."""

    # Chiave segreta usata da Flask per firmare crittograficamente la sessione
    # (nel nostro caso la sessione contiene il carrello dell'utente)
    SECRET_KEY = os.environ.get("SECRET_KEY", "chiave-di-sviluppo-NON-usare-in-produzione")

    # Credenziali Stripe: la chiave pubblica viene esposta al frontend,
    # la chiave segreta rimane esclusivamente sul server
    STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    # Valuta utilizzata per i pagamenti (formato ISO minuscolo, richiesto da Stripe)
    CURRENCY = "eur"

    # Soglia oltre la quale la spedizione standard diventa gratuita
    SOGLIA_SPEDIZIONE_GRATUITA = 150.00
    COSTO_SPEDIZIONE_STANDARD = 6.90
    COSTO_SPEDIZIONE_EXPRESS = 14.90
