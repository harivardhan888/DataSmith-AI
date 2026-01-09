
const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const attachBtn = document.getElementById('attach-btn');
const fileInput = document.getElementById('file-upload');
const filePreview = document.getElementById('file-preview');
const fileNameSpan = document.getElementById('file-name'); // Renamed from fileName
const removeFileBtn = document.getElementById('remove-file');

let currentFile = null;

// Auto-focus input
userInput.focus();

// auto resize textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    if(this.value === '') this.style.height = 'auto';
});

// Event Listeners
userInput.addEventListener('keypress', (e) => { // Changed from keydown to keypress
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

attachBtn.addEventListener('click', () => fileInput.click());

// Handle file selection
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        currentFile = e.target.files[0];
        fileNameSpan.textContent = currentFile.name; // No truncation
        filePreview.classList.remove('hidden');
        // userInput.focus(); // Removed
    }
});

removeFileBtn.addEventListener('click', () => {
    currentFile = null;
    fileInput.value = '';
    filePreview.classList.add('hidden');
});

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text && !currentFile) return;

    // show user message
    addMessage(text, 'user', currentFile ? `[Attached: ${currentFile.name}]` : null);

    // Prepare Payload
    const formData = new FormData();
    formData.append('message', text);
    if (currentFile) {
        formData.append('file', currentFile);
    }
    
    // reset input
    userInput.value = '';
    userInput.style.height = 'auto'; // Reset height
    currentFile = null;
    fileInput.value = '';
    filePreview.classList.add('hidden');

    // Add Loading Stream
    const loadingId = addLoading();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        removeMessage(loadingId);
        
        if (data.status === 'success' || data.status === 'clarification_needed') {
            // display text
            addMessage(data.output, 'assistant', null, data.extracted_text);
        } else {
            addMessage("❌ Error: " + (data.output || "Unknown error"), 'assistant');
        }

    } catch (error) {
        removeMessage(loadingId);
        addMessage("❌ Connection Error.", 'assistant'); // Simplified error message
        console.log(error); // Changed from console.error to console.log
    }
}

function addMessage(text, role, attachmentName = null, hiddenContent = null) { // Parameter names changed
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'user' ? '👤' : 'AI';
    
    // Bubble
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    
    // Main text content (simple markdown parsing)
    let contentHtml = formatMarkdown(text);
    
    if (attachmentName) {
        contentHtml += `<div style="font-size:0.8em; opacity:0.7; margin-top:5px;">${attachmentName}</div>`;
    }

    bubble.innerHTML = contentHtml;

    // Extracted Content Section (for assistant)
    if (hiddenContent && hiddenContent.length > 20) {
        const extractDiv = document.createElement('div');
        extractDiv.className = 'extracted-content';
        
        const header = document.createElement('div');
        header.className = 'extracted-header';
        header.innerHTML = `<span>📄 Extracted Content</span> <span>▼</span>`;
        
        const body = document.createElement('div');
        body.className = 'extracted-body';
        body.textContent = hiddenContent; // Text content to stay safe (no html injection)

        header.addEventListener('click', () => {
            body.classList.toggle('open');
            header.children[1].textContent = body.classList.contains('open') ? '▲' : '▼';
        });

        extractDiv.appendChild(header);
        extractDiv.appendChild(body);
        bubble.appendChild(extractDiv);
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    chatContainer.appendChild(msgDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addLoading() {
    const id = 'loading-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = `message assistant`;
    msgDiv.id = id;
    
    msgDiv.innerHTML = `
        <div class="avatar">AI</div>
        <div class="bubble">
            <span class="typing-indicator">Thinking...</span>
        </div>
    `;
    
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function formatMarkdown(text) {
    if (!text) return '';
    // Very basic markdown formatter
    // 1. Newlines
    let html = text.replace(/\n/g, '<br>');
    // 2. Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // 3. Code blocks (simple)
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    // 4. Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    // 5. Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color: #60a5fa">$1</a>');
    
    return html;
}
