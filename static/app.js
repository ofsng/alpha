document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const ideaInput = document.getElementById('idea');
    const modelSelect = document.getElementById('modelSelect');
    const loopCountInput = document.getElementById('loopCount');
    const messagesContainer = document.getElementById('messagesContainer');
    const placeholderMessage = document.getElementById('placeholderMessage');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');

    let ws = null;

    startBtn.addEventListener('click', () => {
        const idea = ideaInput.value.trim();
        if(!idea) {
            alert("Lütfen bir fikir veya problem yazın.");
            return;
        }

        // Reset UI
        messagesContainer.innerHTML = '';
        placeholderMessage.style.opacity = '0';
        setTimeout(() => placeholderMessage.style.display = 'none', 300);
        
        startBtn.disabled = true;
        startBtn.textContent = "Tartışma Sürüyor...";
        statusIndicator.classList.add('active');
        statusText.textContent = "İşleniyor...";

        // WebSocket Connection
        // Determine correct ws protocol
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/debate`;
        
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            const config = {
                idea: idea,
                model: modelSelect.value,
                loops: parseInt(loopCountInput.value) || 5
            };
            ws.send(JSON.stringify(config));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            appendMessage(data.agent, data.message);
            
            if (data.agent === "System" && data.message.includes("Tamamlandı")) {
                finishDebate();
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket Hatası:", error);
            appendMessage("System_Error", "Bağlantı hatası oluştu.");
            finishDebate();
        };

        ws.onclose = () => {
            finishDebate();
        };
    });

    function appendMessage(agent, text) {
        // If it's a System_Status message, we might want to remove the previous System_Status 
        // to avoid clutter if desired, but let's keep it simple and just append.
        
        const msgDiv = document.createElement('div');
        msgDiv.className = `message agent-${agent}`;
        
        let headerHTML = '';
        if (agent !== 'System' && agent !== 'System_Status' && agent !== 'System_Error') {
            headerHTML = `<div class="message-header">${agent}</div>`;
        }

        // Render Markdown using marked.js
        const htmlContent = marked.parse(text);

        msgDiv.innerHTML = `
            ${headerHTML}
            <div class="message-content">${htmlContent}</div>
        `;
        
        messagesContainer.appendChild(msgDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function finishDebate() {
        startBtn.disabled = false;
        startBtn.textContent = "Yeni Tartışma Başlat";
        statusIndicator.classList.remove('active');
        statusText.textContent = "Bekleniyor...";
        if(ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
        }
    }
});
