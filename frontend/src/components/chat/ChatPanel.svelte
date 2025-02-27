<!-- ChatPanel.svelte -->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { ChatMessage, EmailTemplate, EmailContent, TextResponse } from '$lib/types';
    import { fade, slide } from 'svelte/transition';
    import ContextManager from './ContextManager.svelte';
    import { onMount } from 'svelte';
    import { PUBLIC_AI_SERVICE_URL } from '$env/static/public';
    import { get, writable } from 'svelte/store';
    import type { Context } from '$lib/types';

    export let chatMessages: ChatMessage[] = [];
    export let isGenerating = false;
    export let emailType: "newsletter" | "job_application" = "newsletter";
    
    let quotaInfo = { remaining_chats: 10, max_chats: 10 };
    let showQuotaWarning = false;
    let showChatPanel = true;
    let showAddContext = false;
    let currentMessage = '';
    let currentSessionId: number | null = null;
    let sessions: any[] = [];
    let showSessionList = false;
    let showContextManager = false;

    // Create a local store for contexts
    let contexts = writable<Context[]>([]);
    
    // Keep selectedContexts for compatibility, but it's no longer used for checkbox selection
    let selectedContexts: string[] = [];
    
    // Reference to the ContextManager component
    let contextManagerComponent: ContextManager;

    // For context suggestions
    let showContextSuggestions = false;
    let contextSuggestions: {name: string, id: string}[] = [];
    let currentMentionStart = -1;
    let currentMentionText = '';

    // Add these variables at the top of the script
    let dragCounter = 0;
    let isDragging = false;
    let fileInput: HTMLInputElement;

    // Add session contexts map
    let sessionContexts: Map<number, Context[]> = new Map();

    // Function to get current session contexts
    $: currentContexts = currentSessionId ? (sessionContexts.get(currentSessionId) || []) : [];

    const dispatch = createEventDispatcher<{
        update: { 
            message: string;
            selectedContexts?: any[];
            emailType?: "newsletter" | "job_application";
        } | { 
            showChatPanel: boolean; 
        } | { 
            applyHtml: string; 
        } | { 
            notification: { 
                message: string; 
                type: 'error' | 'info' | 'success'; 
            }; 
        };
    }>();

    // Email type specific configurations
    const emailTypeConfig = {
        newsletter: {
            placeholder: "Ask me to create a newsletter...",
            welcomeMessage: "Hi! I'm your newsletter AI assistant.",
            description: "I can help you create beautiful newsletters without any technical knowledge.",
            suggestion: "Ask me anything about creating newsletters or use the templates from the onboarding guide."
        },
        job_application: {
            placeholder: "Ask me to create a job application email...",
            welcomeMessage: "Hi! I'm your job application AI assistant.",
            description: "I can help you create compelling job application emails that stand out.",
            suggestion: "Ask me about creating attention-grabbing job applications or use the templates provided."
        }
    };

    // Get current config based on email type
    $: currentConfig = emailTypeConfig[emailType];

    // Add these variables at the top of your script
    let showNewChatDialog = false;
    let newChatName = '';

    onMount(() => {
        loadSessions();
    });

    async function checkQuota() {
        try {
            const response = await fetch(`${PUBLIC_AI_SERVICE_URL}/quota`);
            if (response.ok) {
                quotaInfo = await response.json();
                showQuotaWarning = quotaInfo.remaining_chats <= 2;
            }
        } catch (error) {
            console.error('Error fetching quota information:', error);
        }
    }

    async function loadSessions() {
        try {
            const response = await fetch(`${PUBLIC_AI_SERVICE_URL}/chat-sessions`);
            if (response.ok) {
                sessions = await response.json();
                
                // Create default session if no sessions exist
                if (sessions.length === 0) {
                    const defaultSession = await createDefaultSession();
                    if (defaultSession) {
                        sessions = [defaultSession];
                        await switchSession(defaultSession.id);
                    }
                } else if (!currentSessionId) {
                    // If there are sessions but none is selected, select the most recent one
                    await switchSession(sessions[sessions.length - 1].id);
                }
            }
        } catch (error) {
            console.error('Error loading chat sessions:', error);
        }
    }

    async function createDefaultSession() {
        try {
            const response = await fetch(`${PUBLIC_AI_SERVICE_URL}/chat-sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: 'New Chat',
                    email_type: emailType
                })
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error creating default chat session:', error);
        }
        return null;
    }

    async function createNewSession() {
        try {
            const response = await fetch(`${PUBLIC_AI_SERVICE_URL}/chat-sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: `Chat ${sessions.length + 1}`,
                    email_type: emailType
                })
            });
            
            if (response.ok) {
                const newSession = await response.json();
                sessions = [...sessions, newSession];
                await switchSession(newSession.id);
            }
        } catch (error) {
            console.error('Error creating chat session:', error);
        }
    }

    async function switchSession(sessionId: number) {
        try {
            const response = await fetch(`${PUBLIC_AI_SERVICE_URL}/chat-sessions/${sessionId}/messages`);
            if (response.ok) {
                const messages = await response.json();
                chatMessages = messages;
                currentSessionId = sessionId;
                showSessionList = false;
            }
        } catch (error) {
            console.error('Error loading chat messages:', error);
        }
    }

    async function deleteSession(sessionId: number) {
        if (!confirm('Are you sure you want to delete this chat session?')) return;
        
        try {
            const response = await fetch(`${PUBLIC_AI_SERVICE_URL}/chat-sessions/${sessionId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                sessions = sessions.filter(s => s.id !== sessionId);
                if (currentSessionId === sessionId) {
                    currentSessionId = null;
                    chatMessages = [];
                }
            }
        } catch (error) {
            console.error('Error deleting chat session:', error);
        }
    }

    async function handleChat() {
        if (!currentMessage.trim() || isGenerating) return;
        
        const userMessage: ChatMessage = {
            role: 'user',
            content: currentMessage,
            timestamp: new Date()
        };
        
        // Add user message immediately to display
        chatMessages = [...chatMessages, userMessage];
        const messageToSend = currentMessage;
        currentMessage = ''; // Clear input after sending
        isGenerating = true;
        
        try {
            const response = await fetch(`${PUBLIC_AI_SERVICE_URL}/ai/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: messageToSend,
                    session_id: currentSessionId,
                    email_type: emailType
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to get AI response');
            }
            
            const data = await response.json();
            
            // Handle different response types
            let responseContent: string | EmailTemplate;
            if (data.type === "email_template") {
                responseContent = {
                    type: "email_template",
                    content: {
                        message: data.content.message || "Here's your email template:",
                        html: data.content.html
                    }
                };
            } else {
                responseContent = data.content || data.response;
            }
            
            const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: responseContent,
                timestamp: new Date()
            };
            
            // Add assistant message to display
            chatMessages = [...chatMessages, assistantMessage];
            
        } catch (error) {
            console.error('Error in chat:', error);
            // Add error message to chat
            chatMessages = [...chatMessages, {
                role: 'assistant',
                content: 'I apologize, but I encountered an error. Please try again.',
                timestamp: new Date()
            }];
        } finally {
            isGenerating = false;
        }
    }

    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleChat();
        }
    }

    function autoGrow(event: Event) {
        const textarea = event.target as HTMLTextAreaElement;
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, 128)}px`;
    }

    function handleInput(event: Event) {
        autoGrow(event);
        checkForMention();
    }

    function checkForMention() {
        const cursorPosition = (document.querySelector('textarea') as HTMLTextAreaElement).selectionStart;
        const textBeforeCursor = currentMessage.substring(0, cursorPosition);
        
        // Find the last @ symbol before the cursor
        const lastAtIndex = textBeforeCursor.lastIndexOf('@');
        
        if (lastAtIndex >= 0) {
            // Check if there's a space between the @ and the cursor
            const textAfterAt = textBeforeCursor.substring(lastAtIndex);
            const hasSpace = /\s/.test(textAfterAt);
            
            // Only show suggestions if we're in the middle of typing a mention
            if (!hasSpace || lastAtIndex === cursorPosition - 1) {
                currentMentionStart = lastAtIndex;
                currentMentionText = textAfterAt.substring(1); // Remove the @ symbol
                updateContextSuggestions();
                return;
            }
        }
        
        // Hide suggestions if we're not typing a mention
        showContextSuggestions = false;
    }

    function updateContextSuggestions() {
        const contextsValue = get(contexts);
        
        if (contextsValue.length === 0) {
            showContextSuggestions = false;
            return;
        }
        
        // Filter contexts based on what the user has typed so far
        contextSuggestions = contextsValue
            .filter(ctx => ctx.name.toLowerCase().includes(currentMentionText.toLowerCase()))
            .map(ctx => ({ name: ctx.name, id: ctx.id }));
        
        showContextSuggestions = contextSuggestions.length > 0;
    }

    function insertContextMention(contextName: string) {
        if (currentMentionStart >= 0) {
            const beforeMention = currentMessage.substring(0, currentMentionStart);
            const afterMention = currentMessage.substring(currentMentionStart + currentMentionText.length + 1); // +1 for the @ symbol
            
            currentMessage = beforeMention + '@' + contextName + ' ' + afterMention;
            showContextSuggestions = false;
            
            // Focus back on textarea and place cursor after the inserted mention
            setTimeout(() => {
                const textarea = document.querySelector('textarea') as HTMLTextAreaElement;
                textarea.focus();
                const newCursorPosition = currentMentionStart + contextName.length + 2; // +1 for @ and +1 for space
                textarea.setSelectionRange(newCursorPosition, newCursorPosition);
            }, 0);
        }
    }

    function generateNewsletter() {
        if (quotaInfo.remaining_chats <= 0) {
            showQuotaWarning = true;
            return;
        }
        
        handleChat();
    }

    // Function to check if a message contains HTML code
    function containsHtml(content: string): boolean {
        // More robust check for HTML content
        // Check for HTML doctype or html tag
        const hasHtmlStructure = content.includes('<!DOCTYPE html>') || 
                               content.includes('<html') && content.includes('</html>');
        
        // Check for complete HTML structure with body tags
        const hasBodyTags = content.includes('<body') && content.includes('</body>');
        
        // Check for HTML code blocks
        const hasHtmlCodeBlock = content.includes('```html');
        
        // Check for multiple HTML elements and style tags (likely a complete HTML snippet)
        const hasMultipleElements = (content.includes('<div') && content.includes('</div>')) && 
                                  (content.includes('<style') || content.includes('font-family:') || 
                                   content.includes('margin:') || content.includes('padding:'));
        
        return hasHtmlStructure || hasBodyTags || hasHtmlCodeBlock || hasMultipleElements;
    }

    // Function to extract HTML code from a message
    function extractHtml(content: string): string {
        // If the content has HTML code blocks with html language specification
        if (content.includes('```html')) {
            const htmlMatch = content.match(/```html\s*([\s\S]*?)\s*```/);
            if (htmlMatch && htmlMatch[1]) {
                return htmlMatch[1].trim();
            }
        }
        
        // If the content has code blocks without language specification but contains HTML
        if (content.includes('```')) {
            const codeMatches = content.matchAll(/```\s*([\s\S]*?)\s*```/g);
            for (const match of codeMatches) {
                if (match[1] && (
                    match[1].includes('<!DOCTYPE html>') || 
                    match[1].includes('<html') || 
                    (match[1].includes('<body') && match[1].includes('</body>')) ||
                    (match[1].includes('<div') && match[1].includes('</div>') && 
                     (match[1].includes('<style') || match[1].includes('font-family:')))
                )) {
                    return match[1].trim();
                }
            }
        }
        
        // If the content itself is complete HTML
        if (content.includes('<!DOCTYPE html>') || 
            (content.includes('<html') && content.includes('</html>'))) {
            // Try to extract the complete HTML document
            const htmlMatch = content.match(/(<!DOCTYPE html>[\s\S]*)|(<html[\s\S]*<\/html>)/i);
            if (htmlMatch && htmlMatch[0]) {
                return htmlMatch[0].trim();
            }
        }
        
        // If the content contains a body section
        if (content.includes('<body') && content.includes('</body>')) {
            const bodyMatch = content.match(/<body[^>]*>([\s\S]*)<\/body>/i);
            if (bodyMatch && bodyMatch[0]) {
                return bodyMatch[0].trim();
            }
        }
        
        return '';
    }

    // Function to apply HTML to the editor
    function applyHtmlToEditor(html: string | null): void {
        if (!html) {
            console.error('No valid HTML content found to apply to editor');
            dispatch('update', { 
                notification: { 
                    message: 'No valid HTML content found to apply to editor', 
                    type: 'error' 
                } 
            });
            return;
        }
        
        // Basic validation to ensure it's actually HTML content
        const isValidHtml = html.includes('<') && html.includes('>') && 
                          (html.includes('div') || html.includes('body') || 
                           html.includes('html') || html.includes('style'));
        
        if (isValidHtml) {
            dispatch('update', { applyHtml: html });
        } else {
            console.error('Invalid HTML content detected');
            dispatch('update', { 
                notification: { 
                    message: 'Invalid HTML content detected', 
                    type: 'error' 
                } 
            });
        }
    }

    // Function to highlight @filename mentions in user messages
    function highlightMentions(content: string | EmailTemplate | TextResponse): string {
        if (typeof content === 'string') {
            return content.replace(/@(\w+)/g, '<span class="mention">@$1</span>');
        } else if (isTextResponse(content)) {
            return content.content.replace(/@(\w+)/g, '<span class="mention">@$1</span>');
        } else if (isEmailTemplate(content)) {
            const text = content.content.message || '';
            return text.replace(/@(\w+)/g, '<span class="mention">@$1</span>');
        }
        return '';
    }

    function handleContextMention(event: CustomEvent<string>) {
        const contextName = event.detail;
        
        // Insert @contextName in the message input
        if (currentMessage) {
            // If there's already text, add a space before the mention
            if (!currentMessage.endsWith(' ')) {
                currentMessage += ' ';
            }
            currentMessage += `@${contextName} `;
        } else {
            currentMessage = `@${contextName} `;
        }
        
        // Focus the textarea
        setTimeout(() => {
            const textarea = document.querySelector('textarea');
            if (textarea) {
                textarea.focus();
                // Create a proper event object with the textarea as target
                const inputEvent = new Event('input');
                textarea.dispatchEvent(inputEvent);
            }
        }, 0);
    }

    // Add these functions after the existing ones
    function handleDragEnter(event: DragEvent) {
        event.preventDefault();
        dragCounter++;
        isDragging = true;
    }

    function handleDragLeave(event: DragEvent) {
        event.preventDefault();
        dragCounter--;
        if (dragCounter === 0) {
            isDragging = false;
        }
    }

    function handleDragOver(event: DragEvent) {
        event.preventDefault();
    }

    async function handleDrop(event: DragEvent) {
        event.preventDefault();
        dragCounter = 0;
        isDragging = false;
        
        const files = event.dataTransfer?.files;
        if (files) {
            await handleFiles(Array.from(files));
        }
    }

    async function handleFiles(files: File[]) {
        for (const file of files) {
            try {
                const reader = new FileReader();
                
                reader.onload = async () => {
                    const content = file.type.startsWith('image/') 
                        ? reader.result as string  // Base64 image data
                        : reader.result as string; // Text content
                    
                    const context: Context = {
                        id: crypto.randomUUID(),
                        name: file.name,
                        content: content,
                        type: file.type.startsWith('image/') ? "image" : "file",
                        dateAdded: new Date()
                    };
                    
                    if (currentSessionId) {
                        const sessionContextList = sessionContexts.get(currentSessionId) || [];
                        sessionContexts.set(currentSessionId, [...sessionContextList, context]);
                        sessionContexts = new Map(sessionContexts); // Trigger reactivity
                    }
                };
                
                if (file.type.startsWith('image/')) {
                    reader.readAsDataURL(file);
                } else {
                    reader.readAsText(file);
                }
            } catch (error) {
                console.error('Error processing file:', file.name, error);
            }
        }
    }

    function handleContextClick() {
        if (fileInput) {
            fileInput.click();
        }
    }

    function handleFileSelect(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files.length > 0) {
            handleFiles(Array.from(input.files));
        }
        // Reset input value to allow selecting the same file again
        input.value = '';
    }

    // Function to remove context
    function removeContext(contextId: string) {
        if (currentSessionId) {
            const sessionContextList = sessionContexts.get(currentSessionId) || [];
            sessionContexts.set(
                currentSessionId, 
                sessionContextList.filter(ctx => ctx.id !== contextId)
            );
            sessionContexts = new Map(sessionContexts); // Trigger reactivity
        }
    }

    // Add this function to your script
    async function handleNewChat() {
        if (!newChatName.trim()) return;

        try {
            const response = await fetch(`${PUBLIC_AI_SERVICE_URL}/chat-sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: newChatName,
                    email_type: emailType
                })
            });
            
            if (response.ok) {
                const newSession = await response.json();
                sessions = [...sessions, newSession];
                await switchSession(newSession.id);
                showNewChatDialog = false;
                newChatName = '';
            }
        } catch (error) {
            console.error('Error creating chat session:', error);
        }
    }

    // Add this helper function at the top with other functions
    function isEmailTemplate(content: string | EmailTemplate | TextResponse): content is EmailTemplate {
        return typeof content !== 'string' && content.type === 'email_template';
    }

    function isTextResponse(content: string | EmailTemplate | TextResponse): content is TextResponse {
        return typeof content !== 'string' && content.type === 'text';
    }

    function getMessageDisplay(content: string | EmailTemplate): string {
        if (typeof content === 'string') {
            return content;
        }
        return content.content.message || 'Here is your email template:';
    }

    function getHtmlContent(message: ChatMessage): string | null {
        if (!isEmailTemplate(message.content)) {
            return null;
        }
        return message.content.content.html;
    }
</script>

<div 
    class="flex flex-col h-full bg-[#1e1e1e] text-sm relative"
    on:dragenter={handleDragEnter}
    on:dragleave={handleDragLeave}
    on:dragover={handleDragOver}
    on:drop={handleDrop}
    role="region"
    aria-label="Chat panel with file drop zone"
>
    <!-- Hidden file input -->
    <input
        type="file"
        bind:this={fileInput}
        on:change={handleFileSelect}
        multiple
        accept=".txt,.md,.html,.css,.js,.json,.pdf,image/*"
        class="hidden"
    />

    <!-- Drag overlay -->
    {#if isDragging}
        <div class="absolute inset-0 bg-purple-600/20 border-2 border-dashed border-purple-500 rounded-lg z-50 flex items-center justify-center">
            <div class="text-white text-lg">Drop files here to add context</div>
        </div>
    {/if}

    <!-- Chat Header -->
    <div class="flex items-center justify-between px-3 py-2 border-b border-gray-800 bg-[#2d2d2d]">
        <div class="flex items-center gap-3">
            <div class="flex items-center">
                <!-- History Icon with Badge -->
                <button
                    on:click={() => showSessionList = !showSessionList}
                    class="relative p-1.5 rounded hover:bg-gray-700 text-gray-400 hover:text-white"
                    title="Chat History"
                    aria-label="Toggle chat history"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                        <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
                    </svg>
                    {#if sessions.length > 0}
                        <span class="absolute -top-1 -right-1 bg-purple-500 text-white text-[10px] rounded-full w-4 h-4 flex items-center justify-center">
                            {sessions.length}
                        </span>
                    {/if}
                </button>
            </div>

            <!-- Current Session Info -->
            {#if currentSessionId}
                <div class="flex items-center gap-2 px-2 py-1 bg-gray-800/40 rounded-md">
                    <span class="text-xs text-gray-400">Current chat:</span>
                    <span class="text-xs text-white font-medium truncate max-w-[150px]">
                        {sessions.find(s => s.id === currentSessionId)?.name || 'Untitled Chat'}
                    </span>
                </div>
            {:else}
                <span class="text-xs text-gray-500 italic">No active chat session</span>
            {/if}
        </div>

        <div class="flex items-center gap-2">
            <!-- New Chat Button -->
            <button
                on:click={() => showNewChatDialog = true}
                class="flex items-center gap-1.5 px-2 py-1 rounded-md bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium transition-colors"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                New Chat
            </button>

            <!-- Context Icon -->
            <button
                on:click={handleContextClick}
                class="p-1.5 rounded hover:bg-gray-700 text-gray-400 hover:text-white"
                title="Add Context Files"
                aria-label="Toggle context manager"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
            </button>
        </div>
    </div>

    <!-- New Chat Dialog -->
    {#if showNewChatDialog}
        <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" transition:fade>
            <div class="bg-[#2d2d2d] rounded-lg p-4 w-full max-w-md mx-4" transition:slide>
                <h3 class="text-lg font-medium text-white mb-4">Create New Chat</h3>
                <form on:submit|preventDefault={handleNewChat} class="space-y-4">
                    <div>
                        <label for="chatName" class="block text-sm font-medium text-gray-400 mb-1">Chat Name</label>
                        <input
                            type="text"
                            id="chatName"
                            bind:value={newChatName}
                            placeholder="e.g., Newsletter for Q2 2024"
                            class="w-full bg-[#1a1a1a] border border-gray-700 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-purple-500"
                        />
                    </div>
                    <div>
                        <label for="emailType" class="block text-sm font-medium text-gray-400 mb-1">Type</label>
                        <div class="grid grid-cols-2 gap-2" id="emailType" role="radiogroup" aria-label="Email type selection">
                            <button
                                type="button"
                                class="px-3 py-2 rounded-md text-sm font-medium text-center transition-colors {emailType === 'newsletter' ? 'bg-purple-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}"
                                on:click={() => emailType = 'newsletter'}
                            >
                                Newsletter
                            </button>
                            <button
                                type="button"
                                class="px-3 py-2 rounded-md text-sm font-medium text-center transition-colors {emailType === 'job_application' ? 'bg-purple-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}"
                                on:click={() => emailType = 'job_application'}
                            >
                                Job Application
                            </button>
                        </div>
                    </div>
                    <div class="flex justify-end gap-2 mt-6">
                        <button
                            type="button"
                            class="px-4 py-2 rounded-md text-sm font-medium bg-gray-800 text-gray-300 hover:bg-gray-700"
                            on:click={() => showNewChatDialog = false}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            class="px-4 py-2 rounded-md text-sm font-medium bg-purple-600 text-white hover:bg-purple-500 disabled:opacity-50"
                            disabled={!newChatName.trim()}
                        >
                            Create Chat
                        </button>
                    </div>
                </form>
            </div>
        </div>
    {/if}

    <!-- Session List (if shown) -->
    {#if showSessionList}
        <div class="border-b border-gray-800 bg-[#2d2d2d]" transition:slide>
            <div class="p-3 space-y-2 max-h-64 overflow-y-auto">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="text-sm font-medium text-white">Chat History</h3>
                    <span class="text-xs text-gray-400">{sessions.length} chats</span>
                </div>
                
                {#if sessions.length === 0}
                    <div class="text-center py-4">
                        <p class="text-sm text-gray-400">No chat sessions yet</p>
                        <button
                            on:click={() => showNewChatDialog = true}
                            class="mt-2 text-xs text-purple-400 hover:text-purple-300"
                        >
                            Create your first chat
                        </button>
                    </div>
                {:else}
                    <div class="space-y-1">
                        {#each sessions as session}
                            <div 
                                class="flex items-center gap-2 p-2 rounded-md hover:bg-gray-700/50 transition-colors {currentSessionId === session.id ? 'bg-gray-700/50 ring-1 ring-purple-500/50' : ''}"
                            >
                                <div class="flex-1 min-w-0">
                                    <button
                                        class="flex items-center gap-2 w-full text-left"
                                        on:click={() => switchSession(session.id)}
                                    >
                                        <div class="flex-1">
                                            <div class="flex items-center gap-2">
                                                <span class="text-sm text-gray-200 font-medium truncate">
                                                    {session.name}
                                                </span>
                                                {#if session.id === currentSessionId}
                                                    <span class="text-[10px] text-purple-400 font-medium px-1.5 py-0.5 rounded-full bg-purple-500/10">
                                                        Current
                                                    </span>
                                {/if}
                                            </div>
                                            <div class="flex items-center gap-2 mt-0.5">
                                                <span class="text-xs text-gray-500">
                                                    {session.email_type === 'newsletter' ? 'Newsletter' : 'Job Application'}
                                                </span>
                                                <span class="text-gray-600">•</span>
                                                <span class="text-xs text-gray-500">
                                                    {new Date(session.created_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                    </div>
                                        </button>
                                    </div>
                                <button
                                    class="p-1 text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                    on:click={() => deleteSession(session.id)}
                                    title="Delete chat"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
    {/if}

    <!-- Chat Messages -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
        {#each chatMessages as message}
            <div class="message {message.role}" transition:fade>
                <div class="message-content">
                    {#if typeof message.content === 'string'}
                        {@html highlightMentions(message.content)}
                    {:else if isTextResponse(message.content)}
                        {@html highlightMentions(message.content.content)}
                    {:else if isEmailTemplate(message.content)}
                        <!-- Show conversational message -->
                        {@html highlightMentions(message.content.content.message || '')}
                        
                        <!-- Only show HTML template capsule if we have HTML content -->
                        {#if message.content.content.html}
                            <div class="html-template-capsule">
                                <div class="capsule-header">
                                    <span>📧 Email Template</span>
                                    <button 
                                        class="apply-template-btn"
                                        on:click={() => {
                                            if (isEmailTemplate(message.content)) {
                                                dispatch('update', { applyHtml: message.content.content.html });
                                            }
                                        }}
                                    >
                                        Apply to Editor
                                    </button>
                                </div>
                            </div>
                        {/if}
                    {/if}
                </div>
            </div>
        {/each}
        
        {#if isGenerating}
            <div class="flex items-center space-x-2 text-gray-400">
                <div class="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                <div class="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
        {/if}
    </div>

    <!-- Input Area -->
    <div class="border-t border-gray-700/50">
        <!-- Attached Documents Display -->
        {#if currentContexts.length > 0}
            <div class="px-2 py-1.5 flex items-center gap-1.5 overflow-x-auto bg-gray-800/20 border-b border-gray-700/30">
                <span class="text-[11px] text-gray-500 font-medium whitespace-nowrap">Attached files:</span>
                <div class="flex items-center gap-1.5 flex-1 overflow-x-auto">
                    {#each currentContexts as context}
                        <div class="flex items-center gap-1 bg-gray-700/30 rounded px-1.5 py-0.5 group hover:bg-gray-700/40">
                            {#if context.type === "image"}
                                <img src={context.content} alt={context.name} class="w-3 h-3 object-cover rounded" />
                            {:else}
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
                                </svg>
                            {/if}
                            <span class="text-[11px] text-gray-300 truncate max-w-[100px]">{context.name}</span>
                            <button 
                                class="text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                on:click={() => removeContext(context.id)}
                                aria-label="Remove {context.name}"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </button>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}

        <!-- Input Box -->
        <div class="p-2">
            <div class="flex items-center gap-2">
                <textarea
                    bind:value={currentMessage}
                    on:keydown={handleKeydown}
                    on:input={handleInput}
                    placeholder={currentConfig.placeholder}
                    class="flex-1 bg-[#1a1a1a] text-white placeholder-gray-500 rounded px-3 py-1.5 focus:outline-none resize-none text-sm min-h-[36px]"
                    rows="1"
                ></textarea>
                <button
                    on:click={handleChat}
                    disabled={isGenerating}
                    class="p-1.5 rounded bg-purple-600 hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label="Send message"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                    </svg>
                </button>
            </div>
        </div>
    </div>
</div>

<style>
    /* Hide scrollbar for Chrome, Safari and Opera */
    .overflow-y-auto::-webkit-scrollbar {
        display: none;
    }

    /* Hide scrollbar for IE, Edge and Firefox */
    .overflow-y-auto {
        -ms-overflow-style: none;  /* IE and Edge */
        scrollbar-width: none;  /* Firefox */
    }

    textarea {
        min-height: 24px;
        max-height: 96px;
    }

    .message {
        margin-bottom: 1rem;
    }
    
    .message.user {
        text-align: right;
    }
    
    .message-content {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        max-width: 80%;
    }
    
    .user .message-content {
        background-color: rgba(147, 51, 234, 0.2);
    }
    
    .assistant .message-content {
        background-color: rgba(75, 85, 99, 0.2);
    }
    
    .mention {
        color: rgb(192, 132, 252);
        font-weight: 600;
    }
    
    .email-template {
        margin-top: 0.5rem;
    }
    
    .apply-template-btn {
        background-color: #9333ea;
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        margin-top: 8px;
        font-size: 14px;
        transition: background-color 0.2s;
    }
    
    .apply-template-btn:hover {
        background-color: #7e22ce;
    }

    .message-content {
        white-space: pre-wrap;
        word-break: break-word;
    }

    .html-template-capsule {
        margin-top: 8px;
        background: rgba(147, 51, 234, 0.1);
        border: 1px solid rgba(147, 51, 234, 0.2);
        border-radius: 8px;
        overflow: hidden;
    }

    .capsule-header {
        padding: 8px 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(147, 51, 234, 0.15);
        border-bottom: 1px solid rgba(147, 51, 234, 0.2);
    }

    .capsule-header span {
        font-size: 12px;
        color: #c084fc;
    }

    .apply-template-btn {
        background-color: #9333ea;
        color: white;
        padding: 4px 12px;
        border-radius: 4px;
        border: none;
        cursor: pointer;
        font-size: 12px;
        transition: background-color 0.2s;
    }

    .apply-template-btn:hover {
        background-color: #7e22ce;
    }
</style> 