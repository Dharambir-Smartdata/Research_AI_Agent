/**
 * ResearchMatrix AI Agent - Frontend Application Logic
 * Ultra-Responsive, Zero-Bloat, Native Vanilla ES6
 */

document.addEventListener('DOMContentLoaded', () => {
    // State
    let lastReport = null;
    let isResearching = false;
    let progressTimer = null;
    let currentSeconds = 0;
    let reportsData = [];
    let uploadsData = [];
    let activeFilter = 'all';
    let currentConversationId = null;
    let conversationsData = [];
    let attachedFiles = [];
    let currentActiveDocument = null;

    // DOM Elements
    const chatContainer = document.getElementById('chat-container');
    const welcomeHero = document.getElementById('welcome-hero');
    const chatForm = document.getElementById('chat-form');
    const promptInput = document.getElementById('prompt-input');
    const sendBtn = document.getElementById('send-btn');
    const uploadFileBtn = document.getElementById('upload-file-btn');
    const fileUploadInput = document.getElementById('file-upload-input');
    const attachedFileBar = document.getElementById('attached-file-bar');
    const attachedFileName = document.getElementById('attached-file-name');
    const attachedFileSize = document.getElementById('attached-file-size');
    const removeAttachedFileBtn = document.getElementById('remove-attached-file-btn');
    const reportsDrawer = document.getElementById('reports-drawer');
    const drawerBackdrop = document.getElementById('drawer-backdrop');
    const toggleDrawerBtn = document.getElementById('toggle-drawer-btn');
    const closeDrawerBtn = document.getElementById('close-drawer-btn');
    const reportsList = document.getElementById('reports-list');
    const reportsCountBadge = document.getElementById('reports-count-badge');
    const drawerCountBadge = document.getElementById('drawer-count-badge');
    const reportSearch = document.getElementById('report-search');
    const filterTabs = document.querySelectorAll('.filter-tab');
    const previewModal = document.getElementById('preview-modal');
    const closePreviewBtn = document.getElementById('close-preview-btn');
    const previewTitle = document.getElementById('preview-title');
    const previewContent = document.getElementById('preview-content');
    const previewDownloadBtn = document.getElementById('preview-download-btn');
    const resetSessionBtn = document.getElementById('reset-session-btn');
    const agentStatusPill = document.getElementById('agent-status-pill');

    // Conversation History Elements
    const historyDrawer = document.getElementById('history-drawer');
    const toggleHistoryBtn = document.getElementById('toggle-history-btn');
    const closeHistoryBtn = document.getElementById('close-history-btn');
    const historyList = document.getElementById('history-list');
    const historyCountBadge = document.getElementById('history-count-badge');
    const historySearch = document.getElementById('history-search');
    const historyNewChatBtn = document.getElementById('history-new-chat-btn');
    const clearAllHistoryBtn = document.getElementById('clear-all-history-btn');

    // Theme Switcher Elements
    const themeToggleBtn = document.getElementById('theme-toggle-btn');

    function updateThemeUI() {
        const isDark = document.documentElement.classList.contains('dark');
        if (themeToggleBtn) {
            themeToggleBtn.title = isDark ? "Current: Dark Mode (Click for Light Mode)" : "Current: Light Mode (Click for Dark Mode)";
            themeToggleBtn.innerHTML = isDark
                ? `<i data-lucide="moon" class="w-4 h-4 text-indigo-400"></i>`
                : `<i data-lucide="sun" class="w-4 h-4 text-amber-500"></i>`;
        }
        if (window.lucide) lucide.createIcons();
    }

    function toggleTheme() {
        const isDark = document.documentElement.classList.contains('dark');
        if (isDark) {
            document.documentElement.classList.remove('dark');
            document.documentElement.classList.add('light');
            localStorage.setItem('omni_theme', 'light');
            showToast('Switched to Light Mode', 'info');
        } else {
            document.documentElement.classList.remove('light');
            document.documentElement.classList.add('dark');
            localStorage.setItem('omni_theme', 'dark');
            showToast('Switched to Dark Mode', 'info');
        }
        updateThemeUI();
        renderReportsList();
        renderHistoryList();
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
    updateThemeUI();

    // Configure Marked.js for safe, beautiful markdown rendering
    if (window.marked) {
        marked.setOptions({
            breaks: true,
            gfm: true,
            headerIds: false,
            highlight: function(code, lang) {
                if (window.hljs) {
                    if (lang && hljs.getLanguage(lang)) {
                        try { return hljs.highlight(code, { language: lang }).value; } catch (e) {}
                    }
                    try { return hljs.highlightAuto(code).value; } catch (e) {}
                }
                return code;
            }
        });
    }

    // Auto-grow textarea
    promptInput.addEventListener('input', () => {
        promptInput.style.height = 'auto';
        promptInput.style.height = Math.min(promptInput.scrollHeight, 160) + 'px';
    });

    // Enter to send (Shift+Enter for new line)
    promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Quick suggestion cards
    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', () => {
            const prompt = card.getAttribute('data-prompt');
            if (prompt && !isResearching) {
                promptInput.value = prompt;
                promptInput.style.height = 'auto';
                promptInput.style.height = Math.min(promptInput.scrollHeight, 160) + 'px';
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });

    // Drawer toggles
    function openReportsDrawer() {
        closeHistoryDrawer();
        reportsDrawer.classList.remove('translate-x-full');
        drawerBackdrop.classList.remove('hidden');
        setTimeout(() => drawerBackdrop.classList.add('opacity-100'), 10);
    }

    function closeReportsDrawer() {
        reportsDrawer.classList.add('translate-x-full');
        checkBackdrop();
    }

    function openHistoryDrawer() {
        closeReportsDrawer();
        historyDrawer.classList.remove('-translate-x-full');
        drawerBackdrop.classList.remove('hidden');
        setTimeout(() => drawerBackdrop.classList.add('opacity-100'), 10);
    }

    function closeHistoryDrawer() {
        historyDrawer.classList.add('-translate-x-full');
        checkBackdrop();
    }

    function checkBackdrop() {
        setTimeout(() => {
            if (reportsDrawer.classList.contains('translate-x-full') && 
                historyDrawer.classList.contains('-translate-x-full')) {
                drawerBackdrop.classList.remove('opacity-100');
                drawerBackdrop.classList.add('hidden');
            }
        }, 150);
    }

    toggleDrawerBtn.addEventListener('click', openReportsDrawer);
    closeDrawerBtn.addEventListener('click', closeReportsDrawer);
    toggleHistoryBtn.addEventListener('click', openHistoryDrawer);
    closeHistoryBtn.addEventListener('click', closeHistoryDrawer);
    drawerBackdrop.addEventListener('click', () => {
        closeReportsDrawer();
        closeHistoryDrawer();
    });

    historySearch.addEventListener('input', () => {
        renderHistoryList();
    });

    // Report Drawer Search & Filter Tabs Listeners
    const clearReportSearchBtn = document.getElementById('clear-report-search-btn');

    if (reportSearch) {
        reportSearch.addEventListener('input', () => {
            if (clearReportSearchBtn) {
                if (reportSearch.value.trim().length > 0) {
                    clearReportSearchBtn.classList.remove('hidden');
                } else {
                    clearReportSearchBtn.classList.add('hidden');
                }
            }
            renderReportsList();
        });
        reportSearch.addEventListener('keyup', () => {
            renderReportsList();
        });
    }

    if (clearReportSearchBtn) {
        clearReportSearchBtn.addEventListener('click', () => {
            if (reportSearch) {
                reportSearch.value = '';
                clearReportSearchBtn.classList.add('hidden');
                renderReportsList();
                reportSearch.focus();
            }
        });
    }

    function updateFilterTabsUI() {
        filterTabs.forEach(t => {
            const f = t.getAttribute('data-filter');
            if (f === activeFilter) {
                t.className = 'filter-tab px-3 py-1 rounded-lg bg-[#5850ec] text-white font-medium text-xs shadow-sm transition-all';
            } else {
                t.className = 'filter-tab px-3 py-1 rounded-lg bg-slate-200/80 dark:bg-[#121622] border border-slate-300/50 dark:border-[#1e2436] text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all text-xs font-medium';
            }
        });
    }

    filterTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            activeFilter = tab.getAttribute('data-filter') || 'all';
            updateFilterTabsUI();
            renderReportsList();
        });
    });

    // File Attachment & Drag/Drop Upload Handlers
    function renderAttachedFiles() {
        if (!attachedFileBar) return;
        if (!attachedFiles.length) {
            attachedFileBar.classList.add('hidden');
            attachedFileBar.classList.remove('flex');
            attachedFileBar.innerHTML = '';
            return;
        }
        attachedFileBar.classList.remove('hidden');
        attachedFileBar.classList.add('flex');
        attachedFileBar.innerHTML = attachedFiles.map((f, i) => `
            <div class="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-indigo-500/15 border border-indigo-500/30 text-[11px] font-medium text-slate-800 dark:text-slate-200">
                <i data-lucide="file-text" class="w-3 h-3 text-indigo-500 flex-shrink-0"></i>
                <span class="max-w-[130px] truncate" title="${escapeHtml(f.filename)}">${escapeHtml(f.filename)}</span>
                <span class="text-[9px] text-slate-400 font-mono">${escapeHtml(f.size_human)}</span>
                <button type="button" data-remove-idx="${i}" class="p-0.5 rounded text-slate-400 hover:text-rose-500 hover:bg-rose-500/10 transition-colors ml-0.5" title="Remove">
                    <i data-lucide="x" class="w-3 h-3"></i>
                </button>
            </div>
        `).join('');
        if (window.lucide) lucide.createIcons();
    }

    if (attachedFileBar) {
        attachedFileBar.addEventListener('click', (e) => {
            const btn = e.target.closest('button[data-remove-idx]');
            if (btn) {
                const idx = parseInt(btn.getAttribute('data-remove-idx'), 10);
                if (!isNaN(idx) && idx >= 0 && idx < attachedFiles.length) {
                    attachedFiles.splice(idx, 1);
                    renderAttachedFiles();
                }
            }
        });
    }

    async function handleFilesUpload(filesList) {
        if (!filesList || !filesList.length) return;
        const formData = new FormData();
        Array.from(filesList).forEach(f => formData.append('files', f));

        try {
            showToast(`Uploading ${filesList.length} file${filesList.length > 1 ? 's' : ''}...`, 'info');
            const res = await fetch('/api/upload/', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (data.status === 'success') {
                const newFiles = data.files || [data];
                attachedFiles.push(...newFiles);
                renderAttachedFiles();
                showToast(`Attached ${newFiles.length} file${newFiles.length > 1 ? 's' : ''}`, 'success');
                promptInput.focus();
            } else {
                showToast(data.message || 'File upload failed', 'error');
            }
        } catch (err) {
            showToast('Upload network error', 'error');
        }
    }

    if (uploadFileBtn && fileUploadInput) {
        uploadFileBtn.addEventListener('click', () => {
            fileUploadInput.click();
        });

        fileUploadInput.addEventListener('change', (e) => {
            const files = e.target.files;
            if (files && files.length) {
                handleFilesUpload(files);
            }
            fileUploadInput.value = '';
        });
    }

    // Drag and Drop support on chatForm
    if (chatForm) {
        ['dragenter', 'dragover'].forEach(name => {
            chatForm.addEventListener(name, (e) => {
                e.preventDefault();
                e.stopPropagation();
                chatForm.classList.add('ring-2', 'ring-indigo-500/60', 'border-indigo-500/60');
            });
        });

        ['dragleave', 'drop'].forEach(name => {
            chatForm.addEventListener(name, (e) => {
                e.preventDefault();
                e.stopPropagation();
                chatForm.classList.remove('ring-2', 'ring-indigo-500/60', 'border-indigo-500/60');
            });
        });

        chatForm.addEventListener('drop', (e) => {
            const files = e.dataTransfer && e.dataTransfer.files;
            if (files && files.length) {
                handleFilesUpload(files);
            }
        });
    }

    historyNewChatBtn.addEventListener('click', () => {
        closeHistoryDrawer();
        startNewThread();
    });

    if (closePreviewBtn) {
        closePreviewBtn.addEventListener('click', () => {
            if (previewModal) previewModal.classList.add('hidden');
        });
    }

    if (previewModal) {
        previewModal.addEventListener('click', (e) => {
            if (e.target === previewModal) {
                previewModal.classList.add('hidden');
            }
        });
    }

    // Custom Delete Confirmation Modal Logic
    const deleteModal = document.getElementById('delete-confirm-modal');
    const deleteConfirmBtn = document.getElementById('delete-confirm-btn');
    const deleteCancelBtn = document.getElementById('delete-cancel-btn');
    const deleteCheckbox = document.getElementById('delete-dont-ask-checkbox');
    const deleteTitleEl = document.getElementById('delete-confirm-title');
    const deleteMessageEl = document.getElementById('delete-confirm-message');
    let deleteConfirmCallback = null;

    function openDeleteConfirmModal({ title = 'Delete Confirmation', message = 'Do you want to delete this file?', onConfirm }) {
        if (localStorage.getItem('omni_dont_ask_delete') === 'true') {
            if (typeof onConfirm === 'function') onConfirm();
            return;
        }

        if (deleteTitleEl) deleteTitleEl.textContent = title;
        if (deleteMessageEl) deleteMessageEl.textContent = message;
        if (deleteCheckbox) deleteCheckbox.checked = false;

        deleteConfirmCallback = onConfirm;

        if (deleteModal) {
            deleteModal.classList.remove('hidden');
            deleteModal.classList.add('flex');
            if (window.lucide) lucide.createIcons();
        }
    }

    function closeDeleteConfirmModal() {
        if (deleteModal) {
            deleteModal.classList.add('hidden');
            deleteModal.classList.remove('flex');
        }
        deleteConfirmCallback = null;
    }

    if (deleteConfirmBtn) {
        deleteConfirmBtn.addEventListener('click', () => {
            if (deleteCheckbox && deleteCheckbox.checked) {
                localStorage.setItem('omni_dont_ask_delete', 'true');
            }
            const cb = deleteConfirmCallback;
            closeDeleteConfirmModal();
            if (typeof cb === 'function') {
                cb();
            }
        });
    }

    if (deleteCancelBtn) {
        deleteCancelBtn.addEventListener('click', closeDeleteConfirmModal);
    }

    if (deleteModal) {
        deleteModal.addEventListener('click', (e) => {
            if (e.target === deleteModal) {
                closeDeleteConfirmModal();
            }
        });
    }

    // Document Capabilities Modal Logic
    const docCapabilitiesModal = document.getElementById('doc-capabilities-modal');
    const openDocCapabilitiesBtn = document.getElementById('open-doc-capabilities-btn');
    const closeDocCapabilitiesBtn = document.getElementById('close-doc-capabilities-btn');
    const closeDocCapabilitiesFooterBtn = document.getElementById('close-doc-capabilities-footer-btn');

    function openDocCapabilities() {
        if (docCapabilitiesModal) {
            docCapabilitiesModal.classList.remove('hidden');
            docCapabilitiesModal.classList.add('flex');
            if (window.lucide) lucide.createIcons();
        }
    }

    function closeDocCapabilities() {
        if (docCapabilitiesModal) {
            docCapabilitiesModal.classList.add('hidden');
            docCapabilitiesModal.classList.remove('flex');
        }
    }

    if (openDocCapabilitiesBtn) {
        openDocCapabilitiesBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            openDocCapabilities();
        });
    }

    if (closeDocCapabilitiesBtn) {
        closeDocCapabilitiesBtn.addEventListener('click', closeDocCapabilities);
    }

    if (closeDocCapabilitiesFooterBtn) {
        closeDocCapabilitiesFooterBtn.addEventListener('click', closeDocCapabilities);
    }

    if (docCapabilitiesModal) {
        docCapabilitiesModal.addEventListener('click', (e) => {
            if (e.target === docCapabilitiesModal) {
                closeDocCapabilities();
            }
        });
    }

    // Escape key listener for modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeDeleteConfirmModal();
            closeDocCapabilities();
            if (previewModal) previewModal.classList.add('hidden');
        }
    });

    clearAllHistoryBtn.addEventListener('click', () => {
        clearAllHistory();
    });

    // Reset Agent Session / New Thread
    resetSessionBtn.addEventListener('click', () => {
        startNewThread();
    });

    async function startNewThread() {
        try {
            await fetch('/api/reset/', { method: 'POST' });
        } catch (e) {}
        currentConversationId = null;
        lastReport = null;
        currentActiveDocument = null;
        attachedFiles = [];
        renderAttachedFiles();
        chatContainer.innerHTML = '';
        if (welcomeHero) welcomeHero.classList.remove('hidden');
        renderHistoryList();
        showToast('Fresh thread ready.', 'info');
    }

    // Fetch Initial Reports, Conversations & System Status
    fetchReports();
    fetchConversations();
    fetchStatus();

    async function fetchConversations() {
        try {
            const res = await fetch('/api/conversations/');
            const data = await res.json();
            if (data.status === 'success') {
                conversationsData = data.conversations || [];
                historyCountBadge.textContent = conversationsData.length;
                renderHistoryList();
            }
        } catch (err) {
            console.error('Error fetching conversations:', err);
        }
    }

    function renderHistoryList() {
        const query = (historySearch.value || '').toLowerCase().trim();
        let filtered = conversationsData;

        if (query) {
            filtered = filtered.filter(c => 
                (c.title || '').toLowerCase().includes(query) || 
                (c.preview || '').toLowerCase().includes(query)
            );
        }

        if (filtered.length === 0) {
            historyList.innerHTML = `
                <div class="text-center py-10 px-4">
                    <div class="w-10 h-10 mx-auto rounded-full bg-white/5 flex items-center justify-center text-slate-500 mb-2.5">
                        <i data-lucide="message-square-off" class="w-5 h-5"></i>
                    </div>
                    <p class="text-xs font-medium text-slate-400">No conversations found</p>
                    <p class="text-[11px] text-slate-500 mt-1">Start chatting to automatically record history</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        historyList.innerHTML = filtered.map(c => {
            const isActive = c.id === currentConversationId;
            const activeClass = isActive 
                ? 'bg-indigo-600/10 dark:bg-indigo-600/20 border-indigo-500/50 shadow-md shadow-indigo-500/10' 
                : 'bg-slate-100/70 dark:bg-white/5 border-slate-200/80 dark:border-white/5 hover:bg-slate-200/60 dark:hover:bg-white/10';

            // Format date
            let timeStr = '';
            if (c.updated_at) {
                try {
                    const d = new Date(c.updated_at);
                    timeStr = d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) + ' · ' +
                              d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
                } catch (e) {
                    timeStr = c.updated_at;
                }
            }

            return `
                <div onclick="window.loadConversation('${escapeHtml(c.id)}')" 
                     class="group p-3 rounded-xl border ${activeClass} transition-all cursor-pointer flex items-start justify-between gap-2">
                    <div class="flex items-start gap-2.5 min-w-0 flex-1">
                        <div class="w-7 h-7 rounded-lg ${isActive ? 'bg-indigo-600 text-white' : 'bg-slate-200 dark:bg-white/5 text-slate-500 dark:text-slate-400'} flex items-center justify-center flex-shrink-0 mt-0.5">
                            <i data-lucide="message-square" class="w-3.5 h-3.5"></i>
                        </div>
                        <div class="min-w-0 flex-1">
                            <h4 class="text-xs font-semibold ${isActive ? 'text-indigo-600 dark:text-white' : 'text-slate-800 dark:text-slate-200'} truncate" title="${escapeHtml(c.title)}">
                                ${escapeHtml(c.title)}
                            </h4>
                            <div class="flex items-center gap-2 mt-1 text-[11px] text-slate-500 dark:text-slate-400">
                                <span>${timeStr}</span>
                                <span>•</span>
                                <span>${c.message_count} msgs</span>
                            </div>
                        </div>
                    </div>
                    
                    <button onclick="window.deleteConversation(event, '${escapeHtml(c.id)}')" 
                            title="Delete thread" 
                            class="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-500/10 transition-all flex-shrink-0">
                        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                    </button>
                </div>
            `;
        }).join('');

        if (window.lucide) lucide.createIcons();
    }

    window.loadConversation = async function(convId) {
        try {
            const res = await fetch(`/api/conversations/${convId}/`);
            const data = await res.json();
            if (data.status === 'success' && data.conversation) {
                const conv = data.conversation;
                currentConversationId = conv.id;
                lastReport = conv.last_report || null;
                currentActiveDocument = conv.active_document || null;

                if (welcomeHero) welcomeHero.classList.add('hidden');
                chatContainer.innerHTML = '';

                (conv.messages || []).forEach(msg => {
                    if (msg.role === 'user') {
                        appendUserMessage(msg.content, msg.id);
                    } else if (msg.role === 'assistant') {
                        appendAgentResponse(msg.content, msg.is_saved, msg.saved_path, msg);
                    }
                });

                closeHistoryDrawer();
                renderHistoryList();
                showToast('Loaded conversation thread', 'info');
            }
        } catch (e) {
            showToast('Failed to load conversation', 'error');
        }
    };

    window.deleteConversation = function(event, convId) {
        if (event && event.stopPropagation) event.stopPropagation();
        openDeleteConfirmModal({
            title: 'Delete Confirmation',
            message: 'Do you want to delete this file?',
            onConfirm: async () => {
                try {
                    const res = await fetch(`/api/conversations/${convId}/delete/`, { method: 'POST' });
                    const data = await res.json();
                    if (data.status === 'success') {
                        if (currentConversationId === convId) {
                            startNewThread();
                        }
                        fetchConversations();
                        showToast('Conversation deleted', 'info');
                    }
                } catch (e) {
                    showToast('Unable to delete conversation', 'error');
                }
            }
        });
    };

    function clearAllHistory() {
        openDeleteConfirmModal({
            title: 'Clear History',
            message: 'Do you want to delete all conversation history? This cannot be undone.',
            onConfirm: async () => {
                try {
                    const res = await fetch('/api/conversations/clear/', { method: 'POST' });
                    const data = await res.json();
                    if (data.status === 'success') {
                        startNewThread();
                        fetchConversations();
                        showToast('All history cleared', 'info');
                    }
                } catch (e) {
                    showToast('Failed to clear history', 'error');
                }
            }
        });
    }

    async function fetchStatus() {
        try {
            const res = await fetch('/api/status/');
            const data = await res.json();
            if (data.status === 'online') {
                agentStatusPill.innerHTML = `
                    <span class="pulsing-dot mr-2"></span>
                    <span class="text-xs font-medium text-emerald-400">Agent Ready</span>
                    <span class="mx-2 text-slate-600">|</span>
                    <span class="text-xs text-indigo-300 font-mono">${data.model}</span>
                `;
            }
        } catch (e) {
            agentStatusPill.innerHTML = `
                <span class="w-2 h-2 rounded-full bg-amber-400 mr-2"></span>
                <span class="text-xs font-medium text-amber-400">Local Mode</span>
            `;
        }
    }

    async function fetchReports() {
        try {
            const [repRes, upRes] = await Promise.allSettled([
                fetch('/api/reports/'),
                fetch('/api/uploads/')
            ]);
            if (repRes.status === 'fulfilled') {
                const repData = await repRes.value.json();
                reportsData = repData.status === 'success' ? (repData.reports || []) : [];
            }
            if (upRes.status === 'fulfilled') {
                const upData = await upRes.value.json();
                uploadsData = upData.status === 'success' ? (upData.files || []) : [];
            }
            const totalCount = reportsData.length + uploadsData.length;
            reportsCountBadge.textContent = totalCount;
            drawerCountBadge.textContent = `${totalCount} files`;
            updateFilterTabsUI();
            renderReportsList();
        } catch (err) {
            console.error('Error fetching reports:', err);
        }
    }

    function renderReportsList() {
        const query = (reportSearch && reportSearch.value ? reportSearch.value : '').toLowerCase().trim();
        const allItems = [...(reportsData || []), ...(uploadsData || [])];
        let filtered = allItems;

        // Format tab filter
        if (activeFilter === 'uploads') {
            filtered = uploadsData || [];
        } else if (activeFilter === 'pdf') {
            filtered = allItems.filter(r => (r.format || '').toLowerCase() === 'pdf');
        } else if (activeFilter === 'docx' || activeFilter === 'word') {
            filtered = allItems.filter(r => ['docx', 'doc', 'word'].includes((r.format || '').toLowerCase()));
        } else if (activeFilter === 'md' || activeFilter === 'markdown') {
            filtered = allItems.filter(r => ['md', 'markdown'].includes((r.format || '').toLowerCase()));
        }

        // Search text filter
        if (query) {
            filtered = filtered.filter(r => 
                (r.filename || '').toLowerCase().includes(query) || 
                (r.topic || '').toLowerCase().includes(query) ||
                (r.format || '').toLowerCase().includes(query) ||
                (r.relpath || '').toLowerCase().includes(query) ||
                (r.filepath || '').toLowerCase().includes(query)
            );
        }

        if (filtered.length === 0) {
            reportsList.innerHTML = `
                <div class="text-center py-12 px-4">
                    <div class="w-12 h-12 mx-auto rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center text-slate-400 dark:text-slate-500 mb-3">
                        <i data-lucide="folder-search" class="w-6 h-6"></i>
                    </div>
                    <p class="text-sm font-medium text-slate-700 dark:text-slate-400">No matching files found</p>
                    <p class="text-xs text-slate-500 mt-1">Try clearing search or choosing another tab</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        reportsList.innerHTML = filtered.map(report => {
            const extColor = getBadgeClass(report.format);
            const iconName = getIconName(report.format);
            const downloadUrl = report.download_url || (report.relpath ? `/api/reports/download/${encodeURIComponent(report.relpath)}` : '#');

            return `
                <div class="p-3.5 rounded-xl bg-slate-100/90 dark:bg-[#10141f] border border-slate-200/90 dark:border-[#1d2334] hover:border-indigo-500/40 transition-all flex flex-col gap-2.5">
                    <div class="flex items-start justify-between gap-2">
                        <div class="flex items-center gap-2.5 min-w-0">
                            <div class="w-8 h-8 rounded-lg ${extColor.bg} flex items-center justify-center flex-shrink-0 shadow-sm">
                                <i data-lucide="${iconName}" class="w-4 h-4"></i>
                            </div>
                            <div class="min-w-0">
                                <h4 class="text-xs sm:text-[13px] font-semibold text-slate-900 dark:text-slate-100 truncate" title="${escapeHtml(report.filename)}">
                                    ${escapeHtml(report.filename)}
                                </h4>
                                <div class="flex items-center gap-2 mt-0.5">
                                    <span class="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded ${extColor.tag} font-mono">
                                        ${(report.format || 'file').toUpperCase()}
                                    </span>
                                    <span class="text-xs text-slate-500 dark:text-slate-400 truncate">${report.topic || 'uploads'}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        <span class="text-[11px] font-normal">${report.size_human} · ${report.modified_formatted}</span>
                        <div class="flex items-center gap-1.5 flex-shrink-0">
                            <button onclick="window.${report.relpath ? `previewReport('${encodeURIComponent(report.relpath)}')` : `previewDocument('${encodeURIComponent(report.filename)}')`}" 
                                    class="px-2.5 py-1 rounded-lg bg-slate-200/80 dark:bg-[#181d2a] hover:bg-slate-300 dark:hover:bg-[#202738] text-slate-700 dark:text-slate-200 border border-slate-300/60 dark:border-slate-700/60 text-xs font-medium flex items-center gap-1.5 transition-all cursor-pointer">
                                <i data-lucide="eye" class="w-3.5 h-3.5 text-slate-400"></i>
                                <span>Preview</span>
                            </button>
                            <a href="${downloadUrl}" 
                               download
                               class="px-3.5 py-1 rounded-lg bg-[#5850ec] hover:bg-[#4f46e5] text-white text-xs font-semibold transition-all flex items-center gap-1.5 shadow-sm">
                                <i data-lucide="download" class="w-3.5 h-3.5"></i>
                                <span>Get</span>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        if (window.lucide) lucide.createIcons();
    }

    function getBadgeClass(format) {
        switch ((format || '').toLowerCase()) {
            case 'pdf':
                return { bg: 'bg-rose-500/10 border border-rose-500/25 text-rose-400', tag: 'bg-rose-500/10 text-rose-400 border border-rose-500/30' };
            case 'docx':
            case 'doc':
                return { bg: 'bg-blue-500/10 border border-blue-500/25 text-blue-400', tag: 'bg-blue-500/10 text-blue-400 border border-blue-500/30' };
            case 'md':
            case 'txt':
                return { bg: 'bg-violet-500/10 border border-violet-500/25 text-violet-400', tag: 'bg-violet-500/10 text-violet-400 border border-violet-500/30' };
            case 'png':
            case 'jpg':
            case 'jpeg':
                return { bg: 'bg-emerald-500/10 border border-emerald-500/25 text-emerald-400', tag: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' };
            default:
                return { bg: 'bg-slate-500/10 border border-slate-500/25 text-slate-400', tag: 'bg-slate-500/10 text-slate-400 border border-slate-500/30' };
        }
    }

    function getIconName(format) {
        switch ((format || '').toLowerCase()) {
            case 'pdf': return 'file-text';
            case 'docx': case 'doc': return 'file-edit';
            case 'md': case 'txt': return 'file-code';
            case 'png': case 'jpg': case 'jpeg': return 'image';
            default: return 'file';
        }
    }

    // Window global for previewing reports and documents
    window.previewDocument = function(filename, customRelpath = null) {
        if (!filename) return;
        const clean = filename.split('/').pop().replace(/[^\w.\-]/g, '');
        const rel = customRelpath ? customRelpath.replace(/[^\w.\-/]/g, '') : clean;
        const ext = clean.split('.').pop().toLowerCase();

        const isReport = customRelpath && (customRelpath.includes('reports') || !customRelpath.includes('uploads'));
        const previewUrl = isReport 
            ? `/api/reports/preview/${encodeURIComponent(rel)}`
            : `/api/uploads/preview/${encodeURIComponent(clean)}`;
        const downloadUrl = isReport
            ? `/api/reports/download/${encodeURIComponent(rel)}`
            : `/api/uploads/download/${encodeURIComponent(clean)}`;

        if (previewTitle) previewTitle.textContent = clean;
        if (previewDownloadBtn) {
            previewDownloadBtn.href = downloadUrl;
            previewDownloadBtn.setAttribute('download', clean);
        }

        if (previewContent) {
            if (['pdf', 'png', 'jpg', 'jpeg', 'webp'].includes(ext)) {
                previewContent.innerHTML = `<div class="p-8 text-center text-slate-400"><i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-400"></i>Loading document preview...</div>`;
                if (window.lucide) lucide.createIcons();

                fetch(previewUrl, { method: 'HEAD' }).then(response => {
                    if (!response.ok) {
                        throw new Error(`Document not available on server (${response.status})`);
                    }
                    previewContent.innerHTML = `<iframe src="${previewUrl}" class="w-full h-[72vh] rounded-xl border border-slate-200/50 dark:border-white/10 bg-slate-900" title="Document Preview"></iframe>`;
                }).catch(() => {
                    previewContent.innerHTML = `
                        <div class="p-8 sm:p-12 text-center flex flex-col items-center justify-center">
                            <div class="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center mb-3">
                                <i data-lucide="file-question" class="w-6 h-6"></i>
                            </div>
                            <h4 class="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1">Document Not Available Locally</h4>
                            <p class="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-4">
                                <strong>${escapeHtml(clean)}</strong> was not found on the server. If this was a web research citation or unsaved report, use the <strong>"Save as PDF"</strong> button below the research response to export it.
                            </p>
                        </div>
                    `;
                    if (window.lucide) lucide.createIcons();
                });
            } else if (['docx', 'doc'].includes(ext)) {
                previewContent.innerHTML = `<div class="p-8 text-center text-slate-400"><i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-400"></i>Extracting document text...</div>`;
                if (window.lucide) lucide.createIcons();

                fetch(previewUrl, { headers: { 'Accept': 'application/json' } })
                    .then(r => r.json())
                    .then(data => {
                        if (data.status === 'success' && data.content) {
                            previewContent.innerHTML = `<div class="p-4 sm:p-6 bg-slate-900/60 rounded-xl text-xs sm:text-sm font-sans text-slate-200 overflow-auto max-h-[70vh] whitespace-pre-wrap leading-relaxed">${escapeHtml(data.content)}</div>`;
                        } else {
                            throw new Error('Unable to extract Word document');
                        }
                    })
                    .catch(() => {
                        previewContent.innerHTML = `
                            <div class="p-8 sm:p-12 text-center flex flex-col items-center justify-center">
                                <div class="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center mb-3">
                                    <i data-lucide="file-text" class="w-6 h-6"></i>
                                </div>
                                <h4 class="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1">${escapeHtml(clean)}</h4>
                                <p class="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-4">
                                    Preview not available for this Word document. Download it to view on your device.
                                </p>
                                <a href="${downloadUrl}" download="${escapeHtml(clean)}" class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2">
                                    <i data-lucide="download" class="w-4 h-4"></i>
                                    <span>Download Word File</span>
                                </a>
                            </div>
                        `;
                        if (window.lucide) lucide.createIcons();
                    });
            } else {
                fetch(previewUrl).then(r => r.text()).then(text => {
                    if (['md'].includes(ext)) {
                        previewContent.innerHTML = `<div class="p-4 sm:p-6 bg-slate-900/60 rounded-xl text-xs sm:text-sm prose prose-invert max-w-none overflow-auto max-h-[70vh]">${renderMarkdownWithMath(text)}</div>`;
                    } else {
                        previewContent.innerHTML = `<pre class="p-4 bg-slate-900/60 rounded-xl text-xs font-mono text-slate-200 overflow-auto max-h-[70vh] whitespace-pre-wrap">${escapeHtml(text)}</pre>`;
                    }
                }).catch(() => {
                    window.open(previewUrl, '_blank');
                });
            }
        }
        if (previewModal) {
            previewModal.classList.remove('hidden');
            previewModal.classList.add('flex');
            if (window.lucide) lucide.createIcons();
            if (previewContent) renderMathIfAvailable(previewContent);
        }
    };

    window.previewReport = function(relpath) {
        window.previewDocument(relpath, relpath);
    };

    // Core Research Query Dispatcher
    async function submitResearchQuery(prompt, options = {}) {
        let text = (prompt || '').trim();
        if (!text) return;
        if (isResearching) {
            showToast('Agent is currently researching. Please wait...', 'info');
            return;
        }

        // Handle active attachments
        let filePaths = attachedFiles.map(f => f.filepath);
        let filePath = filePaths[0] || options.filePath || null;
        if (attachedFiles.length) {
            attachedFiles = [];
            renderAttachedFiles();
        }

        // Hide welcome hero if first message
        if (welcomeHero) welcomeHero.classList.add('hidden');

        // Clear composer if query originated from prompt input
        if (options.isFromComposer) {
            promptInput.value = '';
            promptInput.style.height = 'auto';
        }

        // Only append a new user message if not already updating in-place from edit
        if (!options.isEdit) {
            appendUserMessage(text);
        }

        // Determine target element for loader (in-place regeneration)
        let targetForLoader = null;
        let insertAfter = false;
        if (options.isEdit && options.messageElement) {
            const nextEl = options.messageElement.nextElementSibling;
            if (nextEl) {
                targetForLoader = nextEl;
                // Remove any subsequent elements after this turn
                while (nextEl.nextElementSibling) {
                    nextEl.nextElementSibling.remove();
                }
            } else {
                targetForLoader = options.messageElement;
                insertAfter = true;
            }
        }

        // Append Loading State with Animated Telemetry (in-place if editing)
        const loaderId = appendAgentLoader(text, targetForLoader, insertAfter);

        isResearching = true;
        sendBtn.disabled = true;
        sendBtn.classList.add('opacity-50', 'cursor-not-allowed');
        scrollToBottom();

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: text,
                    file_path: filePath,
                    file_paths: filePaths,
                    active_document: currentActiveDocument,
                    last_report: lastReport,
                    conversation_id: currentConversationId,
                    edit_message_id: options.msgId || null,
                    is_edit: !!options.isEdit
                })
            });

            const data = await response.json();
            stopResearchProgress();

            const loaderEl = document.getElementById(loaderId);

            if (data.status === 'success') {
                const responseText = data.response;
                const stripped = (responseText || '').trim();

                // If not a save confirmation, update lastReport
                if (!stripped.startsWith('SAVED:') && !stripped.startsWith('SAVE_FAILED:')) {
                    lastReport = responseText;
                }

                // Update current conversation id and refresh history list
                if (data.conversation_id) {
                    currentConversationId = data.conversation_id;
                    fetchConversations();
                }

                if (data.active_document) {
                    currentActiveDocument = data.active_document;
                }

                // Replace loader in-place with the newly generated agent response
                appendAgentResponse(responseText, data.is_saved, data.saved_path, data, loaderEl);

                // If saved or doc result, refresh reports & uploads vault
                if (data.is_saved || data.is_doc_result) {
                    fetchReports();
                    if (data.is_saved) {
                        showToast('Document saved to vault!', 'success');
                    } else if (data.is_doc_result) {
                        showToast('Document operation completed!', 'success');
                    }
                }
            } else {
                appendErrorMessage(data.message || 'An error occurred during agent execution.', loaderEl);
            }
        } catch (err) {
            stopResearchProgress();
            const loaderEl = document.getElementById(loaderId);
            appendErrorMessage(err.message || 'Network communication error.', loaderEl);
        } finally {
            isResearching = false;
            sendBtn.disabled = false;
            sendBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            promptInput.focus();
            if (typeof window._onLiveVoiceResearchFinished === 'function') {
                try {
                    window._onLiveVoiceResearchFinished();
                } catch(e) {}
                window._onLiveVoiceResearchFinished = null;
            }
        }
    }

    // Chat Submission Form
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = promptInput.value.trim();
        if (!prompt) return;
        await submitResearchQuery(prompt, { isFromComposer: true });
    });

    function appendUserMessage(text, msgId = null) {
        const msg = document.createElement('div');
        msg.className = 'flex justify-end gap-2 sm:gap-3 mb-4 sm:mb-6 animate-fadeIn group user-message-row';
        const actualMsgId = msgId || ('msg_u_' + Date.now());
        msg.setAttribute('data-msg-id', actualMsgId);

        msg.innerHTML = `
            <div class="user-chat-bubble max-w-[88%] sm:max-w-2xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-2xl rounded-tr-sm px-3.5 sm:px-5 py-2.5 sm:py-3.5 shadow-lg shadow-indigo-500/10 text-xs sm:text-sm leading-relaxed font-normal flex flex-col min-w-[170px] transition-all">
                
                <!-- View Mode -->
                <div class="user-msg-view flex flex-col w-full">
                    <div class="user-msg-text user-msg-scroll max-h-[220px] overflow-y-auto pr-1 text-xs sm:text-sm whitespace-pre-wrap break-words leading-relaxed select-text">${escapeHtml((text || '').trim())}</div>
                    
                    <!-- Actions Toolbar: Edit and Send button -->
                    <div class="user-msg-actions flex items-center justify-end gap-1.5 pt-2 mt-2 border-t border-white/15 select-none">
                        <button type="button" 
                                class="btn-edit-msg inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium text-white/80 hover:text-white bg-white/10 hover:bg-white/20 transition-all active:scale-95 cursor-pointer" 
                                title="Edit context">
                            <i data-lucide="pencil" class="w-3 h-3"></i>
                            <span>Edit</span>
                        </button>
                        <button type="button" 
                                class="btn-send-msg inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-medium text-white bg-white/20 hover:bg-white/30 transition-all active:scale-95 cursor-pointer shadow-sm" 
                                title="Send context">
                            <i data-lucide="send" class="w-3 h-3"></i>
                            <span>Send</span>
                        </button>
                    </div>
                </div>

                <!-- Edit Mode -->
                <div class="user-msg-edit hidden flex flex-col gap-2 w-full min-w-[240px] sm:min-w-[420px]">
                    <textarea class="user-edit-textarea w-full user-msg-scroll max-h-[220px] overflow-y-auto p-2.5 sm:p-3 bg-black/25 text-white placeholder-white/50 border border-white/25 rounded-xl text-xs sm:text-sm focus:outline-none focus:border-white/50 focus:ring-1 focus:ring-white/40 resize-none font-normal leading-relaxed"></textarea>
                    
                    <div class="flex items-center justify-between gap-2 pt-1 border-t border-white/15 select-none">
                        <span class="text-[10px] text-white/60 hidden sm:inline">Enter to send · Shift+Enter newline · Esc cancel</span>
                        <div class="flex items-center gap-1.5 ml-auto">
                            <button type="button" 
                                    class="btn-cancel-edit inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-medium text-white/80 hover:text-white bg-white/10 hover:bg-white/20 transition-all active:scale-95 cursor-pointer">
                                <i data-lucide="x" class="w-3 h-3"></i>
                                <span>Cancel</span>
                            </button>
                            <button type="button" 
                                    class="btn-send-edit inline-flex items-center gap-1 px-3 py-0.5 rounded-md text-[11px] font-semibold text-indigo-700 bg-white hover:bg-slate-100 transition-all active:scale-95 cursor-pointer shadow-sm" 
                                    title="Send edited context">
                                <i data-lucide="send" class="w-3 h-3 text-indigo-700"></i>
                                <span>Send</span>
                            </button>
                        </div>
                    </div>
                </div>

            </div>
            <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-indigo-500/10 dark:bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-600 dark:text-indigo-300 flex-shrink-0 text-[10px] sm:text-xs font-semibold">
                You
            </div>
        `;

        const viewContainer = msg.querySelector('.user-msg-view');
        const editContainer = msg.querySelector('.user-msg-edit');
        const textElem = msg.querySelector('.user-msg-text');
        const textarea = msg.querySelector('.user-edit-textarea');
        const editBtn = msg.querySelector('.btn-edit-msg');
        const sendBtn = msg.querySelector('.btn-send-msg');
        const cancelBtn = msg.querySelector('.btn-cancel-edit');
        const confirmSendBtn = msg.querySelector('.btn-send-edit');
        const bubble = msg.querySelector('.user-chat-bubble');

        let currentContent = text;

        function enterEditMode() {
            if (isResearching) {
                showToast('Agent is currently researching. Please wait...', 'info');
                return;
            }
            viewContainer.classList.add('hidden');
            editContainer.classList.remove('hidden');
            bubble.classList.add('is-editing');
            textarea.value = currentContent;

            // Auto-adjust textarea height up to 220px
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(Math.max(textarea.scrollHeight, 52), 220) + 'px';

            setTimeout(() => {
                textarea.focus();
                textarea.setSelectionRange(textarea.value.length, textarea.value.length);
            }, 10);
            if (window.lucide) lucide.createIcons();
        }

        function exitEditMode() {
            editContainer.classList.add('hidden');
            viewContainer.classList.remove('hidden');
            bubble.classList.remove('is-editing');
            if (window.lucide) lucide.createIcons();
        }

        async function handleSendFromEdit() {
            if (isResearching) {
                showToast('Agent is currently researching. Please wait...', 'info');
                return;
            }
            const newText = textarea.value.trim();
            if (!newText) {
                showToast('Context cannot be empty', 'warning');
                return;
            }
            currentContent = newText;
            textElem.textContent = newText;
            exitEditMode();
            await submitResearchQuery(newText, {
                isEdit: true,
                messageElement: msg,
                msgId: actualMsgId
            });
        }

        async function handleSendFromView() {
            if (isResearching) {
                showToast('Agent is currently researching. Please wait...', 'info');
                return;
            }
            await submitResearchQuery(currentContent, {
                isEdit: true,
                messageElement: msg,
                msgId: actualMsgId
            });
        }

        editBtn.addEventListener('click', enterEditMode);
        sendBtn.addEventListener('click', handleSendFromView);
        cancelBtn.addEventListener('click', exitEditMode);
        confirmSendBtn.addEventListener('click', handleSendFromEdit);

        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(Math.max(textarea.scrollHeight, 52), 220) + 'px';
        });

        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendFromEdit();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                exitEditMode();
            }
        });

        chatContainer.appendChild(msg);
        if (window.lucide) lucide.createIcons();
        scrollToBottom();
    }

    function appendAgentLoader(userPrompt, targetElement = null, insertAfter = false) {
        const loaderId = 'loader-' + Date.now();
        const loader = document.createElement('div');
        loader.id = loaderId;
        loader.className = 'flex gap-2 sm:gap-4 mb-4 sm:mb-6 animate-fadeIn';

        loader.innerHTML = `
            <div class="w-7 h-7 sm:w-9 sm:h-9 rounded-lg sm:rounded-xl bg-gradient-to-br from-indigo-500 to-violet-700 flex items-center justify-center text-white flex-shrink-0 shadow-lg shadow-indigo-500/20 mt-0.5">
                <i data-lucide="bot" class="w-4 h-4 sm:w-5 sm:h-5"></i>
            </div>
            <div class="flex-1 glass-panel rounded-2xl rounded-tl-sm p-3.5 sm:p-5 border border-indigo-500/20 max-w-2xl min-w-0">
                <!-- Universal Header: Quantum Core + Universal Status + Wave + Timer -->
                <div class="flex items-center justify-between pb-2.5 sm:pb-3 border-b border-slate-200/80 dark:border-white/5">
                    <div class="flex items-center gap-2.5 sm:gap-3.5 min-w-0">
                        <!-- Quantum Core Animation -->
                        <div class="quantum-core flex-shrink-0">
                            <div class="quantum-ring quantum-ring-1"></div>
                            <div class="quantum-ring quantum-ring-2"></div>
                            <div class="quantum-nucleus"></div>
                        </div>
                        <div class="min-w-0">
                            <div class="flex items-center gap-1.5 sm:gap-2">
                                <span class="shimmer-text text-[11px] sm:text-xs font-bold tracking-wider uppercase truncate">AI Processing</span>
                                <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping flex-shrink-0"></span>
                            </div>
                            <p class="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 truncate" id="phase-status-text">Understanding instructions...</p>
                        </div>
                    </div>
                    
                    <div class="flex items-center gap-2 sm:gap-2.5 flex-shrink-0">
                        <!-- Neural Frequency Equalizer Wave -->
                        <div class="neural-wave hidden sm:flex" title="Active computation">
                            <div class="neural-bar"></div>
                            <div class="neural-bar"></div>
                            <div class="neural-bar"></div>
                            <div class="neural-bar"></div>
                            <div class="neural-bar"></div>
                        </div>
                        <!-- Elapsed Timer Badge -->
                        <div class="px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full bg-slate-100 dark:bg-white/5 text-[10px] sm:text-[11px] font-mono text-cyan-600 dark:text-cyan-300 border border-slate-200 dark:border-white/10 flex items-center gap-1">
                            <span id="elapsed-timer">0s</span>
                        </div>
                    </div>
                </div>

                <!-- Universal Thought Formulation Stream (Skeleton Waves) -->
                <div class="py-3 flex flex-col gap-2">
                    <div class="skeleton-line w-[85%]"></div>
                    <div class="skeleton-line w-[65%]"></div>
                    <div class="skeleton-line w-[40%]"></div>
                </div>

                <!-- Universal Capability Badges -->
                <div class="pt-2 border-t border-slate-200/80 dark:border-white/5 flex items-center justify-between text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400">
                    <div class="flex items-center gap-2 sm:gap-3">
                        <span class="flex items-center gap-1">
                            <i data-lucide="cpu" class="w-3 h-3 text-indigo-500 dark:text-indigo-400"></i>
                            <span id="loader-mode-badge">Active Reasoning</span>
                        </span>
                        <span class="text-slate-300 dark:text-slate-700">•</span>
                        <span class="flex items-center gap-1">
                            <i data-lucide="wrench" class="w-3 h-3 text-violet-500 dark:text-violet-400"></i>
                            <span>Tools</span>
                        </span>
                    </div>
                    <span class="text-[9px] sm:text-[10px] text-slate-400 dark:text-slate-500 font-mono">stream active</span>
                </div>
            </div>
        `;

        if (targetElement && targetElement.parentNode) {
            if (insertAfter) {
                targetElement.after(loader);
            } else {
                targetElement.replaceWith(loader);
            }
        } else {
            chatContainer.appendChild(loader);
        }
        if (window.lucide) lucide.createIcons();
        scrollToBottom();

        startResearchProgress();
        return loaderId;
    }

    function startResearchProgress() {
        currentSeconds = 0;
        const timerElem = document.getElementById('elapsed-timer');
        const statusText = document.getElementById('phase-status-text');
        const modeBadge = document.getElementById('loader-mode-badge');

        // Universal progression that fits ANY task (web, directory, files, math, Q&A)
        const universalPhases = [
            { sec: 0, text: "Understanding instructions and planning actions...", mode: "Intent Analysis" },
            { sec: 3, text: "Executing operations with active tools & environment...", mode: "Tool Execution" },
            { sec: 8, text: "Processing data and cross-referencing context...", mode: "Context Synthesis" },
            { sec: 14, text: "Synthesizing output and preparing response...", mode: "Response Formulation" },
        ];

        progressTimer = setInterval(() => {
            currentSeconds++;
            if (timerElem) timerElem.textContent = `${currentSeconds}s`;

            if (currentSeconds === 3 && statusText && modeBadge) {
                statusText.textContent = universalPhases[1].text;
                modeBadge.textContent = universalPhases[1].mode;
            } else if (currentSeconds === 8 && statusText && modeBadge) {
                statusText.textContent = universalPhases[2].text;
                modeBadge.textContent = universalPhases[2].mode;
            } else if (currentSeconds === 14 && statusText && modeBadge) {
                statusText.textContent = universalPhases[3].text;
                modeBadge.textContent = universalPhases[3].mode;
            }
        }, 1000);
    }

    function stopResearchProgress() {
        if (progressTimer) {
            clearInterval(progressTimer);
            progressTimer = null;
        }
    }

    function parseReferencesAndCleanContent(rawContent) {
        let content = rawContent || '';
        let sources = [];

        // Remove the "Reply 'save as ...'" footer line if present
        content = content.replace(/\n*Reply\s*['"]?save as\s*<format>['"]?.*$/i, '');
        content = content.replace(/\n*Reply\s*['"]?save as\s*['"]?.*if you want this saved.*$/i, '');
        content = content.replace(/\n*Reply\s*['"]?save as\s*['"]?.*$/i, '');

        // Match References / Sources / Citations section at end (supports markdown headers, bold **References:**, and horizontal dividers)
        const refMatch = content.match(/(?:^|\n)(?:[-*_]{3,}\s*\n+)?(?:\*{1,2}|#{1,4})?\s*(?:References|Sources|Citations|Web Sources|Reference Links|Sources & References)\s*:?\s*(?:\*{1,2})?([\s\S]*)$/i);
        if (refMatch) {
            const refSection = refMatch[1];
            content = content.substring(0, refMatch.index).replace(/\n*[-*_]{3,}\s*$/, '').trim();

            const lines = refSection.split('\n');
            lines.forEach(line => {
                const trimmed = line.trim();
                if (!trimmed) return;

                const urlMatch = trimmed.match(/(https?:\/\/[^\s\)\>\]]+)/i);
                if (urlMatch) {
                    let url = urlMatch[1].replace(/[.,;:\)\]>]+$/, '');
                    let title = '';
                    const titleMatch = trimmed.match(/\[([^\]]+)\]/);
                    if (titleMatch) {
                        title = titleMatch[1].trim();
                    } else {
                        title = trimmed.replace(/^[\d+.\-*#\s]+/, '').split(/https?:\/\//i)[0].replace(/[-:–—(]\s*$/, '').trim();
                    }

                    try {
                        const parsedUrl = new URL(url);
                        const domain = parsedUrl.hostname.replace(/^www\./, '');
                        if (!title || title.length < 2) {
                            title = domain;
                        }
                        sources.push({
                            title: title,
                            url: url,
                            domain: domain,
                            favicon: `https://www.google.com/s2/favicons?domain=${domain}&sz=32`
                        });
                    } catch (e) {}
                }
            });
        }

        // Deduplicate sources by URL
        const uniqueSources = [];
        const seenUrls = new Set();
        sources.forEach(s => {
            if (!seenUrls.has(s.url)) {
                seenUrls.add(s.url);
                uniqueSources.push(s);
            }
        });

        return {
            cleanedContent: content,
            sources: uniqueSources
        };
    }

    window.toggleSources = function(trayId) {
        const tray = document.getElementById(trayId);
        const chevron = document.getElementById('chevron-' + trayId);
        if (!tray) return;
        if (tray.classList.contains('hidden')) {
            tray.classList.remove('hidden');
            if (chevron) chevron.style.transform = 'rotate(180deg)';
        } else {
            tray.classList.add('hidden');
            if (chevron) chevron.style.transform = 'rotate(0deg)';
        }
    };

    function renderMarkdownWithMath(content) {
        if (!content) return '';
        if (!window.marked) {
            return `<p class="whitespace-pre-wrap">${escapeHtml(content)}</p>`;
        }

        // Protect math expressions so marked does not strip backslashes or corrupt underscores
        const mathBlocks = [];
        const protectedContent = content.replace(/(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\$[^$\n]+\$|\\\([\s\S]*?\\\))/g, (match) => {
            // Auto-escape unescaped % inside math expressions so KaTeX does not treat % as a comment
            const safeMath = match.replace(/(^|[^\\])%/g, '$1\\%');
            const placeholder = `@@@MATH_BLOCK_${mathBlocks.length}@@@`;
            mathBlocks.push({ placeholder, safeMath });
            return placeholder;
        });

        // Parse markdown with marked
        let html = marked.parse(protectedContent);

        // Restore math blocks cleanly
        for (const item of mathBlocks) {
            html = html.replace(item.placeholder, () => item.safeMath);
        }

        return html;
    }

    function renderMathIfAvailable(element) {
        if (!element) return;
        if (window.renderMathInElement) {
            try {
                // Ensure any % in remaining math text nodes is escaped before KaTeX renders
                const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null, false);
                let textNode;
                const nodesToEscape = [];
                while ((textNode = walker.nextNode())) {
                    if (textNode.nodeValue && (textNode.nodeValue.includes('$$') || textNode.nodeValue.includes('$') || textNode.nodeValue.includes('\\[') || textNode.nodeValue.includes('\\('))) {
                        nodesToEscape.push(textNode);
                    }
                }
                for (const node of nodesToEscape) {
                    node.nodeValue = node.nodeValue.replace(/(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\$[^$\n]+\$|\\\([\s\S]*?\\\))/g, (math) => {
                        return math.replace(/(^|[^\\])%/g, '$1\\%');
                    });
                }

                window.renderMathInElement(element, {
                    delimiters: [
                        { left: '$$', right: '$$', display: true },
                        { left: '\\[', right: '\\]', display: true },
                        { left: '$', right: '$', display: false },
                        { left: '\\(', right: '\\)', display: false },
                    ],
                    throwOnError: false,
                    errorColor: 'currentColor',
                    strict: false,
                });
            } catch (e) {
                console.warn('[KaTeX] render error:', e);
            }
        }
    }

    function appendAgentResponse(content, isSaved, savedPath, docResult = null, replaceEl = null) {
        const msg = document.createElement('div');
        msg.className = 'flex gap-2 sm:gap-4 mb-6 sm:mb-8 animate-fadeIn assistant-message-row';

        const { cleanedContent, sources } = parseReferencesAndCleanContent(content);

        const msgId = 'msg-' + Date.now();
        const sourcesId = 'sources-' + Date.now();

        const isUpload = !!(isSaved && savedPath && (savedPath.startsWith('uploads/') || savedPath.includes('uploads')));

        // Check if Document Agent Result (EDITED, REMOVED, SIGNED, CONVERTED)
        let docBanner = '';
        let isDoc = !!(docResult && docResult.is_doc_result);
        let docAction = docResult ? docResult.doc_action : null;
        let docFilename = docResult ? docResult.doc_filename : null;
        let downloadUrl = docResult ? docResult.download_url : null;

        if (!isDoc && typeof content === 'string') {
            const stripped = content.trim();
            for (const [prefix, act] of [
                ['EDITED:', 'edit'],
                ['REMOVED:', 'remove_pages'],
                ['SIGNED:', 'sign'],
                ['CONVERTED:', 'convert'],
                ['MERGED:', 'merge'],
                ['SAVED: uploads/', 'save'],
            ]) {
                if (stripped.includes(prefix)) {
                    isDoc = true;
                    docAction = act;
                    const pathPart = stripped.split(prefix)[1].trim().split('\n')[0].trim();
                    docFilename = pathPart.split('/').pop().replace(/[^\w.\-]/g, '');
                    downloadUrl = `/api/uploads/download/${encodeURIComponent(docFilename)}`;
                    break;
                }
            }
        }

        const isDocumentAgent = isDoc || isUpload || !!(docResult && (docResult.is_doc_task || docResult.is_document_agent));

        // Check if saved
        let saveBanner = '';
        if (isSaved && savedPath && !isDoc) {
            const rawFilename = savedPath.split('/').pop().replace(/[^\w.\-]/g, '');
            const isUpload = savedPath.startsWith('uploads/') || savedPath.includes('uploads');
            const downloadUrl = isUpload 
                ? `/api/uploads/download/${encodeURIComponent(rawFilename)}` 
                : `/api/reports/download/${encodeURIComponent(savedPath)}`;

            saveBanner = `
                <div class="mb-3.5 sm:mb-4 p-3 sm:p-4 rounded-xl bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-transparent border border-emerald-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
                        <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
                            <i data-lucide="check-circle" class="w-4 h-4 sm:w-5 sm:h-5"></i>
                        </div>
                        <div class="min-w-0">
                            <h4 class="text-xs font-semibold text-white">${isUpload ? 'Document Processed & Saved' : 'Report Successfully Saved'}</h4>
                            <p class="text-[10px] sm:text-[11px] text-slate-400 font-mono truncate">${escapeHtml(rawFilename)}</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-2 flex-shrink-0">
                        <button type="button" onclick="window.previewDocument('${escapeHtml(rawFilename)}', '${escapeHtml(savedPath)}')"
                                class="px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-slate-200/80 dark:bg-white/10 hover:bg-slate-300 dark:hover:bg-white/15 text-slate-700 dark:text-slate-200 font-medium text-xs flex items-center gap-1.5 border border-slate-300/60 dark:border-white/10 transition-all cursor-pointer">
                            <i data-lucide="eye" class="w-3.5 h-3.5 text-emerald-400"></i>
                            <span>Preview</span>
                        </button>
                        <a href="${downloadUrl}" 
                           download="${escapeHtml(rawFilename)}"
                           class="px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs flex items-center gap-1.5 sm:gap-2 shadow-lg shadow-emerald-500/20 transition-all flex-shrink-0">
                            <i data-lucide="download" class="w-3.5 h-3.5 sm:w-4 sm:h-4"></i>
                            <span>Download</span>
                        </a>
                    </div>
                </div>
            `;
        }

        if (isDoc && docFilename) {
            // Avoid duplicate banner if saveBanner already handled this same file
            if (isSaved && savedPath && savedPath.includes(docFilename)) {
                saveBanner = '';
            }

            const actionTitles = {
                edit: 'Document Successfully Edited',
                remove_pages: 'PDF Pages Successfully Removed',
                sign: 'Digital Signature Successfully Applied',
                convert: 'Document Format Successfully Converted',
                merge: 'PDFs Successfully Merged',
                split: 'Document Successfully Split',
                save: 'Document Processed & Saved',
            };
            const actionIcons = {
                edit: 'file-edit',
                remove_pages: 'scissors',
                sign: 'file-signature',
                convert: 'repeat',
                merge: 'layers',
                split: 'scissors',
                save: 'file-check',
            };
            const title = actionTitles[docAction] || 'Document Processed Successfully';
            const icon = actionIcons[docAction] || 'file-check';

            docBanner = `
                <div class="mb-3.5 sm:mb-4 p-3 sm:p-4 rounded-xl bg-gradient-to-r from-violet-500/10 via-indigo-500/10 to-transparent border border-violet-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
                        <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-violet-500/20 text-violet-400 flex items-center justify-center flex-shrink-0">
                            <i data-lucide="${icon}" class="w-4 h-4 sm:w-5 sm:h-5"></i>
                        </div>
                        <div class="min-w-0">
                            <h4 class="text-xs font-semibold text-white">${title}</h4>
                            <p class="text-[10px] sm:text-[11px] text-slate-400 font-mono truncate">${escapeHtml(docFilename)}</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-2 flex-shrink-0">
                        <button type="button" onclick="window.previewDocument('${escapeHtml(docFilename)}')"
                                class="px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-slate-200/80 dark:bg-white/10 hover:bg-slate-300 dark:hover:bg-white/15 text-slate-700 dark:text-slate-200 font-medium text-xs flex items-center gap-1.5 border border-slate-300/60 dark:border-white/10 transition-all cursor-pointer">
                            <i data-lucide="eye" class="w-3.5 h-3.5 text-indigo-400"></i>
                            <span>Preview</span>
                        </button>
                        <a href="${downloadUrl || `/api/uploads/download/${encodeURIComponent(docFilename)}`}" 
                           download="${escapeHtml(docFilename)}"
                           class="px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center gap-1.5 sm:gap-2 shadow-lg shadow-indigo-500/20 transition-all flex-shrink-0">
                            <i data-lucide="download" class="w-3.5 h-3.5 sm:w-4 sm:h-4"></i>
                            <span>Download File</span>
                        </a>
                    </div>
                </div>
            `;
        }

        // Clean prose content - suppress raw status message lines, links, and internal paths
        let displayContent = cleanedContent || '';
        if (isDocumentAgent || isDoc) {
            displayContent = displayContent
                .replace(/^(?:EDITED|REMOVED|SIGNED|CONVERTED|MERGED|SAVED):\s*.*$/gim, '')
                .replace(/\[(?:Download|View|File|Click)[^\]]*\]\([^)]*\)/gi, '')
                .replace(/\[.*?\]\((?:uploads\/|\/api\/uploads\/|http)[^)]*\)/gi, '')
                .replace(/(?:You can download[^.\n]*|Download the[^.\n]*|Download link:?)[^.\n]*\.?/gi, '')
                .replace(/(?:uploads\/|\buploads[\\/])/g, '')
                .replace(/^(?:The modified file has been saved as:?|Saved as:?|Output file:?)\s*.*$/gim, '')
                .trim();
        }

        let parsedHtml = '';
        if (displayContent) {
            parsedHtml = renderMarkdownWithMath(displayContent);
        }

        const proseHtml = parsedHtml ? `
            <div class="prose-report">
                ${parsedHtml}
            </div>
        ` : '';

        // Generate Perplexity-style Sources Pill (Matching Image 2)
        let sourcesPillHtml = '';
        if (sources && sources.length > 0 && !isDocumentAgent) {
            const previewFavicons = sources.slice(0, 4);
            const faviconsHtml = previewFavicons.map(s => 
                `<img src="${s.favicon}" alt="${s.domain}" class="w-4 h-4 rounded-full border border-slate-900 dark:border-[#131722] bg-slate-800 object-cover flex-shrink-0" onerror="this.style.display='none'" />`
            ).join('');

            const sourcesCardsHtml = sources.map((s, idx) => `
                <a href="${s.url}" target="_blank" rel="noopener noreferrer" 
                   class="source-card p-2 sm:p-2.5 rounded-xl bg-slate-100/90 dark:bg-white/5 hover:bg-slate-200/90 dark:hover:bg-white/10 border border-slate-200/90 dark:border-white/5 flex flex-col justify-between gap-1.5 group/card transition-all text-left">
                    <div class="flex items-center gap-1.5 sm:gap-2 min-w-0">
                        <img src="${s.favicon}" class="w-3.5 h-3.5 rounded-sm object-contain flex-shrink-0" onerror="this.style.display='none'" />
                        <span class="text-[10px] font-medium text-slate-500 dark:text-slate-400 truncate">${s.domain}</span>
                        <span class="text-[9px] text-slate-400 dark:text-slate-500 ml-auto font-mono">#${idx + 1}</span>
                    </div>
                    <h5 class="text-xs font-medium text-slate-800 dark:text-slate-200 group-hover/card:text-indigo-600 dark:group-hover/card:text-indigo-300 line-clamp-2 leading-snug">
                        ${escapeHtml(s.title)}
                    </h5>
                </a>
            `).join('');

            sourcesPillHtml = `
                <div class="sources-wrapper mb-3 sm:mb-4">
                    <!-- Pill Button matching Screenshot 2 -->
                    <button type="button" 
                            onclick="window.toggleSources('${sourcesId}')" 
                            class="source-pill inline-flex items-center gap-2 sm:gap-2.5 px-3 sm:px-3.5 py-1.5 rounded-full cursor-pointer select-none text-xs">
                        <div class="flex items-center -space-x-1.5 overflow-hidden">
                            ${faviconsHtml}
                        </div>
                        <span class="text-[11px] sm:text-xs font-semibold tracking-wide">${sources.length} web page${sources.length > 1 ? 's' : ''}</span>
                        <i data-lucide="chevron-down" id="chevron-${sourcesId}" class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200"></i>
                    </button>

                    <!-- Expandable Sources Tray -->
                    <div id="${sourcesId}" class="hidden mt-2.5 sm:mt-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 p-2.5 sm:p-3 rounded-2xl bg-slate-100/80 dark:bg-slate-900/60 border border-slate-200 dark:border-white/5 animate-fadeIn">
                        ${sourcesCardsHtml}
                    </div>
                </div>
            `;
        }

        // Quick Action Bar: Only shown for Research Reports, hidden when Document Agent is active
        const quickActionBar = isDocumentAgent ? '' : `
            <!-- Quick Action Bar -->
            <div class="mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-slate-200/80 dark:border-white/5 flex flex-wrap items-center justify-between gap-2 sm:gap-3 text-xs">
                <div class="flex items-center gap-1.5 sm:gap-2 text-slate-500 dark:text-slate-400">
                    <i data-lucide="sparkles" class="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400"></i>
                    <span class="text-[10px] sm:text-[11px]">Save Format:</span>
                </div>
                <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
                    <button onclick="window.sendSaveCommand('save as pdf')" 
                            class="px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-rose-500/10 hover:text-rose-600 dark:hover:text-rose-300 hover:border-rose-500/40 border border-slate-200/80 dark:border-white/5 text-slate-700 dark:text-slate-300 transition-all flex items-center gap-1 sm:gap-1.5 text-[11px] sm:text-xs font-medium">
                        <i data-lucide="file-text" class="w-3.5 h-3.5 text-rose-500"></i>
                        <span class="hidden sm:inline">Save as </span><span>PDF</span>
                    </button>
                    <button onclick="window.sendSaveCommand('save as docx')" 
                            class="px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-blue-500/10 hover:text-blue-600 dark:hover:text-blue-300 hover:border-blue-500/40 border border-slate-200/80 dark:border-white/5 text-slate-700 dark:text-slate-300 transition-all flex items-center gap-1 sm:gap-1.5 text-[11px] sm:text-xs font-medium">
                        <i data-lucide="file-code" class="w-3.5 h-3.5 text-blue-500"></i>
                        <span class="hidden sm:inline">Save as </span><span>Word</span>
                    </button>
                    <button onclick="window.sendSaveCommand('save as markdown')" 
                            class="px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-violet-500/10 hover:text-violet-600 dark:hover:text-violet-300 hover:border-violet-500/40 border border-slate-200/80 dark:border-white/5 text-slate-700 dark:text-slate-300 transition-all flex items-center gap-1 sm:gap-1.5 text-[11px] sm:text-xs font-medium">
                        <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-violet-500"></i>
                        <span class="hidden sm:inline">Save as </span><span>MD</span>
                    </button>
                    <button onclick="window.copyReportText('${msgId}')" 
                            class="px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200/80 dark:border-white/5 transition-all flex items-center gap-1 sm:gap-1.5 text-[11px] sm:text-xs font-medium">
                        <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                        <span>Copy</span>
                    </button>
                </div>
            </div>
        `;

        msg.innerHTML = `
            <div class="w-7 h-7 sm:w-9 sm:h-9 rounded-lg sm:rounded-xl bg-gradient-to-br from-indigo-500 to-violet-700 flex items-center justify-center text-white flex-shrink-0 shadow-lg shadow-indigo-500/20 mt-0.5">
                <i data-lucide="bot" class="w-4 h-4 sm:w-5 sm:h-5"></i>
            </div>
            <div class="flex-1 glass-panel rounded-2xl rounded-tl-sm p-3.5 sm:p-6 border border-slate-200/80 dark:border-white/5 max-w-4xl min-w-0" id="${msgId}">
                ${saveBanner}
                ${docBanner}
                ${sourcesPillHtml}
                ${proseHtml}
                ${quickActionBar}
            </div>
        `;

        if (replaceEl && replaceEl.parentNode) {
            replaceEl.replaceWith(msg);
        } else {
            chatContainer.appendChild(msg);
        }
        renderMathIfAvailable(msg);
        if (window.lucide) lucide.createIcons();
        scrollToBottom();
    }

    function appendErrorMessage(errorText, replaceEl = null) {
        const msg = document.createElement('div');
        msg.className = 'flex gap-2 sm:gap-4 mb-4 sm:mb-6 animate-fadeIn assistant-message-row';
        msg.innerHTML = `
            <div class="w-7 h-7 sm:w-9 sm:h-9 rounded-lg sm:rounded-xl bg-rose-500/20 text-rose-500 border border-rose-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                <i data-lucide="alert-triangle" class="w-4 h-4 sm:w-5 sm:h-5"></i>
            </div>
            <div class="flex-1 glass-panel rounded-2xl rounded-tl-sm p-3.5 sm:p-4 border border-rose-200 dark:border-rose-500/20 max-w-2xl bg-rose-50/70 dark:bg-rose-950/20 min-w-0">
                <h4 class="text-xs font-semibold text-rose-700 dark:text-rose-300 mb-1">Execution Notice</h4>
                <p class="text-xs text-rose-600 dark:text-rose-200/80 leading-relaxed">${escapeHtml(errorText)}</p>
            </div>
        `;
        if (replaceEl && replaceEl.parentNode) {
            replaceEl.replaceWith(msg);
        } else {
            chatContainer.appendChild(msg);
        }
        renderMathIfAvailable(msg);
        if (window.lucide) lucide.createIcons();
        scrollToBottom();
    }

    // Save helper called from quick buttons
    window.sendSaveCommand = function(cmd) {
        if (isResearching) return;
        promptInput.value = cmd;
        chatForm.dispatchEvent(new Event('submit'));
    };

    // Copy text helper
    window.copyReportText = function(msgId) {
        const elem = document.getElementById(msgId);
        if (!elem) return;
        const text = elem.querySelector('.prose-report').innerText;
        navigator.clipboard.writeText(text).then(() => {
            showToast('Report copied to clipboard!', 'success');
        });
    };

    function showToast(text, type = 'info') {
        const toast = document.createElement('div');
        const color = type === 'success' ? 'bg-emerald-600' : type === 'error' ? 'bg-rose-600' : 'bg-indigo-600';
        toast.className = `fixed bottom-6 right-6 ${color} text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-medium z-50 flex items-center gap-2 animate-bounce`;
        toast.innerHTML = `<span>${escapeHtml(text)}</span>`;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    function removeElement(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        setTimeout(() => {
            const anchor = document.getElementById('chat-bottom-anchor');
            if (anchor) {
                anchor.scrollIntoView({ behavior: 'smooth', block: 'end' });
            } else {
                const target = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
                window.scrollTo({
                    top: target + 300,
                    behavior: 'smooth'
                });
            }
        }, 60);
    }

    // -------------------------------------------------------------------------
    // Live Voice Autonomous Research Popup (Hands-Free Voice Intelligence)
    // -------------------------------------------------------------------------
    function initLiveVoiceResearchPopup() {
        const liveVoiceBtn = document.getElementById('live-voice-btn');
        const popup = document.getElementById('live-voice-popup');
        const closeBtn = document.getElementById('close-voice-popup-btn');
        const micButton = document.getElementById('popup-mic-button');
        const transcriptEl = document.getElementById('popup-transcript');
        const titleEl = document.getElementById('popup-title');
        const subtitleEl = document.getElementById('popup-subtitle');
        const badgeText = document.getElementById('popup-badge-text');
        const badgeEl = document.getElementById('popup-badge');
        const waveCanvas = document.getElementById('popup-wave-canvas');
        const autoLaunchIndicator = document.getElementById('popup-auto-launch-indicator');
        const autoLaunchText = document.getElementById('popup-auto-launch-text');

        const listeningSection = document.getElementById('popup-listening-section');
        const researchingSection = document.getElementById('popup-researching-section');
        const activeQueryText = document.getElementById('popup-active-query-text');
        const researchStepText = document.getElementById('popup-research-step-text');
        const glow1 = document.getElementById('popup-glow-1');
        const glow2 = document.getElementById('popup-glow-2');

        if (!liveVoiceBtn || !popup) return;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        let isListening = false;
        let finalSpokenQuery = '';
        let silenceTimer = null;
        let stepCycleInterval = null;
        let waveAnimFrame = null;
        let voiceTargetAmp = 4;
        let voiceCurrentAmp = 4;
        let isCancelled = false;

        // Voice Command Triggers for Hands-Free Cancellation
        const CANCEL_TRIGGERS = [
            'cancel', 'stop', 'abort', 'ruko', 'ruk jao', 'band karo',
            'never mind', 'exit', 'quit', 'stop research', 'cancel research', "don't research"
        ];

        // ---------------------------------------------------------------------
        // Modern Fluid Audio Wave Canvas Animation
        // ---------------------------------------------------------------------
        function startFluidWaveAnimation() {
            if (!waveCanvas) return;
            const ctx = waveCanvas.getContext('2d');
            let phase = 0;

            function resizeCanvas() {
                waveCanvas.width = waveCanvas.parentElement.clientWidth || 360;
                waveCanvas.height = 64;
            }
            resizeCanvas();

            function render() {
                waveAnimFrame = requestAnimationFrame(render);
                ctx.clearRect(0, 0, waveCanvas.width, waveCanvas.height);

                // Smoothly interpolate amplitude based on voice activity
                voiceCurrentAmp += (voiceTargetAmp - voiceCurrentAmp) * 0.12;

                const width = waveCanvas.width;
                const height = waveCanvas.height;
                const midY = height / 2;

                phase += 0.04;

                // Draw 3 layers of fluid glowing sine waves
                const waves = [
                    { freq: 0.015, amp: voiceCurrentAmp * 1.0, color: 'rgba(244, 63, 94, 0.75)', lineWidth: 2.2 },
                    { freq: 0.022, amp: voiceCurrentAmp * 0.75, color: 'rgba(99, 102, 241, 0.65)', lineWidth: 1.8 },
                    { freq: 0.030, amp: voiceCurrentAmp * 0.45, color: 'rgba(168, 85, 247, 0.55)', lineWidth: 1.4 }
                ];

                waves.forEach((w, wIdx) => {
                    ctx.beginPath();
                    ctx.lineWidth = w.lineWidth;
                    ctx.strokeStyle = w.color;

                    for (let x = 0; x <= width; x += 3) {
                        // Blend sinusoidal curves with Gaussian envelope to taper edges smoothly
                        const normX = (x / width) * 2 - 1; // -1 to 1
                        const envelope = Math.max(0, 1 - normX * normX);
                        const y = midY + Math.sin(x * w.freq + phase + wIdx * 0.8) * w.amp * envelope;

                        if (x === 0) ctx.moveTo(x, y);
                        else ctx.lineTo(x, y);
                    }
                    ctx.stroke();
                });
            }
            render();
        }

        function stopFluidWaveAnimation() {
            if (waveAnimFrame) {
                cancelAnimationFrame(waveAnimFrame);
                waveAnimFrame = null;
            }
        }

        // ---------------------------------------------------------------------
        // Popup Management
        // ---------------------------------------------------------------------
        function openVoicePopup(e) {
            if (e) {
                e.preventDefault();
                e.stopPropagation();
            }

            finalSpokenQuery = '';
            isCancelled = false;
            clearTimeout(silenceTimer);

            // Reset views
            if (listeningSection) listeningSection.classList.remove('hidden');
            if (researchingSection) researchingSection.classList.add('hidden');
            if (autoLaunchIndicator) autoLaunchIndicator.classList.add('hidden');

            transcriptEl.textContent = '"Listening for your voice..."';
            transcriptEl.classList.add('italic');
            titleEl.textContent = 'Listening...';
            subtitleEl.textContent = 'Speak naturally • Silence automatically begins research';
            badgeText.textContent = 'Voice Intelligence Active';

            if (badgeEl) {
                badgeEl.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[11px] font-semibold uppercase tracking-wider mb-4 transition-colors';
            }
            if (glow1) glow1.className = 'absolute -top-16 -left-16 w-44 h-44 bg-rose-500/20 rounded-full blur-3xl pointer-events-none transition-colors duration-500';
            if (glow2) glow2.className = 'absolute -bottom-16 -right-16 w-44 h-44 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none transition-colors duration-500';

            popup.classList.remove('hidden');
            popup.classList.add('flex');
            if (window.lucide) lucide.createIcons();

            startFluidWaveAnimation();
            startVoiceCapture();
        }

        function closeVoicePopup() {
            stopVoiceCapture();
            stopFluidWaveAnimation();
            clearTimeout(silenceTimer);
            if (stepCycleInterval) {
                clearInterval(stepCycleInterval);
                stepCycleInterval = null;
            }
            popup.classList.add('hidden');
            popup.classList.remove('flex');
        }

        // ---------------------------------------------------------------------
        // Hands-Free Voice Cancellation ("Stop" / "Cancel")
        // ---------------------------------------------------------------------
        function handleVoiceCancellation(matchedKeyword) {
            isCancelled = true;
            stopVoiceCapture();
            clearTimeout(silenceTimer);

            if (autoLaunchIndicator) autoLaunchIndicator.classList.add('hidden');

            titleEl.textContent = `🚫 Cancelled via Voice`;
            subtitleEl.textContent = `Heard "${matchedKeyword}". Aborting research request.`;
            badgeText.textContent = 'Cancelled';

            if (badgeEl) {
                badgeEl.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-400 text-[11px] font-semibold uppercase tracking-wider mb-4 transition-colors';
            }
            if (glow1) glow1.className = 'absolute -top-16 -left-16 w-44 h-44 bg-amber-500/25 rounded-full blur-3xl pointer-events-none transition-colors duration-500';

            voiceTargetAmp = 1;

            setTimeout(() => {
                closeVoicePopup();
            }, 900);
        }

        // ---------------------------------------------------------------------
        // Speech Recognition with Silence VAD Detection
        // ---------------------------------------------------------------------
        function startVoiceCapture() {
            if (!SpeechRecognition) {
                showToast('Speech recognition requires Google Chrome, Edge, or Safari.', 'error');
                subtitleEl.textContent = 'Browser speech recognition not supported. Please use Chrome/Edge.';
                return;
            }

            try {
                if (recognition) {
                    try { recognition.stop(); } catch(e) {}
                }

                recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'en-US';

                recognition.onstart = () => {
                    isListening = true;
                    voiceTargetAmp = 14;
                    titleEl.textContent = 'Listening...';
                    subtitleEl.textContent = 'Speak your topic. Pause when done to auto-start.';
                };

                recognition.onresult = (event) => {
                    if (isCancelled) return;

                    let interim = '';
                    let final = '';

                    for (let i = event.resultIndex; i < event.results.length; ++i) {
                        if (event.results[i].isFinal) {
                            final += event.results[i][0].transcript;
                        } else {
                            interim += event.results[i][0].transcript;
                        }
                    }

                    const current = (final || interim).trim();
                    if (!current) return;

                    const lower = current.toLowerCase().trim();

                    // Check for Voice Cancellation Command
                    for (const trigger of CANCEL_TRIGGERS) {
                        if (lower === trigger || lower.endsWith(' ' + trigger) || lower.startsWith(trigger + ' ')) {
                            handleVoiceCancellation(trigger);
                            return;
                        }
                    }

                    // Voice detected & active
                    voiceTargetAmp = 26; // Expand waveform visually
                    finalSpokenQuery = current;
                    transcriptEl.textContent = `"${current}"`;
                    transcriptEl.classList.remove('italic');
                    titleEl.textContent = 'Voice Detected';
                    badgeText.textContent = 'Transcribing Voice...';

                    // Show auto-launch preview
                    if (autoLaunchIndicator && current.length >= 3) {
                        autoLaunchIndicator.classList.remove('hidden');
                        autoLaunchIndicator.classList.add('flex');
                        if (autoLaunchText) {
                            autoLaunchText.textContent = `Silence detected. Starting research on "${current.substring(0, 30)}..."`;
                        }
                    }

                    // Reset Silence VAD Timer: Automatically launch when user is quiet
                    clearTimeout(silenceTimer);
                    silenceTimer = setTimeout(() => {
                        if (!isCancelled && finalSpokenQuery && finalSpokenQuery.length >= 3) {
                            executeResearchFromVoice();
                        }
                    }, 1400); // 1.4 seconds of quiet triggers auto-start
                };

                recognition.onerror = (event) => {
                    console.warn('Live voice recognition notice:', event.error);
                    if (event.error === 'not-allowed') {
                        subtitleEl.textContent = 'Microphone permission blocked. Please allow mic in browser.';
                        showToast('Please allow microphone access in your browser address bar.', 'error');
                    } else if (event.error !== 'no-speech') {
                        subtitleEl.textContent = `Notice: ${event.error}. Speak to continue.`;
                    }
                };

                recognition.onend = () => {
                    isListening = false;
                    voiceTargetAmp = 4;
                    // If recognition ends naturally and we have a valid query, execute research
                    if (!isCancelled && finalSpokenQuery && finalSpokenQuery.length >= 3 && popup.classList.contains('flex')) {
                        executeResearchFromVoice();
                    }
                };

                recognition.start();

            } catch (err) {
                console.error('Error starting live voice capture:', err);
                subtitleEl.textContent = 'Click microphone icon to retry.';
            }
        }

        function stopVoiceCapture() {
            clearTimeout(silenceTimer);
            if (recognition) {
                try {
                    recognition.stop();
                } catch (e) {}
                recognition = null;
            }
            isListening = false;
            voiceTargetAmp = 4;
        }

        // ---------------------------------------------------------------------
        // Autonomous Research Execution & Persistence
        // ---------------------------------------------------------------------
        function executeResearchFromVoice() {
            if (isCancelled) return;

            const query = finalSpokenQuery.trim();
            if (!query) return;

            stopVoiceCapture();
            clearTimeout(silenceTimer);

            // Clean conversational filler if present (e.g. "i want to do research on jet planes" -> "jet planes")
            let cleanQuery = query;
            const prefixes = [
                'i want to do research on', 'i want to research on', 'i want research on',
                'please research on', 'please research about', 'research on', 'research about',
                'do research on', 'do research about', 'can you research'
            ];
            const lowerQuery = query.toLowerCase();
            for (const p of prefixes) {
                if (lowerQuery.startsWith(p)) {
                    cleanQuery = query.substring(p.length).trim();
                    break;
                }
            }
            if (!cleanQuery) cleanQuery = query;

            // Transition popup from Listening to Autonomous Researching State
            if (listeningSection) listeningSection.classList.add('hidden');
            if (researchingSection) {
                researchingSection.classList.remove('hidden');
                researchingSection.classList.add('flex');
            }

            if (activeQueryText) activeQueryText.textContent = `"${cleanQuery}"`;
            if (badgeText) badgeText.textContent = 'Autonomous Research in Progress';
            if (badgeEl) {
                badgeEl.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-[11px] font-semibold uppercase tracking-wider mb-4 transition-colors';
            }
            if (glow1) glow1.className = 'absolute -top-16 -left-16 w-44 h-44 bg-indigo-500/30 rounded-full blur-3xl pointer-events-none transition-colors duration-500';
            if (glow2) glow2.className = 'absolute -bottom-16 -right-16 w-44 h-44 bg-emerald-500/20 rounded-full blur-3xl pointer-events-none transition-colors duration-500';
            if (window.lucide) lucide.createIcons();

            // Dynamic Live Telemetry Steps (kept active until complete)
            const telemetryPhases = [
                'Phase 1/3: Deep Web Search & Academic Ingestion...',
                'Phase 2/3: Multimodal Synthesis & Cross-Verification...',
                'Phase 3/3: Formatting Executive Report & Visual Analytics...'
            ];
            let phaseIdx = 0;
            if (researchStepText) researchStepText.textContent = telemetryPhases[0];

            stepCycleInterval = setInterval(() => {
                phaseIdx = (phaseIdx + 1) % telemetryPhases.length;
                if (researchStepText) researchStepText.textContent = telemetryPhases[phaseIdx];
            }, 3000);

            // Hook callback to close popup ONLY when research is completely finished!
            window._onLiveVoiceResearchFinished = () => {
                if (stepCycleInterval) {
                    clearInterval(stepCycleInterval);
                    stepCycleInterval = null;
                }

                if (researchStepText) {
                    researchStepText.innerHTML = '<span class="text-emerald-400 font-bold flex items-center justify-center gap-1.5"><i data-lucide="check-circle" class="w-4 h-4"></i> Research Complete! Response delivered to chat.</span>';
                }
                if (badgeText) badgeText.textContent = '✓ Delivered to Chatbot';
                if (badgeEl) {
                    badgeEl.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-[11px] font-semibold uppercase tracking-wider mb-4 transition-colors';
                }
                if (window.lucide) lucide.createIcons();

                // Close popup smoothly and reveal report in chat
                setTimeout(() => {
                    closeVoicePopup();
                    scrollToBottom();
                }, 1200);
            };

            // Dispatch autonomous research query to the chatbot pipeline
            setTimeout(async () => {
                await submitResearchQuery(cleanQuery, { isFromComposer: true });
            }, 200);
        }

        // Event Listeners
        liveVoiceBtn.addEventListener('click', openVoicePopup);
        if (closeBtn) closeBtn.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); closeVoicePopup(); });

        if (micButton) {
            micButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (isListening) {
                    stopVoiceCapture();
                    if (finalSpokenQuery && finalSpokenQuery.length >= 3) {
                        executeResearchFromVoice();
                    }
                } else {
                    startVoiceCapture();
                }
            });
        }

        popup.addEventListener('click', (e) => {
            if (e.target === popup && !researchingSection.classList.contains('flex')) {
                closeVoicePopup();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !popup.classList.contains('hidden')) {
                closeVoicePopup();
            }
        });
    }

    initLiveVoiceResearchPopup();

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
