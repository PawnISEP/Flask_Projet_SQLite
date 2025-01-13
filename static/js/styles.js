document.addEventListener("DOMContentLoaded", () => {
    // Sélection des éléments nécessaires
    const searchBar = document.getElementById("searchBar");
    const rows = document.querySelectorAll("#catalogueBody tr");
    const noResultsMessage = document.getElementById("noResultsMessage");
    const scrollTopButton = document.getElementById("scrollTopButton");
    const contactButton = document.getElementById("contactButton");
    const contactForm = document.getElementById("contactForm");
    const closeContactFormButton = document.getElementById("closeContactForm");
    const submitContactForm = document.getElementById("submitContactForm");
    const notification = document.getElementById("notification");
    const notificationRequest = document.getElementById("notificationRequest");
    const footer = document.querySelector(".pied-de-page");
    const bottomButtons = document.querySelector(".bottom-buttons");

    // Affiche une notification si "auth=login-required" est dans l'URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth') === 'login-required') {
        showNotification("Vous devez être connecté pour accéder à cette page.");
    }

    // Gestion des notifications pour les emprunts
    const requestSuccess = urlParams.get("request") === "success";
    const requestError = urlParams.get("request") === "error";

    if (requestSuccess) {
        showRequestNotification("Votre démarche a été effectué avec succès !");
    } else if (requestError) {
        showRequestNotification("Erreur : Veuillez réessayer.");
    }

    // Supprimer les paramètres de l'URL après affichage
    if (requestSuccess || requestError) {
        const url = new URL(window.location);
        url.searchParams.delete("request");
        window.history.replaceState({}, document.title, url.toString());
    }

    // Fonction pour remonter en haut de la page
    if (scrollTopButton) {
        scrollTopButton.addEventListener("click", (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // Ouvrir le formulaire de contact
    if (contactButton) {
        contactButton.addEventListener("click", (e) => {
            e.preventDefault();
            contactForm.style.display = "block";
        });
    }

    // Fermer le formulaire de contact
    if (closeContactFormButton) {
        closeContactFormButton.addEventListener("click", (e) => {
            e.preventDefault();
            contactForm.style.display = "none";
        });
    }

    // Soumission du formulaire de contact
    if (submitContactForm) {
        submitContactForm.addEventListener("click", () => {
            if (validateContactForm()) {
                showNotification("Votre message a été transmis.");
                contactForm.style.display = "none";
                document.getElementById("contactFormElement").reset();
            } else {
                alert("Veuillez remplir tous les champs.");
            }
        });
    }

    // Validation du formulaire
    function validateContactForm() {
        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const subject = document.getElementById("subject").value.trim();
        const problem = document.getElementById("problem").value.trim();
        return name && email && subject && problem;
    }

    // Affiche une notification temporaire
    function showNotification(message) {
        notification.textContent = message;
        notification.style.display = "block";
        notification.classList.add("show");
        setTimeout(() => {
            notification.classList.remove("show");
            notification.classList.add("hide");
            setTimeout(() => {
                notification.classList.remove("hide");
                notification.style.display = "none";
            }, 500);
        }, 3000);
    }

    // Affiche une notification pour les emprunts
    function showRequestNotification(message) {
        if (!notificationRequest) return;

        notificationRequest.textContent = message;
        notificationRequest.style.display = "block";
        notificationRequest.classList.add("show");
        setTimeout(() => {
            notificationRequest.classList.remove("show");
            notificationRequest.classList.add("hide");
            setTimeout(() => {
                notificationRequest.classList.remove("hide");
                notificationRequest.style.display = "none";
            }, 500);
        }, 3000);
    }

    // Ajuste la position des boutons "haut" et "contact"
    function adjustButtonPosition() {
        const footerRect = footer.getBoundingClientRect();
        const windowHeight = window.innerHeight;

        if (footerRect.top < windowHeight) {
            const overlapHeight = windowHeight - footerRect.top;
            bottomButtons.style.transform = `translateY(-${overlapHeight - 2}px)`;
        } else {
            bottomButtons.style.transform = "translateY(0)";
        }
    }

    // Ajustement des boutons au défilement et au redimensionnement
    window.addEventListener("scroll", adjustButtonPosition);
    window.addEventListener("resize", adjustButtonPosition);
    adjustButtonPosition(); // Initialisation

    // Recherche dynamique dans le tableau
    searchBar.addEventListener("input", () => {
        const query = searchBar.value.toLowerCase();
        let hasResults = false;

        rows.forEach(row => {
            const titre = row.querySelector(".titre-livre").textContent.toLowerCase();
            if (titre.includes(query)) {
                row.style.display = ""; // Afficher
                hasResults = true;
            } else {
                row.style.display = "none"; // Masquer
            }
        });

        noResultsMessage.style.display = hasResults ? "none" : "block";
    });
});
