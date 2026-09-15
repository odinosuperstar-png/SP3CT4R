/* ==========================================================================
   SP3CT4R — cart.js
   ==========================================================================
   Gestisce:
   - apertura e chiusura del Cart Drawer (pannello laterale)
   - caricamento dello stato del carrello dal server (GET /cart/data)
   - aggiunta prodotti (POST /cart/add), esposta globalmente come
     window.aggiungiAlCarrello() così da poter essere richiamata dai
     pulsanti "Aggiungi al carrello" presenti in shop.html e product.html
   - modifica quantità (POST /cart/update) e rimozione (POST /cart/remove)

   Questo file viene caricato in OGNI pagina (incluso in base.html), perché
   il badge del carrello nell'header deve restare sempre aggiornato.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {

    // ---------- Riferimenti agli elementi del DOM ----------
    const cartDrawer = document.getElementById("cart-drawer");
    const drawerOverlay = document.getElementById("drawer-overlay");
    const cartToggleBtn = document.getElementById("cart-toggle-btn");
    const closeDrawerBtn = document.getElementById("close-drawer-btn");
    const cartBody = document.getElementById("cart-drawer-body");
    const cartBadge = document.getElementById("cart-badge");
    const cartSubtotal = document.getElementById("cart-subtotal");

    // ---------- Apertura / chiusura del drawer ----------
    function apriCarrello() {
        cartDrawer.classList.add("open");
        drawerOverlay.classList.add("visible");
    }

    function chiudiCarrello() {
        cartDrawer.classList.remove("open");
        drawerOverlay.classList.remove("visible");
    }

    if (cartToggleBtn) {
        cartToggleBtn.addEventListener("click", () => {
            apriCarrello();
            caricaCarrello();
        });
    }
    if (closeDrawerBtn) closeDrawerBtn.addEventListener("click", chiudiCarrello);
    if (drawerOverlay) drawerOverlay.addEventListener("click", chiudiCarrello);

    // ---------- Utility: formattazione prezzo in Euro (locale italiano) ----------
    function formattaPrezzo(valore) {
        return valore.toLocaleString("it-IT", { style: "currency", currency: "EUR" });
    }

    // ---------- Renderizza gli articoli ricevuti dal server nel drawer ----------
    function renderizzaCarrello(dati) {
        if (cartBadge) cartBadge.textContent = dati.quantita_totale;
        if (cartSubtotal) cartSubtotal.textContent = formattaPrezzo(dati.totale);

        if (!cartBody) return;

        if (dati.articoli.length === 0) {
            cartBody.innerHTML = '<p class="cart-empty-msg">Il tuo carrello è vuoto.</p>';
            return;
        }

        cartBody.innerHTML = dati.articoli.map(articolo => `
            <div class="cart-item" data-id="${articolo.id}">
                <img src="${articolo.immagine}" alt="${articolo.nome}" class="cart-item-img">
                <div class="cart-item-info">
                    <p class="cart-item-name">${articolo.nome}</p>
                    <p class="cart-item-price">${formattaPrezzo(articolo.prezzo)}</p>
                    <div class="qty-controls">
                        <button class="qty-btn qty-decrease" data-id="${articolo.id}" aria-label="Diminuisci quantità">−</button>
                        <span class="qty-value">${articolo.quantita}</span>
                        <button class="qty-btn qty-increase" data-id="${articolo.id}" aria-label="Aumenta quantità">+</button>
                    </div>
                </div>
                <button class="remove-item-btn" data-id="${articolo.id}" aria-label="Rimuovi articolo">&times;</button>
            </div>
        `).join("");

        collegaEventiArticoliCarrello();
    }

    // ---------- Recupera lo stato attuale del carrello dal server ----------
    function caricaCarrello() {
        fetch("/cart/data")
            .then(risposta => risposta.json())
            .then(dati => renderizzaCarrello(dati))
            .catch(errore => console.error("Errore nel caricamento del carrello:", errore));
    }

    // ---------- Aggiunge un prodotto al carrello (funzione globale) ----------
    // Richiamata dai pulsanti "Aggiungi al carrello" / "Aggiungi Rapido"
    // presenti in shop.html, product.html e nella card prodotto.
    window.aggiungiAlCarrello = function (idProdotto, quantita = 1) {
        fetch("/cart/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id_prodotto: idProdotto, quantita: quantita }),
        })
            .then(risposta => risposta.json())
            .then(dati => {
                renderizzaCarrello(dati);
                apriCarrello();
            })
            .catch(errore => console.error("Errore nell'aggiunta al carrello:", errore));
    };

    // ---------- Aggiorna la quantità di un articolo già presente ----------
    function aggiornaQuantita(idProdotto, nuovaQuantita) {
        fetch("/cart/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id_prodotto: idProdotto, quantita: nuovaQuantita }),
        })
            .then(risposta => risposta.json())
            .then(dati => renderizzaCarrello(dati))
            .catch(errore => console.error("Errore nell'aggiornamento della quantità:", errore));
    }

    // ---------- Rimuove completamente un articolo dal carrello ----------
    function rimuoviArticolo(idProdotto) {
        fetch("/cart/remove", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id_prodotto: idProdotto }),
        })
            .then(risposta => risposta.json())
            .then(dati => renderizzaCarrello(dati))
            .catch(errore => console.error("Errore nella rimozione dell'articolo:", errore));
    }

    // ---------- Collega gli eventi ai pulsanti +/- e rimuovi generati dinamicamente ----------
    function collegaEventiArticoliCarrello() {
        document.querySelectorAll(".qty-increase").forEach(bottone => {
            bottone.addEventListener("click", () => {
                const id = bottone.dataset.id;
                const valoreAttuale = parseInt(bottone.previousElementSibling.textContent, 10);
                aggiornaQuantita(id, valoreAttuale + 1);
            });
        });

        document.querySelectorAll(".qty-decrease").forEach(bottone => {
            bottone.addEventListener("click", () => {
                const id = bottone.dataset.id;
                const valoreAttuale = parseInt(bottone.nextElementSibling.textContent, 10);
                aggiornaQuantita(id, valoreAttuale - 1);
            });
        });

        document.querySelectorAll(".remove-item-btn").forEach(bottone => {
            bottone.addEventListener("click", () => rimuoviArticolo(bottone.dataset.id));
        });
    }

    // Al caricamento di ogni pagina, sincronizza subito il badge del carrello
    caricaCarrello();
});
