"""
data.py
=======
Catalogo prodotti del brand SP3CT4R.

NOTA PER LA PRODUZIONE:
Questa è una struttura INIZIALE del progetto: per semplicità e velocità di
sviluppo il catalogo è definito come lista Python in memoria. In un ambiente
di produzione questi dati dovrebbero risiedere in un database relazionale
(es. PostgreSQL) gestito tramite un ORM come SQLAlchemy, con relative
migrazioni (Flask-Migrate / Alembic). La struttura dei dizionari qui sotto
è pensata per rendere questo passaggio il più semplice possibile in futuro.
"""

# Le immagini utilizzano un servizio di placeholder (placehold.co) generato
# dinamicamente con i colori del brand. Sostituiscile con gli URL reali delle
# fotografie prodotto (es. su un bucket S3 o Cloudinary) quando disponibili.
_BASE_IMG = "https://placehold.co/700x900/151515/00E5C7"

PRODOTTI = [
    {
        "id": 1,
        "nome": "GHOST-01 Cargo Jacket",
        "categoria": "Giacche",
        "prezzo": 249.00,
        "codice_riferimento": "SP3-JK-001",
        "descrizione": (
            "Giacca cargo tecnica in tessuto ripstop idrorepellente, con tasche "
            "multiple a compressione e cuciture termosaldate. Costruita per la "
            "città, pensata per resistere a tutto."
        ),
        "immagine": f"{_BASE_IMG}?text=GHOST-01",
        "taglie": ["S", "M", "L", "XL", "XXL"],
        "in_evidenza": True,
    },
    {
        "id": 2,
        "nome": "NOMAD-X Tech Pants",
        "categoria": "Pantaloni",
        "prezzo": 179.00,
        "codice_riferimento": "SP3-PT-002",
        "descrizione": (
            "Pantaloni tecnici a vita regolabile con inserti elastici strategici, "
            "tasche cargo asimmetriche e fondo gamba regolabile con fettuccia."
        ),
        "immagine": f"{_BASE_IMG}?text=NOMAD-X",
        "taglie": ["S", "M", "L", "XL"],
        "in_evidenza": True,
    },
    {
        "id": 3,
        "nome": "VOID Oversized Hoodie",
        "categoria": "Maglie",
        "prezzo": 139.00,
        "codice_riferimento": "SP3-HD-003",
        "descrizione": (
            "Felpa oversize in cotone pesante 400gsm con cappuccio doppio strato "
            "e stampa riflettente SP3CT4R sulla schiena."
        ),
        "immagine": f"{_BASE_IMG}?text=VOID",
        "taglie": ["XS", "S", "M", "L", "XL"],
        "in_evidenza": True,
    },
    {
        "id": 4,
        "nome": "CIPHER Utility Vest",
        "categoria": "Giacche",
        "prezzo": 199.00,
        "codice_riferimento": "SP3-JK-004",
        "descrizione": (
            "Gilet utility modulare con sistema di aggancio MOLLE, tasche "
            "trasparenti removibili e fibbie metalliche verniciate opache."
        ),
        "immagine": f"{_BASE_IMG}?text=CIPHER",
        "taglie": ["S", "M", "L", "XL"],
        "in_evidenza": False,
    },
    {
        "id": 5,
        "nome": "STEALTH Cargo Shorts",
        "categoria": "Pantaloni",
        "prezzo": 99.00,
        "codice_riferimento": "SP3-PT-005",
        "descrizione": (
            "Bermuda cargo in twill resistente con tasconi laterali e coulisse "
            "interna in vita per una vestibilità regolabile."
        ),
        "immagine": f"{_BASE_IMG}?text=STEALTH",
        "taglie": ["S", "M", "L", "XL"],
        "in_evidenza": False,
    },
    {
        "id": 6,
        "nome": "GRID Longsleeve Tee",
        "categoria": "Maglie",
        "prezzo": 69.00,
        "codice_riferimento": "SP3-TS-006",
        "descrizione": (
            "Maglia a manica lunga in cotone organico con pannello a griglia "
            "stampato e collo a costine rinforzato."
        ),
        "immagine": f"{_BASE_IMG}?text=GRID",
        "taglie": ["XS", "S", "M", "L", "XL", "XXL"],
        "in_evidenza": True,
    },
    {
        "id": 7,
        "nome": "RECON Tactical Backpack",
        "categoria": "Accessori",
        "prezzo": 159.00,
        "codice_riferimento": "SP3-AC-007",
        "descrizione": (
            "Zaino tattico 28L con scomparto imbottito per laptop, pannello "
            "MOLLE frontale e tessuto esterno a prova di strappo."
        ),
        "immagine": f"{_BASE_IMG}?text=RECON",
        "taglie": ["Taglia Unica"],
        "in_evidenza": False,
    },
    {
        "id": 8,
        "nome": "PULSE Balaclava",
        "categoria": "Accessori",
        "prezzo": 45.00,
        "codice_riferimento": "SP3-AC-008",
        "descrizione": (
            "Passamontagna tecnico in maglia scuba con dettagli catarifrangenti, "
            "essenziale per completare ogni look SP3CT4R."
        ),
        "immagine": f"{_BASE_IMG}?text=PULSE",
        "taglie": ["Taglia Unica"],
        "in_evidenza": False,
    },
    {
        "id": 9,
        "nome": "ECHO Windbreaker",
        "categoria": "Giacche",
        "prezzo": 219.00,
        "codice_riferimento": "SP3-JK-009",
        "descrizione": (
            "Giacca a vento ultraleggera ripiegabile in tasca, cuciture nastrate "
            "e cappuccio con regolazione a tre punti."
        ),
        "immagine": f"{_BASE_IMG}?text=ECHO",
        "taglie": ["S", "M", "L", "XL"],
        "in_evidenza": False,
    },
    {
        "id": 10,
        "nome": "DRIFT Track Pants",
        "categoria": "Pantaloni",
        "prezzo": 149.00,
        "codice_riferimento": "SP3-PT-010",
        "descrizione": (
            "Pantaloni track tecnici con bande laterali a contrasto, caviglia "
            "elasticizzata con zip e tasca posteriore a scomparsa."
        ),
        "immagine": f"{_BASE_IMG}?text=DRIFT",
        "taglie": ["S", "M", "L", "XL"],
        "in_evidenza": True,
    },
]


def get_prodotto_by_id(id_prodotto):
    """Restituisce il dizionario prodotto corrispondente all'id, o None se non esiste."""
    return next((prodotto for prodotto in PRODOTTI if prodotto["id"] == id_prodotto), None)


def get_categorie():
    """Restituisce l'elenco ordinato e senza duplicati delle categorie disponibili."""
    return sorted({prodotto["categoria"] for prodotto in PRODOTTI})
