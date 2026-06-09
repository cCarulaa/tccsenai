document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) {
        window.lucide.createIcons();
    }

    document.querySelectorAll(".js-photo-button").forEach((button) => {
        button.addEventListener("click", () => {
            const itemName = button.dataset.itemName || "Produto";
            const photoUrl = button.dataset.photoUrl;

            if (!photoUrl) {
                showAlert({
                    icon: "info",
                    title: itemName,
                    text: "Este item ainda nao possui foto cadastrada."
                });
                return;
            }

            if (window.Swal) {
                window.Swal.fire({
                    title: itemName,
                    imageUrl: photoUrl,
                    imageAlt: `Foto de ${itemName}`,
                    imageWidth: "100%",
                    customClass: {
                        image: "swal-product-image"
                    },
                    confirmButtonColor: "#176b5b",
                    confirmButtonText: "Fechar"
                });
            } else {
                window.open(photoUrl, "_blank", "noopener");
            }
        });
    });

    document.querySelectorAll(".js-photo-input").forEach((input) => {
        input.addEventListener("change", () => {
            const preview = document.querySelector(".photo-preview");
            const file = input.files && input.files[0];
            if (!preview) return;

            if (!file) {
                preview.hidden = true;
                preview.removeAttribute("src");
                return;
            }

            preview.src = URL.createObjectURL(file);
            preview.hidden = false;
        });
    });

    document.querySelectorAll(".js-confirm-form").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!window.Swal || form.dataset.confirmed === "true") return;

            event.preventDefault();
            window.Swal.fire({
                icon: "question",
                title: form.dataset.confirm || "Confirmar acao?",
                showCancelButton: true,
                confirmButtonColor: "#176b5b",
                cancelButtonColor: "#667085",
                confirmButtonText: "Confirmar",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    form.dataset.confirmed = "true";
                    form.submit();
                }
            });
        });
    });

    document.querySelectorAll(".js-movement-type").forEach((select) => {
        const purpose = document.querySelector(".js-purpose");
        const syncPurpose = () => {
            if (!purpose) return;
            purpose.required = select.value === "saida";
            purpose.placeholder = select.value === "saida"
                ? "Aula do professor Roger, aula na Volkswagen..."
                : "Reposicao, compra, devolucao...";
        };

        select.addEventListener("change", syncPurpose);
        syncPurpose();
    });

    window.setTimeout(() => {
        document.querySelectorAll(".alert").forEach((alert) => {
            if (window.bootstrap) {
                window.bootstrap.Alert.getOrCreateInstance(alert).close();
            } else {
                alert.remove();
            }
        });
    }, 5200);
});

function showAlert(options) {
    if (window.Swal) {
        window.Swal.fire({
            confirmButtonColor: "#176b5b",
            confirmButtonText: "Ok",
            ...options
        });
        return;
    }

    window.alert(options.text || options.title || "Aviso");
}
