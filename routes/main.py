"""
routes/main.py
===============
Rotte "di navigazione" del sito: Home, Catalogo (Shop) e Pagina Prodotto.
Non contengono logica di pagamento: quella vive in routes/checkout.py.
"""

from flask import Blueprint, render_template, abort, request

from data import PRODOTTI, get_prodotto_by_id, get_categorie

# Il Blueprint raggruppa le rotte "principali" sotto un unico namespace ("main.*")
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Homepage: hero di brand + selezione di prodotti in evidenza."""
    prodotti_in_evidenza = [p for p in PRODOTTI if p.get("in_evidenza")]
    return render_template("index.html", prodotti_in_evidenza=prodotti_in_evidenza)


@main_bp.route("/shop")
def shop():
    """
    Catalogo prodotti, filtrabile per categoria tramite query string.
    Esempio: /shop?categoria=Giacche
    """
    categoria_attiva = request.args.get("categoria")

    if categoria_attiva:
        prodotti = [p for p in PRODOTTI if p["categoria"] == categoria_attiva]
    else:
        prodotti = PRODOTTI

    return render_template(
        "shop.html",
        prodotti=prodotti,
        categorie=get_categorie(),
        categoria_attiva=categoria_attiva,
    )


@main_bp.route("/product/<int:id_prodotto>")
def product_detail(id_prodotto):
    """Scheda del singolo prodotto, con suggerimento di articoli correlati."""
    prodotto = get_prodotto_by_id(id_prodotto)

    # Se l'id non corrisponde a nessun prodotto, restituisce un 404 standard
    if prodotto is None:
        abort(404)

    prodotti_correlati = [
        p for p in PRODOTTI
        if p["categoria"] == prodotto["categoria"] and p["id"] != prodotto["id"]
    ][:4]

    return render_template(
        "product.html",
        prodotto=prodotto,
        prodotti_correlati=prodotti_correlati,
    )
