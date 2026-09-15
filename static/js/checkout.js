/* ==========================================================================
   SP3CT4R — checkout.js
   ==========================================================================
   Gestisce esclusivamente la pagina /checkout:
   - navigazione tra i 3 step (Spedizione, Metodo, Pagamento)
   - aggiornamento del riepilogo ordine in base al metodo di spedizione scelto
   - montaggio del campo carta sicuro di Stripe Elements
   - invio del pagamento: crea il PaymentIntent sul server, poi lo conferma
     con Stripe.js senza far transitare i dati della carta dal nostro backend

   Le costanti STRIPE_PUBLIC_KEY, TOTALE_PRODOTTI, SPEDIZIONE_STANDARD e
   SPEDIZIONE_EXPRESS sono definite in un tag <script> inline dentro
   checkout.html, valorizzate lato server da Jinja2.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* ====================================================================
       1. NAVIGAZIONE TRA GLI STEP
       ==================================================================== */
    const step_sections = document.querySelectorAll(".checkout-step");
    const step_dots = document.querySelectorAll(".step-dot");

    function vaiAlloStep(numeroStep) {
        step_sections.forEach(step => step.classList.remove("active"));
        document.getElementById(`step-${numeroStep}`).classList.add("active");

        step_dots.forEach(dot => {
            const stepDelPuntino = parseInt(dot.dataset.step, 10);
            dot.classList.toggle("active", stepDelPuntino <= parseInt(numeroStep, 10));
        });

        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    document.querySelectorAll(".step-next-btn").forEach(bottone => {
        bottone.addEventListener("click", () => {
            // Prima di passare dallo Step 1 allo Step 2, valida il form di spedizione
            if (bottone.dataset.next === "2") {
                const formSpedizione = document.getElementById("shipping-form");
                if (!formSpedizione.checkValidity()) {
                    formSpedizione.reportValidity();
                    return;
                }
            }
            vaiAlloStep(bottone.dataset.next);
        });
    });

    document.querySelectorAll(".step-prev-btn").forEach(bottone => {
        bottone.addEventListener("click", () => vaiAlloStep(bottone.dataset.prev));
    });

    /* ====================================================================
       2. SELEZIONE DEL METODO DI SPEDIZIONE E AGGIORNAMENTO DEL RIEPILOGO
       ==================================================================== */
    const cardMetodiSpedizione = document.querySelectorAll(".shipping-option-card");
    const summaryShipping = document.getElementById("summary-shipping");
    const summaryTotal = document.getElementById("summary-total");

    function formattaPrezzo(valore) {
        return valore.toLocaleString("it-IT", { style: "currency", currency: "EUR" });
    }

    cardMetodiSpedizione.forEach(card => {
        card.addEventListener("click", () => {
            cardMetodiSpedizione.forEach(c => c.classList.remove("selected"));
            card.classList.add("selected");
            card.querySelector('input[type="radio"]').checked = true;
            aggiornaRiepilogoSpedizione();
        });
    });

    function aggiornaRiepilogoSpedizione() {
        const metodoSelezionato = document.querySelector('input[name="metodo_spedizione"]:checked').value;
        const costoSpedizione = metodoSelezionato === "express" ? SPEDIZIONE_EXPRESS : SPEDIZIONE_STANDARD;

        summaryShipping.textContent = costoSpedizione === 0 ? "Gratuita" : formattaPrezzo(costoSpedizione);
        summaryTotal.textContent = formattaPrezzo(TOTALE_PRODOTTI + costoSpedizione);
    }

    /* ====================================================================
       3. EXPRESS CHECKOUT (Apple Pay / PayPal / Klarna)
       ====================================================================
       In questa struttura iniziale i pulsanti sono funzionalmente dei
       segnaposto grafici. Per l'attivazione reale:
       - Apple Pay / Google Pay: Stripe Payment Request Button
         (richiede la verifica del dominio nella Dashboard Stripe)
       - PayPal e Klarna: vanno abilitati come Payment Method nella
         Dashboard Stripe e poi richiamati tramite l'API Payment Element
       ==================================================================== */
    document.querySelectorAll(".btn-express").forEach(bottone => {
        bottone.addEventListener("click", () => {
            alert("Metodo di pagamento rapido in fase di configurazione. Utilizza il pagamento con carta qui sotto.");
        });
    });

    /* ====================================================================
       4. INTEGRAZIONE STRIPE ELEMENTS (campo carta sicuro)
       ==================================================================== */
    const stripe = Stripe(STRIPE_PUBLIC_KEY);
    const elements = stripe.elements();

    // Stile del campo carta, allineato al tema scuro/neon del sito
    const stileCampoCarta = {
        style: {
            base: {
                color: "#F2F2F0",
                fontFamily: '"Inter", sans-serif',
                fontSize: "15px",
                "::placeholder": { color: "#5C5C5C" },
                iconColor: "#00E5C7",
            },
            invalid: {
                color: "#FF3B6B",
                iconColor: "#FF3B6B",
            },
        },
    };

    const cardElement = elements.create("card", stileCampoCarta);
    cardElement.mount("#card-element");

    cardElement.on("change", (evento) => {
        document.getElementById("card-errors").textContent = evento.error ? evento.error.message : "";
    });

    /* ====================================================================
       5. INVIO DEL PAGAMENTO
       ==================================================================== */
    const paymentForm = document.getElementById("payment-form");
    const submitBtn = document.getElementById("submit-payment-btn");
    const btnText = document.getElementById("btn-text");
    const btnSpinner = document.getElementById("btn-spinner");

    paymentForm.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        impostaStatoCaricamento(true);

        const metodoSpedizioneScelto = document.querySelector('input[name="metodo_spedizione"]:checked').value;
        const nomeTitolareCarta = document.getElementById("input-titolare").value;

        try {
            // Passo 1: chiede al backend Flask di creare il PaymentIntent,
            // calcolato sul totale reale del carrello salvato in sessione
            const rispostaIntent = await fetch("/create-payment-intent", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ metodo_spedizione: metodoSpedizioneScelto }),
            });
            const datiIntent = await rispostaIntent.json();

            if (datiIntent.errore) {
                mostraErrorePagamento(datiIntent.errore);
                impostaStatoCaricamento(false);
                return;
            }

            // Passo 2: conferma il pagamento direttamente con Stripe (non con il nostro server)
            const risultatoConferma = await stripe.confirmCardPayment(datiIntent.client_secret, {
                payment_method: {
                    card: cardElement,
                    billing_details: { name: nomeTitolareCarta },
                },
            });

            if (risultatoConferma.error) {
                mostraErrorePagamento(risultatoConferma.error.message);
                impostaStatoCaricamento(false);
            } else if (risultatoConferma.paymentIntent.status === "succeeded") {
                // Passo 3: pagamento riuscito, reindirizza alla pagina di successo
                window.location.href = "/checkout/success";
            }
        } catch (errore) {
            console.error("Errore imprevisto durante il pagamento:", errore);
            mostraErrorePagamento("Si è verificato un errore imprevisto. Riprova.");
            impostaStatoCaricamento(false);
        }
    });

    function mostraErrorePagamento(messaggio) {
        document.getElementById("card-errors").textContent = messaggio;
    }

    function impostaStatoCaricamento(inCorso) {
        submitBtn.disabled = inCorso;
        btnText.classList.toggle("hidden", inCorso);
        btnSpinner.classList.toggle("hidden", !inCorso);
    }
});
