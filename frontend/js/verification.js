const API_URL = "http://127.0.0.1:8000/api/verification/verify";

const documentInput = document.getElementById("documentInput");
const analyzeButton = document.getElementById("analyzeBtn");
const clearButton = document.getElementById("clearBtn");

const fileNameBox = document.getElementById("fileName");
const previewBox = document.getElementById("preview");
const loadingMessage = document.getElementById("loadingMessage");
const errorMessage = document.getElementById("errorMessage");

const resultBox = document.getElementById("result");
const closeResultButton = document.getElementById("closeResultBtn");
const resultHeader = document.getElementById("resultHeader");
const resultStatus = document.getElementById("resultStatus");
const resultMessage = document.getElementById("resultMessage");
const scoreNumber = document.getElementById("scoreNumber");
const genuineProbability = document.getElementById("genuineProbability");
const fakeProbability = document.getElementById("fakeProbability");
const analysisStatus = document.getElementById("analysisStatus");
const selectedFile = document.getElementById("selectedFile");
const resultPreview = document.getElementById("resultPreview");
const scoreBar = document.getElementById("scoreBar");
const genuineBar = document.getElementById("genuineBar");
const fakeBar = document.getElementById("fakeBar");
const resultNote = document.getElementById("resultNote");

let selectedDocument = null;

documentInput.addEventListener("change", function () {
    selectedDocument = documentInput.files[0] || null;

    console.log("FILE SELECTED:", selectedDocument);

    if (!selectedDocument) {
        fileNameBox.textContent = "No file selected";
        return;
    }

    fileNameBox.textContent = selectedDocument.name;
    errorMessage.style.display = "none";

    const reader = new FileReader();

    reader.onload = function (event) {
        previewBox.innerHTML =
            '<img src="' + event.target.result + '" alt="Document preview">';

        previewBox.style.display = "block";
    };

    reader.readAsDataURL(selectedDocument);
});

analyzeButton.addEventListener("click", async function (event) {
    event.preventDefault();

    console.log("ANALYZE CLICKED");
    console.log("SELECTED FILE:", selectedDocument);

    if (!selectedDocument) {
        errorMessage.textContent = "Please select a document first.";
        errorMessage.style.display = "block";
        return;
    }

    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analyzing...";
    loadingMessage.style.display = "block";
    errorMessage.style.display = "none";

    const formData = new FormData();

    formData.append(
        "document",
        selectedDocument,
        selectedDocument.name
    );

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            body: formData
        });

        console.log("HTTP STATUS:", response.status);

        const data = await response.json();

        console.log("BACKEND RESPONSE:", data);

        if (!response.ok) {
            throw new Error(data.detail || "Verification failed.");
        }

        const status = String(
            data.verification_status || data.result || ""
        ).toUpperCase();

        const score = Number(data.score || 0);
        const genuine = Number(data.genuine_probability || 0);
        const fake = Number(data.fake_probability || 0);

        resultStatus.textContent = status;

        resultMessage.textContent =
            data.message || "Document analysis completed.";

        scoreNumber.textContent =
            score.toFixed(2) + "%";

        genuineProbability.textContent =
            genuine.toFixed(2) + "%";

        fakeProbability.textContent =
            fake.toFixed(2) + "%";

        scoreBar.style.width = Math.min(score, 100) + "%";
        genuineBar.style.width = Math.min(genuine, 100) + "%";
        fakeBar.style.width = Math.min(fake, 100) + "%";
        resultPreview.src = previewBox.querySelector("img")?.src || "";

        analysisStatus.textContent =
            data.forgery_status || data.status || "Completed";

        resultNote.textContent = status === "FAKE"
            ? "The AI model detected a higher probability of a forged document."
            : status === "REAL"
                ? "The AI model detected a higher probability of a genuine document."
                : "The AI model requires a manual review of this document.";

        selectedFile.textContent =
            selectedDocument.name;

        resultHeader.classList.remove("real", "fake", "review");

        const resultClass = status === "REAL"
            ? "real"
            : status === "FAKE"
                ? "fake"
                : "review";

        resultHeader.classList.add(resultClass);

        let history = [];

        try {
            const storedHistory = localStorage.getItem("verificationHistory");
            const parsedHistory = storedHistory ? JSON.parse(storedHistory) : [];
            history = Array.isArray(parsedHistory) ? parsedHistory : [];
        } catch (storageError) {
            console.warn("Unable to read verification history:", storageError);
        }

        history.unshift({
            fileName: selectedDocument.name,
            result: status,
            score: score,
            genuineProbability: genuine,
            fakeProbability: fake,
            createdAt: new Date().toISOString()
        });

        localStorage.setItem(
            "verificationHistory",
            JSON.stringify(history.slice(0, 20))
        );

        resultBox.classList.add("is-visible");
        resultBox.style.display = "flex";

        localStorage.setItem(
            "documentsScanned",
            String(Number(localStorage.getItem("documentsScanned") || 0) + 1)
        );

        if (status === "REAL" || status === "FAKE") {
            const counterKey = status === "REAL"
                ? "verifiedDocuments"
                : "suspiciousDocuments";

            localStorage.setItem(
                counterKey,
                String(Number(localStorage.getItem(counterKey) || 0) + 1)
            );
        }

        console.log(
            "RESULT DISPLAYED:",
            status,
            score
        );

    } catch (error) {
        console.error("VERIFICATION ERROR:", error);

        errorMessage.textContent =
            error.message || "Unable to analyze the document.";

        errorMessage.style.display = "block";

    } finally {
        loadingMessage.style.display = "none";
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze & Verify";
    }
});

clearButton.addEventListener("click", function (event) {
    event.preventDefault();

    selectedDocument = null;
    documentInput.value = "";

    fileNameBox.textContent = "No file selected";

    previewBox.innerHTML = "";
    previewBox.style.display = "none";

    errorMessage.style.display = "none";
    resultBox.classList.remove("is-visible");
    resultBox.style.display = "none";
    loadingMessage.style.display = "none";
});

closeResultButton.addEventListener("click", function (event) {
    event.preventDefault();
    event.stopPropagation();
    resultBox.classList.remove("is-visible");
    resultBox.style.display = "none";
});
