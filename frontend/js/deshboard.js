(function () {

    function escapeHtml(value) {
        return String(value).replace(/[&<>'"]/g, function (character) {
            const entities = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                "'": "&#39;",
                "\"": "&quot;"
            };

            return entities[character];
        });
    }

    const historyElement =
        document.getElementById("verificationHistory");

    if (historyElement) {

        let history = [];

        try {
            const storedHistory = localStorage.getItem("verificationHistory");
            const parsedHistory = storedHistory ? JSON.parse(storedHistory) : [];
            history = Array.isArray(parsedHistory) ? parsedHistory : [];
        } catch (error) {
            console.error("Verification history error:", error);
        }

        if (history.length) {

            historyElement.innerHTML = history.map(function (item) {
                const date = new Date(item.createdAt).toLocaleString();

                return `
                    <div class="history-item">
                        <div>
                            <strong>${escapeHtml(item.fileName)}</strong>
                            <span>${date}</span>
                        </div>
                        <div class="history-result ${item.result === "REAL" ? "real" : "fake"}">
                            ${item.result} · ${Number(item.score).toFixed(2)}%
                        </div>
                    </div>
                `;
            }).join("");
        }
    }

    const scanned =
        Number(
            localStorage.getItem(
                "documentsScanned"
            ) || 0
        );


    const verified =
        Number(
            localStorage.getItem(
                "verifiedDocuments"
            ) || 0
        );


    const suspicious =
        Number(
            localStorage.getItem(
                "suspiciousDocuments"
            ) || 0
        );


    const scannedElement =
        document.getElementById(
            "documentsScanned"
        );


    const verifiedElement =
        document.getElementById(
            "verifiedDocuments"
        );


    const suspiciousElement =
        document.getElementById(
            "suspiciousDocuments"
        );


    if (scannedElement) {

        scannedElement.textContent =
            scanned;
    }


    if (verifiedElement) {

        verifiedElement.textContent =
            verified;
    }


    if (suspiciousElement) {

        suspiciousElement.textContent =
            suspicious;
    }

})();