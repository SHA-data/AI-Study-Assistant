// --- Global Variables & Initialization ---
let memberName = getCookie('member_name');
let conversationId = generateUUID(); // Simple session ID for chat

document.addEventListener('DOMContentLoaded', () => {
    initMemberIdentity();
    
    // Page specific initialization
    if (document.getElementById('chat-thread')) {
        initChat();
        initParticleSphere();
    }
    if (document.getElementById('upload-zone')) {
        initResourceCenter();
    }
});

// --- UI Utilities ---
function showToast(message, isError = false) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${isError ? 'error' : ''}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function setCookie(name, value) {
    document.cookie = `${name}=${value};path=/;max-age=31536000`; // 1 year
}

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// --- Member Identity ---
function initMemberIdentity() {
    const modal = document.getElementById('welcome-modal');
    const input = document.getElementById('name-input');
    const saveBtn = document.getElementById('save-name-btn');
    
    function updateSidebarName() {
        if (memberName) {
            document.getElementById('display-member-name').textContent = memberName;
            document.getElementById('avatar-initials').textContent = memberName.substring(0, 2).toUpperCase();
        }
    }

    if (!memberName) {
        modal.classList.remove('hidden');
        input.focus();
    } else {
        updateSidebarName();
    }

    saveBtn.addEventListener('click', () => {
        const name = input.value.trim();
        if (name) {
            memberName = name;
            setCookie('member_name', name);
            modal.classList.add('hidden');
            updateSidebarName();
            if (document.getElementById('upload-zone')) {
                 renderMetadataFlow(document.querySelector('.type-pill.active').dataset.type); // Refresh namespace selector
            }
        }
    });

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') saveBtn.click();
    });

    // Handle clicking member identity to change name
    document.getElementById('member-identity-btn').addEventListener('click', () => {
        input.value = memberName || '';
        modal.classList.remove('hidden');
        input.focus();
    });
}

// --- Dynamic Subjects and Groups ---
let defaultSubjects = ["DBMS", "Linear Algebra", "Theory of Automata", "Computer Networks", "Artificial Intelligence"];
let defaultGroups = ["Study Group 1", "Study Group 2"];

let subjects = JSON.parse(localStorage.getItem('subjects')) || defaultSubjects;
let studyGroups = JSON.parse(localStorage.getItem('studyGroups')) || defaultGroups;

function saveSidebarState() {
    localStorage.setItem('subjects', JSON.stringify(subjects));
    localStorage.setItem('studyGroups', JSON.stringify(studyGroups));
    renderSidebarPills();
}

function renderSidebarPills() {
    const subjectsContainer = document.getElementById('subjects-container');
    const groupsContainer = document.getElementById('groups-container');
    if (!subjectsContainer || !groupsContainer) return;
    
    let savedSubject = sessionStorage.getItem('activeSubject') || "DBMS";
    
    subjectsContainer.innerHTML = '';
    subjects.forEach((subj, idx) => {
        const btn = document.createElement('button');
        btn.className = `sidebar-pill ${subj === savedSubject ? 'active' : ''}`;
        btn.innerHTML = `<span>${subj}</span> <span class="delete-pill" data-type="subject" data-idx="${idx}" style="font-size: 10px; margin-left: 8px; opacity: 0.5;">✕</span>`;
        subjectsContainer.appendChild(btn);
    });

    groupsContainer.innerHTML = '';
    studyGroups.forEach((grp, idx) => {
        const btn = document.createElement('button');
        btn.className = `sidebar-pill ${grp === savedSubject ? 'active' : ''}`;
        btn.innerHTML = `<span>${grp}</span> <span class="delete-pill" data-type="group" data-idx="${idx}" style="font-size: 10px; margin-left: 8px; opacity: 0.5;">✕</span>`;
        groupsContainer.appendChild(btn);
    });
    
    bindSidebarEvents();
}

function bindSidebarEvents() {
    const subjectNameSpan = document.getElementById('chat-subject-name');
    
    document.querySelectorAll('#subjects-container .sidebar-pill, #groups-container .sidebar-pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-pill')) {
                e.stopPropagation();
                if (confirm(`Are you sure you want to delete this tab? (Files will remain in the database)`)) {
                    const type = e.target.dataset.type;
                    const idx = e.target.dataset.idx;
                    if (type === 'subject') {
                        subjects.splice(idx, 1);
                    } else {
                        studyGroups.splice(idx, 1);
                    }
                    saveSidebarState();
                }
                return;
            }
            
            document.querySelectorAll('.sidebar-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            
            const subjectTag = pill.querySelector('span').textContent.trim();
            if (subjectNameSpan) subjectNameSpan.textContent = subjectTag;
            
            sessionStorage.setItem('activeSubject', subjectTag);
            
            restoreChatHistory(subjectTag);
        });
    });
}

// --- Chat Logic ---
const chatHistories = JSON.parse(sessionStorage.getItem('chatHistories')) || {};

function initChat() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const subjectNameSpan = document.getElementById('chat-subject-name');
    
    let savedSubject = sessionStorage.getItem('activeSubject');
    if (savedSubject && subjectNameSpan) {
        subjectNameSpan.textContent = savedSubject;
    }

    let subjectTag = subjectNameSpan ? subjectNameSpan.textContent.trim() : "DBMS";
    
    if (!chatHistories[subjectTag]) {
        chatHistories[subjectTag] = [];
        sessionStorage.setItem('chatHistories', JSON.stringify(chatHistories));
    }
    
    restoreChatHistory(subjectTag);
    renderSidebarPills();

    // Add event listeners for the '+' buttons
    document.querySelectorAll('.add-pill-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const type = e.target.dataset.type;
            const name = prompt(`Enter new ${type} name:`);
            if (name && name.trim()) {
                const cleanName = name.trim();
                if (type === 'subject') {
                    if (!subjects.includes(cleanName)) subjects.push(cleanName);
                } else {
                    if (!studyGroups.includes(cleanName)) studyGroups.push(cleanName);
                }
                saveSidebarState();
            }
        });
    });

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const memberName = getCookie('member_name');
    if (!chatInput) return;

    const message = chatInput.value.trim();
    if (!message || !memberName) return;

    const currentSubject = sessionStorage.getItem('activeSubject') || "DBMS";

    chatInput.value = '';
    appendMessage(message, 'user');
    
    if (!chatHistories[currentSubject]) chatHistories[currentSubject] = [];
    chatHistories[currentSubject].push({ role: 'user', text: message });
    sessionStorage.setItem('chatHistories', JSON.stringify(chatHistories));

    const loadingDots = appendLoading();

    try {
        let isolatedNamespace = `${memberName}_${currentSubject}`;
        isolatedNamespace = isolatedNamespace.replace(/[^a-zA-Z0-9_-]/g, '_');
        
        const res = await fetch(`${BACKEND_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message, 
                namespace: isolatedNamespace, 
                member_name: memberName, 
                conversation_id: conversationId,
                subject: currentSubject
            })
        });
        
        loadingDots.remove();
        
        if (!res.ok) throw new Error('Network response was not ok');
        const data = await res.json();
        
        if (data.error) throw new Error(data.error);
        
        appendMessage(data.answer, 'assistant', data.sources);
        
        chatHistories[currentSubject].push({ role: 'assistant', text: data.answer, sources: data.sources });
        sessionStorage.setItem('chatHistories', JSON.stringify(chatHistories));
        
    } catch (error) {
        if (loadingDots) loadingDots.remove();
        showToast("Failed to send message.", true);
        console.error(error);
    }
}

function restoreChatHistory(subject) {
    const thread = document.getElementById('chat-thread');
    if (!thread) return;
    thread.innerHTML = '';
    
    if (chatHistories[subject]) {
        chatHistories[subject].forEach(msg => {
            appendMessage(msg.text, msg.role, msg.sources);
        });
    }
}

function appendMessage(text, sender, sources = []) {
    const thread = document.getElementById('chat-thread');
    if (!thread) return;
    const wrap = document.createElement('div');
    wrap.className = 'message-wrap';
    
    if (sender === 'user') {
        const bubble = document.createElement('div');
        bubble.className = 'message-user';
        bubble.textContent = text;
        wrap.appendChild(bubble);
    } else {
        const group = document.createElement('div');
        group.className = 'message-assistant-group';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-assistant';
        if (window.marked) {
            bubble.innerHTML = marked.parse(text);
        } else {
            bubble.textContent = text;
        }
        group.appendChild(bubble);
        
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            const prefix = document.createElement('span');
            prefix.style.fontSize = '11px';
            prefix.style.color = 'var(--color-text-secondary)';
            prefix.textContent = 'Sources: ';
            sourcesDiv.appendChild(prefix);
            
            const uniqueTitles = [...new Set(sources.map(s => s.title))];
            uniqueTitles.forEach(title => {
                const pill = document.createElement('span');
                pill.className = 'source-pill';
                pill.textContent = title;
                sourcesDiv.appendChild(pill);
            });
            group.appendChild(sourcesDiv);
        }
        wrap.appendChild(group);
    }
    
    thread.appendChild(wrap);
    thread.scrollTop = thread.scrollHeight;
}

function appendLoading() {
    const thread = document.getElementById('chat-thread');
    if (!thread) return null;
    const wrap = document.createElement('div');
    wrap.className = 'message-wrap';
    wrap.innerHTML = `
        <div class="message-assistant-group">
            <div class="message-assistant loading-dots">
                <div class="dot"></div><div class="dot"></div><div class="dot"></div>
            </div>
        </div>
    `;
    thread.appendChild(wrap);
    thread.scrollTop = thread.scrollHeight;
    return wrap;
}

// --- Resource Center Logic ---
let currentUploadType = 'pdf';
let selectedFile = null;

function initResourceCenter() {
    document.querySelectorAll('.type-pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
            e.stopPropagation(); 
            document.querySelectorAll('.type-pill').forEach(p => p.classList.remove('active'));
            e.target.classList.add('active');
            currentUploadType = e.target.dataset.type;
            selectedFile = null;
            renderMetadataFlow(currentUploadType);
        });
    });

    const dropZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');

    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        ['dragleave', 'dragend'].forEach(type => {
            dropZone.addEventListener(type, () => dropZone.classList.remove('dragover'));
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            if (currentUploadType === 'pdf' || currentUploadType === 'pptx') {
                if (e.dataTransfer.files.length) {
                    const file = e.dataTransfer.files[0];
                    if (currentUploadType === 'pdf' && (file.type === "application/pdf" || file.name.endsWith('.pdf'))) {
                        selectedFile = file;
                        renderMetadataFlow('pdf');
                    } else if (currentUploadType === 'pptx' && (file.name.endsWith('.pptx') || file.type.includes('presentation'))) {
                        selectedFile = file;
                        renderMetadataFlow('pptx');
                    } else {
                        showToast(`Only ${currentUploadType.toUpperCase()} files are allowed for this type.`, true);
                    }
                }
            }
        });

        dropZone.addEventListener('click', () => {
            if (currentUploadType === 'pdf') {
                fileInput.accept = ".pdf";
                fileInput.click();
            } else if (currentUploadType === 'pptx') {
                fileInput.accept = ".pptx";
                fileInput.click();
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                selectedFile = e.target.files[0];
                renderMetadataFlow(currentUploadType);
            }
        });
    }

    const toggleBtn = document.getElementById('col-toggle-btn');
    const toggleMenu = document.getElementById('col-toggle-menu');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
            toggleMenu.classList.toggle('hidden');
            e.stopPropagation();
        });
        document.addEventListener('click', () => toggleMenu.classList.add('hidden'));
        toggleMenu.addEventListener('click', e => e.stopPropagation());
    }

    document.querySelectorAll('.col-toggle').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const colIndex = e.target.dataset.col;
            const display = e.target.checked ? '' : 'none';
            const th = document.querySelector(`th[data-col="${colIndex}"]`);
            if (th) th.style.display = display;
            document.querySelectorAll(`#uploads-tbody tr`).forEach(row => {
                if (row.children[colIndex]) row.children[colIndex].style.display = display;
            });
        });
    });

    const tableSearch = document.getElementById('table-search');
    if (tableSearch) {
        tableSearch.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('#uploads-tbody tr').forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });
    }

    fetchLibrary();
}

function getNamespaceOptions() {
    return `
        <option value="${memberName}">${memberName}</option>
        <option value="shared">Shared Library</option>
    `;
}

function getSubjectOptions() {
    let options = '';
    subjects.forEach(s => options += `<option value="${s}">${s}</option>`);
    studyGroups.forEach(s => options += `<option value="${s}">${s}</option>`);
    return options;
}

function renderMetadataFlow(type) {
    const flow = document.getElementById('metadata-flow');
    if (!flow) return;
    flow.innerHTML = '';
    
    if ((type === 'pdf' || type === 'pptx') && !selectedFile) {
        flow.classList.add('hidden');
        return;
    }
    
    flow.classList.remove('hidden');

    if (type === 'pdf' || type === 'pptx') {
        let ext = type === 'pdf' ? '.pdf' : '.pptx';
        flow.innerHTML = `
            <div class="meta-input-group">
                <span style="font-weight: 500;">[ ${selectedFile.name} ]</span>
            </div>
            <div style="display: flex; gap: 12px; margin-bottom: 12px;">
                <div class="meta-input-group" style="flex: 1; margin-bottom: 0;">
                    <label>Namespace:</label>
                    <select id="meta-namespace" class="meta-select">${getNamespaceOptions()}</select>
                </div>
                <div class="meta-input-group" style="flex: 1; margin-bottom: 0;">
                    <label>Subject:</label>
                    <select id="meta-subject" class="meta-select">${getSubjectOptions()}</select>
                </div>
            </div>
            <div class="meta-input-group">
                <label>Title:</label>
                <input type="text" id="meta-title" class="meta-input" value="${selectedFile.name.replace(ext, '')}">
            </div>
            <button class="btn-primary" onclick="submitUpload('${type}')">Upload</button>
        `;
    } else if (type === 'text') {
        flow.innerHTML = `
            <div style="width: 100%; max-width: 600px;">
                <input type="text" id="meta-title" class="meta-input" placeholder="Title" style="width: 100%; margin-bottom: 12px;">
                <textarea id="meta-text" class="meta-textarea" placeholder="Paste or type your text here..."></textarea>
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px;">
                    <div style="display: flex; gap: 12px; flex: 1;">
                        <div class="meta-input-group" style="margin-bottom: 0; flex: 1;">
                            <label>Namespace:</label>
                            <select id="meta-namespace" class="meta-select">${getNamespaceOptions()}</select>
                        </div>
                        <div class="meta-input-group" style="margin-bottom: 0; flex: 1;">
                            <label>Subject:</label>
                            <select id="meta-subject" class="meta-select">${getSubjectOptions()}</select>
                        </div>
                    </div>
                    <button class="btn-primary" onclick="submitUpload('text')">Submit</button>
                </div>
            </div>
        `;
    }
}

async function submitUpload(type) {
    const baseNamespace = document.getElementById('meta-namespace').value;
    const subject = document.getElementById('meta-subject').value;
    const title = document.getElementById('meta-title').value;
    
    let namespace = baseNamespace === 'shared' ? 'shared' : `${baseNamespace}_${subject}`;
    namespace = namespace.replace(/[^a-zA-Z0-9_-]/g, '_');
    
    if (!title || !baseNamespace || !subject) {
        showToast("Please fill all required fields", true);
        return;
    }

    try {
        let res;
        if (type === 'pdf') {
            const form = new FormData();
            form.append('file', selectedFile);
            form.append('namespace', namespace);
            form.append('title', title);
            res = await fetch(`${BACKEND_URL}/ingest/pdf`, { method: 'POST', body: form });
        } else if (type === 'pptx') {
            const form = new FormData();
            form.append('file', selectedFile);
            form.append('namespace', namespace);
            form.append('title', title);
            res = await fetch(`${BACKEND_URL}/ingest/pptx`, { method: 'POST', body: form });
        } else if (type === 'text') {
            const text = document.getElementById('meta-text').value;
            if (!text) { showToast("Please enter text", true); return; }
            res = await fetch(`${BACKEND_URL}/ingest/text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, namespace, title })
            });
        }

        if (!res.ok) throw new Error("Upload failed");
        const data = await res.json();
        if (data.error) throw new Error(data.error);

        showToast("Upload successful!");
        selectedFile = null;
        renderMetadataFlow(currentUploadType);
        fetchLibrary();

    } catch (error) {
        showToast(error.message || "An error occurred", true);
        console.error(error);
    }
}

async function fetchLibrary() {
    const tbody = document.getElementById('uploads-tbody');
    if (!tbody) return;
    try {
        const res = await fetch(`${BACKEND_URL}/library`);
        if (!res.ok) return;
        const data = await res.json();
        
        tbody.innerHTML = '';
        
        if (data.documents && data.documents.length > 0) {
            data.documents.forEach(doc => {
                const date = new Date(doc.created_at);
                const dateStr = `${date.getDate()}-${date.getMonth()+1}-${date.getFullYear()}`;
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${doc.title}</td>
                    <td data-col="1"><span class="format-badge">${doc.doc_type.toUpperCase()}</span></td>
                    <td data-col="2">${doc.namespace}</td>
                    <td data-col="3">${dateStr}</td>
                    <td>
                        <div class="table-actions">
                            <button class="action-icon" onclick="showToast('Link copied!')" aria-label="Copy link">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                                </svg>
                            </button>
                            <button class="action-icon" onclick="deleteDoc(${doc.id}, this)" aria-label="Delete">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                </svg>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            document.querySelectorAll('.col-toggle').forEach(checkbox => {
                checkbox.dispatchEvent(new Event('change'));
            });
        } else {
             tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--color-text-muted);">No uploads found.</td></tr>';
        }
    } catch (error) {
        console.error("Failed to fetch library", error);
    }
}

function deleteDoc(id, btnElement) {
    const originalContent = btnElement.parentElement.innerHTML;
    const actionsDiv = btnElement.parentElement;
    
    actionsDiv.innerHTML = `
        <span style="font-size: 11px; margin-right: 8px;">Delete?</span>
        <button class="action-icon" style="color: var(--color-pink-deep); font-weight: bold; margin-right: 8px;" onclick="confirmDelete(${id}, this.parentElement.parentElement.parentElement)">Yes</button>
        <button class="action-icon" onclick="cancelDelete(this.parentElement, \`${originalContent.replace(/"/g, '&quot;')}\`)">No</button>
    `;
}

function cancelDelete(actionsDiv, originalContent) {
    actionsDiv.innerHTML = originalContent;
}

async function confirmDelete(id, trElement) {
    try {
        const res = await fetch(`${BACKEND_URL}/library/${id}`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error("Delete failed");
        
        showToast("File deleted successfully.");
        trElement.remove();
    } catch (error) {
        showToast("Failed to delete file", true);
        console.error(error);
    }
}

function initParticleSphere() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    let width, height;
    const particles = [];
    const particleCount = 280;
    const sphereRadius = 220;
    
    function resize() {
        const parent = canvas.parentElement;
        if (!parent) return;
        
        width = parent.clientWidth || window.innerWidth;
        height = parent.clientHeight || window.innerHeight;
        
        canvas.width = width;
        canvas.height = height;
    }
    
    window.addEventListener('resize', resize);
    setTimeout(resize, 100);
    
    for (let i = 0; i < particleCount; i++) {
        const phi = Math.acos(-1 + (2 * i) / particleCount);
        const theta = Math.sqrt(particleCount * Math.PI) * phi;
        
        particles.push({
            x: sphereRadius * Math.cos(theta) * Math.sin(phi),
            y: sphereRadius * Math.sin(theta) * Math.sin(phi),
            z: sphereRadius * Math.cos(phi)
        });
    }
    
    let angleX = 0.0012;
    let angleY = 0.0012;
    
    function rotateX(p, angle) {
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        const y = p.y * cos - p.z * sin;
        const z = p.y * sin + p.z * cos;
        p.y = y;
        p.z = z;
    }
    
    function rotateY(p, angle) {
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        const x = p.x * cos - p.z * sin;
        const z = p.x * sin + p.z * cos;
        p.x = x;
        p.z = z;
    }
    
    function animate() {
        if (!width || !height) {
            requestAnimationFrame(animate);
            return;
        }

        ctx.clearRect(0, 0, width, height);
        
        const perspective = 450;
        const centerX = width / 2;
        const centerY = height / 2;
        
        const sortedParticles = [...particles].sort((a, b) => b.z - a.z);
        
        sortedParticles.forEach(p => {
            rotateX(p, angleX);
            rotateY(p, angleY);
            
            const original = particles.find(orig => orig.x === p.x && orig.y === p.y && orig.z === p.z);
            if (original) {
                original.x = p.x;
                original.y = p.y;
                original.z = p.z;
            }

            const scale = perspective / (perspective + p.z);
            const x2d = p.x * scale + centerX;
            const y2d = p.y * scale + centerY;
            
            const alpha = 0.2 + 0.6 * ((p.z + sphereRadius) / (2 * sphereRadius));
            ctx.fillStyle = `rgba(244, 167, 185, ${alpha})`;
            
            ctx.beginPath();
            ctx.arc(x2d, y2d, scale * 2.2, 0, Math.PI * 2);
            ctx.fill();
            
            if (p.z > sphereRadius * 0.5) {
                ctx.shadowBlur = 5;
                ctx.shadowColor = 'rgba(244, 167, 185, 0.5)';
            } else {
                ctx.shadowBlur = 0;
            }
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
}
