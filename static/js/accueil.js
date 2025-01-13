document.addEventListener("DOMContentLoaded", () => {
    const scrollTopButton = document.getElementById("scrollTopButton");
    const contactButton = document.getElementById("contactButton");
    const contactForm = document.getElementById("contactForm");
    const closeContactFormButton = document.getElementById("closeContactForm");
    const notificationForm = document.getElementById("notificationForm"); // Notification pour formulaire
    const notification = document.getElementById("notification"); // Notification pour connexion, inscription et déconnexion
    const notificationRequest = document.getElementById("notificationRequest"); // Notification pour demande réalisée
    const footer = document.querySelector(".footer");
    const bottomButtons = document.querySelector(".bottom-buttons");

    // Scroll to top functionality
    if (scrollTopButton) {
        scrollTopButton.addEventListener("click", (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // Show contact form
    if (contactButton && contactForm) {
        contactButton.addEventListener("click", (e) => {
            e.preventDefault();
            contactForm.style.display = "block";
        });
    }

    // Close contact form
    if (closeContactFormButton && contactForm) {
        closeContactFormButton.addEventListener("click", (e) => {
            e.preventDefault();
            contactForm.style.display = "none";
        });
    }

    // Submit contact form
    const submitContactForm = document.getElementById("submitContactForm");
    if (submitContactForm) {
        submitContactForm.addEventListener("click", () => {
            if (validateContactForm()) {
                showFormNotification("Votre message a été transmis.");
                if (contactForm) contactForm.style.display = "none";
                const contactFormElement = document.getElementById("contactFormElement");
                if (contactFormElement) contactFormElement.reset();
            } else {
                alert("Veuillez remplir tous les champs.");
            }
        });
    }

    // Validate contact form fields
    function validateContactForm() {
        const name = document.getElementById("name")?.value.trim();
        const email = document.getElementById("email")?.value.trim();
        const subject = document.getElementById("subject")?.value.trim();
        const problem = document.getElementById("problem")?.value.trim();
        return name && email && subject && problem;
    }

    // Show notification for form submission
    function showFormNotification(message) {
        if (!notificationForm) return;

        notificationForm.textContent = message;
        notificationForm.style.display = "block";
        notificationForm.classList.add("show");
        setTimeout(() => {
            notificationForm.classList.remove("show");
            notificationForm.classList.add("hide");
            setTimeout(() => {
                notificationForm.classList.remove("hide");
                notificationForm.style.display = "none";
            }, 500);
        }, 3000);
    }

    // Show notification for successful login or inscription
    function showLoginNotification(message) {
        if (!notification) return;

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

    // Show notification for successful logout
    function showLogoutNotification(message) {
        if (!notification) return;

        notification.textContent = message;
        notification.style.display = "block";
        notification.style.backgroundColor = "#ffcccc"; // Fond rouge clair
        notification.style.color = "#721c24"; // Texte rouge foncé
        notification.style.border = "2px solid rgb(151, 36, 47)"; // Bordure rouge foncé
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

    // Show notification for a successful request (e.g., action réalisée)
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

    // Adjust bottom-buttons position to avoid overlapping with footer
    function adjustButtonPosition() {
        if (!footer || !bottomButtons) return;

        const footerRect = footer.getBoundingClientRect();
        const windowHeight = window.innerHeight;

        if (footerRect.top < windowHeight) {
            const overlapHeight = windowHeight - footerRect.top;
            bottomButtons.style.bottom = `${overlapHeight + 5}px`;
        } else {
            bottomButtons.style.bottom = "10px";
        }
    }

    // Attach event listeners for scroll and resize
    window.addEventListener("scroll", adjustButtonPosition);
    window.addEventListener("resize", adjustButtonPosition);
    adjustButtonPosition();

    // Display notifications based on URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const authSuccess = urlParams.get("auth") === "success";
    const logoutSuccess = urlParams.get("logout") === "success";
    const requestSuccess = urlParams.get("request") === "success";

    if (authSuccess) {
        const isInscriptionSuccess = urlParams.get("inscription") === "success";
        if (isInscriptionSuccess) {
            showLoginNotification("Inscription réussie ! Vous pouvez maintenant vous connecter.");
        } else {
            showLoginNotification("Connexion réussie !");
        }
    }

    if (logoutSuccess) {
        showLogoutNotification("Déconnexion réussie !");
    }

    if (requestSuccess) {
        showRequestNotification("Votre démarche a été réalisée !");
    }

    // Remove query parameters from the URL after displaying notifications
    if (authSuccess || logoutSuccess || requestSuccess) {
        const url = new URL(window.location);
        url.searchParams.delete("auth");
        url.searchParams.delete("logout");
        url.searchParams.delete("request");
        url.searchParams.delete("inscription");
        window.history.replaceState({}, document.title, url.toString());
    }
});
