"""
app.py
=======
Punto di ingresso dell'applicazione e-commerce SP3CT4R.

Per avviare il server in locale:
    1. python -m venv venv
    2. source venv/bin/activate      (su Windows: venv\\Scripts\\activate)
    3. pip install -r requirements.txt
    4. cp .env.example .env          (poi inserisci le tue chiavi Stripe di test)
    5. python app.py
    6. Apri http://127.0.0.1:5000 nel browser
"""

from flask import Flask
import stripe
import { SpeedInsights } 
from "@vercel/speed-insights/next"
from config import Config
from routes.main import main_bp
from routes.cart import cart_bp
from routes.checkout import checkout_bp
from flask import Response

@app.route("/robots.txt")
def robots_txt():
    return Response(
        """User-agent: *
Allow: /

Sitemap: https://sp3ct4r.vercel.app/sitemap.xml
""",
        mimetype="text/plain"
    )

def crea_app():
    """
    Application factory: costruisce e configura l'istanza Flask.

    Usare una funzione "factory" invece di un'istanza globale è una best
    practice consolidata, perché permette di creare più istanze dell'app
    con configurazioni diverse (utile per i test automatici, ad esempio).
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Imposta la chiave segreta di Stripe a livello globale per l'intero SDK
    stripe.api_key = app.config["STRIPE_SECRET_KEY"]

    # Registrazione dei Blueprint: ogni modulo di routes/ viene "agganciato"
    # all'applicazione principale, mantenendo il codice organizzato per dominio
    app.register_blueprint(main_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)

    # Rende la chiave pubblica Stripe disponibile in automatico in TUTTI i
    # template Jinja2, senza doverla passare manualmente in ogni render_template
    @app.context_processor
    def inject_stripe_public_key():
        return {"stripe_public_key": app.config["STRIPE_PUBLIC_KEY"]}

    # Gestione personalizzata della pagina 404, coerente con il tema del sito
    @app.errorhandler(404)
    def pagina_non_trovata(errore):
        from flask import render_template
        return render_template("404.html"), 404

    return app


# Istanza dell'applicazione, utilizzata sia da "python app.py" sia da
# eventuali server WSGI di produzione (es. Gunicorn: "gunicorn app:app")
app = crea_app()


if __name__ == "__main__":
    # debug=True abilita il reload automatico e le pagine di errore dettagliate:
    # DISATTIVARE SEMPRE in un ambiente di produzione reale
    app.run(debug=True, port=5000)
