// BACKEND URL
// Supports overrides:
// - Query param: ?api=http://127.0.0.1:8000
// - LocalStorage: rag_serve_base_url
function resolveBaseUrl() {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get("api") || params.get("base_url") || params.get("backend");
    const fromStorage = localStorage.getItem("rag_serve_base_url");
    const raw = (fromQuery || fromStorage || "https://rag-serve.onrender.com").trim();
    return raw.replace(/\/+$/, "");
}

const BASE_URL = resolveBaseUrl();
localStorage.setItem("rag_serve_base_url", BASE_URL);

// UI Elements
const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

const fileInput = document.getElementById("file-input");
const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");

const apiKeyInput = document.getElementById("api-key-input");
const apiKeyTestBtn = document.getElementById("api-key-test-btn");
const apiKeyStatus = document.getElementById("api-key-status");
const llmProviderSelect = document.getElementById("llm-provider");

const metricsBox = document.getElementById("metrics-box");

function isLocalBackend(url) {
    try {
        const u = new URL(url);
        return u.hostname === "localhost" || u.hostname === "127.0.0.1";
    } catch {
        return false;
    }
}

// Only enable Ollama when the UI points to a local backend.
(() => {
    const ollamaOpt = llmProviderSelect?.querySelector('option[value="ollama"]');
    if (!ollamaOpt) return;
    if (!isLocalBackend(BASE_URL)) {
        ollamaOpt.disabled = true;
        ollamaOpt.textContent = "Ollama (local only)";
    }
})();

// Load API key from localStorage
function loadApiKey() {
    const saved = localStorage.getItem("openai_api_key");
    if (saved) {
        apiKeyInput.value = saved;
        apiKeyStatus.textContent = "✓ API key loaded from storage";
        apiKeyStatus.style.color = "green";
    }
}

// Save and validate API key
apiKeyTestBtn.addEventListener("click", async () => {
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
        apiKeyStatus.textContent = "Please enter an API key";
        apiKeyStatus.style.color = "red";
        return;
    }

    apiKeyStatus.textContent = "Testing API key...";
    apiKeyStatus.style.color = "black";

    try {
        const response = await fetch(`${BASE_URL}/health`);
        if (response.ok) {
            localStorage.setItem("openai_api_key", apiKey);
            localStorage.setItem("api_key_test_time", new Date().toISOString());
            apiKeyStatus.textContent = "✓ API key saved successfully!";
            apiKeyStatus.style.color = "green";
        } else {
            apiKeyStatus.textContent = "Backend error. Check server.";
            apiKeyStatus.style.color = "red";
        }
    } catch (err) {
        apiKeyStatus.textContent = "Network error: " + err.message;
        apiKeyStatus.style.color = "red";
    }
});

// ---------------- Chat UI helpers ----------------

function appendMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = `p-3 my-2 rounded-lg max-w-[100%] whitespace-pre-wrap ${
        sender === "user" ? "bg-blue-200 ml-auto w-fit" : "bg-gray-200 mr-auto w-fit"
    }`;
    bubble.textContent = text;
    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function appendLoading() {
    const bubble = document.createElement("div");
    bubble.id = "loading";
    bubble.className = "p-3 my-2 rounded-lg bg-gray-200 mr-auto";
    bubble.textContent = "Thinking...";
    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeLoading() {
    const bubble = document.getElementById("loading");
    if (bubble) bubble.remove();
}

function displayMetrics(results) {
    metricsBox.innerHTML = "";
    
    if (!results || results.length === 0) {
        metricsBox.innerHTML = "<p class='text-gray-500'>No results</p>";
        return;
    }

    const title = document.createElement("p");
    title.className = "font-semibold text-xs mb-2";
    title.textContent = `Retrieved ${results.length} chunks:`;
    metricsBox.appendChild(title);

    results.forEach((item, idx) => {
        const container = document.createElement("div");
        container.className = "bg-white p-2 rounded border-l-2 border-blue-400 text-xs";
        
        const header = document.createElement("div");
        header.className = "font-semibold mb-1";
        header.textContent = `#${idx + 1} | Distance: ${item.distance.toFixed(4)}`;
        
        const text = document.createElement("p");
        text.className = "text-gray-700 line-clamp-3";
        text.textContent = item.text.substring(0, 150) + (item.text.length > 150 ? "..." : "");
        
        container.appendChild(header);
        container.appendChild(text);
        metricsBox.appendChild(container);
    });
}

// ---------------- File Upload ----------------

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function pollIndexStatus(jobId, { intervalMs = 2000, timeoutMs = 10 * 60 * 1000 } = {}) {
    const start = Date.now();
    let lastErr = null;
    while (true) {
        try {
            // Render free-tier cold starts and transient restarts can briefly return 502/503/504.
            const res = await fetch(`${BASE_URL}/index-status/${encodeURIComponent(jobId)}`, { cache: "no-store" });
            if (res.status === 502 || res.status === 503 || res.status === 504) {
                lastErr = new Error(`Backend temporarily unavailable (${res.status})`);
            } else if (!res.ok) {
                throw new Error(`Index status check failed (${res.status})`);
            } else {
                const data = await res.json();
                if (data.status === "completed") return data;
                if (data.status === "failed") {
                    throw new Error(data.error || "Indexing failed");
                }
            }
        } catch (err) {
            // If CORS is misconfigured or the service is still waking up, browsers report a generic fetch error.
            lastErr = err;
        }

        if (Date.now() - start > timeoutMs) {
            throw new Error(
                `Indexing timed out while waiting for completion. Last error: ${lastErr?.message || "Unknown"}`
            );
        }
        await sleep(intervalMs);
    }
}

uploadBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) {
        uploadStatus.textContent = "Please select a file first.";
        uploadStatus.style.color = "red";
        return;
    }

    uploadStatus.textContent = "Uploading and indexing...";
    uploadStatus.style.color = "black";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch(`${BASE_URL}/index-doc`, {
            method: "POST",
            body: formData,
        });

        const data = await res.json();
        
        // New behavior: /index-doc returns 202 + job_id and indexing happens in the background.
        if (data.job_id) {
            uploadStatus.textContent = "Indexing started... (This may take a bit on first request due to cold start)";
            uploadStatus.style.color = "black";

            const final = await pollIndexStatus(data.job_id);
            uploadStatus.textContent = `✓ Indexed! ${final.chunks_indexed} chunks, dimension: ${final.embedding_dim}`;
            uploadStatus.style.color = "green";
            metricsBox.innerHTML = "<p class='text-gray-500'>Ready to ask questions!</p>";
        } else if (data.chunks_indexed) {
            // Backward-compatible: if the API still responds synchronously.
            uploadStatus.textContent = `✓ Indexed! ${data.chunks_indexed} chunks, dimension: ${data.embedding_dim}`;
            uploadStatus.style.color = "green";
            metricsBox.innerHTML = "<p class='text-gray-500'>Ready to ask questions!</p>";
        } else {
            uploadStatus.textContent = "Error: " + (data.error || "Unknown error");
            uploadStatus.style.color = "red";
        }

    } catch (err) {
        uploadStatus.textContent = "Upload failed: " + (err?.message || err);
        uploadStatus.style.color = "red";
    }
});

// ---------------- Chat Send ----------------

async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    const apiKey = localStorage.getItem("openai_api_key");
    const llmProvider = llmProviderSelect.value;

    appendMessage(text, "user");
    input.value = "";

    appendLoading();

    try {
        // First, get the search results to show RAG metrics
        const searchRes = await fetch(`${BASE_URL}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: text, top_k: 3 }),
        });

        const searchData = await searchRes.json();

        // Display RAG metrics
        if (searchData.results) {
            displayMetrics(searchData.results);
        }

        // Then, get the generated answer
        const generateHeaders = { "Content-Type": "application/json" };
        if (apiKey) {
            generateHeaders["X-API-Key"] = apiKey;
        }

        const generateRes = await fetch(`${BASE_URL}/generate?llm_provider=${encodeURIComponent(llmProvider)}`, {
            method: "POST",
            headers: generateHeaders,
            body: JSON.stringify({ query: text, top_k: 3 }),
        });

        const generateData = await generateRes.json();

        removeLoading();

        if (generateData.response) {
            appendMessage(generateData.response, "bot");
        } else if (generateData.error) {
            appendMessage("Error: " + generateData.error, "bot");
        } else {
            appendMessage("Error: No response from server", "bot");
        }

    } catch (err) {
        removeLoading();
        appendMessage("Network Error: " + err.message, "bot");
    }
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
});

// Load API key on page load
loadApiKey();
