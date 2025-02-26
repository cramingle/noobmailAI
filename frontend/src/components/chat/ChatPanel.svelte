<!-- ChatPanel.svelte -->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { ChatMessage } from '$lib/types';
    import { fade, slide } from 'svelte/transition';
    import ContextManager from './ContextManager.svelte';
    import { onMount } from 'svelte';
    import { PUBLIC_AI_SERVICE_URL } from '$env/static/public';
    import { get, writable } from 'svelte/store';
    import type { Context } from '$lib/types';

    export let chatMessages: ChatMessage[] = [];
    export let isGenerating = false;
    let quotaInfo = { remaining_chats: 10, max_chats: 10 };
    let showQuotaWarning = false;
    let showChatPanel = true;
    let showAddContext = false; // Control visibility of context manager

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

    const dispatch = createEventDispatcher<{
        update: { message: string, selectedContexts?: any[] } | { showChatPanel: boolean } | { applyHtml: string } | { notification: { message: string, type: 'error' | 'info' | 'success' } };
    }>();
    let currentMessage = '';

    // Function to set the current message from outside (for templates)
    export function setPrompt(prompt: string) {
        currentMessage = prompt;
        
        // Focus the textarea and trigger auto-grow
        setTimeout(() => {
            const textarea = document.querySelector('textarea');
            if (textarea) {
                textarea.focus();
                const inputEvent = new Event('input');
                textarea.dispatchEvent(inputEvent);
            }
        }, 0);
    }

    onMount(async () => {
        try {
            const response = await fetch(`${PUBLIC_AI_SERVICE_URL}/quota`);
            if (response.ok) {
                quotaInfo = await response.json();
                showQuotaWarning = quotaInfo.remaining_chats <= 2;
            }
        } catch (error) {
            console.error('Error fetching quota information:', error);
        }
    });

    function handleChat() {
        if (!currentMessage.trim() || isGenerating) return;
        
        // Get contexts mentioned in the message
        const contextContents = getContextContentsForMessage(currentMessage);
        
        // Show notification if context files are being used
        if (contextContents.length > 0) {
            const fileNames = contextContents.map(ctx => ctx.name).join(', ');
            dispatch('update', { 
                notification: { 
                    message: `Using context files: ${fileNames}`, 
                    type: 'info' 
                } 
            });
        }
        
        dispatch('update', { 
            message: currentMessage,
            selectedContexts: contextContents
        });
        currentMessage = '';
    }

    // Function to find mentioned contexts using @filename syntax
    function findMentionedContexts(message: string) {
        const mentionedContexts = [];
        const contextsValue = get(contexts);
        
        // Regular expression to match @filename patterns
        const mentionRegex = /@([^\s@]+)/g;
        const mentions = message.match(mentionRegex);
        
        if (mentions) {
            for (const mention of mentions) {
                const fileName = mention.substring(1); // Remove the @ symbol
                
                // Find the context with a matching name (case insensitive)
                const matchedContext = contextsValue.find(
                    ctx => ctx.name.toLowerCase() === fileName.toLowerCase()
                );
                
                if (matchedContext) {
                    mentionedContexts.push({
                        name: matchedContext.name,
                        content: matchedContext.content,
                        type: matchedContext.type
                    });
                }
            }
        }
        
        return mentionedContexts;
    }

    // Function to get the content of all available contexts for the current message
    function getContextContentsForMessage(message: string) {
        // Get all mentioned contexts
        const mentionedContexts = findMentionedContexts(message);
        
        // If no explicit mentions, check if any context file names appear in the message
        if (mentionedContexts.length === 0) {
            const contextsValue = get(contexts);
            
            for (const context of contextsValue) {
                // If the user mentions the file name in their message, include it
                if (message.toLowerCase().includes(context.name.toLowerCase())) {
                    mentionedContexts.push({
                        name: context.name,
                        content: context.content,
                        type: context.type
                    });
                    break; // Only include the first matching file to avoid making the prompt too long
                }
            }
        }
        
        return mentionedContexts;
    }

    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleChat();
            showContextSuggestions = false;
        } else if (showContextSuggestions) {
            // Handle navigation in suggestions
            if (event.key === 'Escape') {
                showContextSuggestions = false;
            }
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
    function applyHtmlToEditor(content: string) {
        const html = extractHtml(content);
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
    function highlightMentions(content: string): string {
        // Regular expression to match @filename patterns
        const mentionRegex = /@([^\s@]+)/g;
        
        // Replace @filename with highlighted version
        return content.replace(mentionRegex, (match) => {
            return `<span class="text-purple-400 font-semibold">${match}</span>`;
        });
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
</script>

<div class="h-full border-l border-gray-800 bg-[#2d2d2d] flex flex-col max-h-full overflow-hidden">
    <!-- Chat Header -->
    <div class="p-3 border-b border-gray-800 flex justify-between items-center flex-shrink-0 bg-gradient-to-r from-gray-800 to-gray-900">
        <span class="text-base font-medium text-white flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
            </svg>
            AI Assistant
        </span>
        <div class="flex items-center space-x-2">
            <button
                on:click={() => showAddContext = !showAddContext}
                class="p-1.5 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 transition-colors"
                title="Toggle Context Library"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            </button>
            <button
                class="lg:hidden p-1.5 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 transition-colors"
                on:click={() => dispatch('update', { showChatPanel: false })}
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>
    </div>

    <!-- Context Manager - Collapsible -->
    {#if showAddContext}
        <div class="p-3 border-b border-gray-800 flex-shrink-0" transition:slide={{ duration: 200 }}>
            <ContextManager 
                bind:selectedContexts 
                bind:contexts 
                bind:this={contextManagerComponent}
                on:insertMention={handleContextMention}
            />
        </div>
    {/if}

    <!-- Chat Messages - This is the scrollable area -->
    <div class="flex-1 overflow-y-auto p-3 space-y-4 min-h-0">
        {#if chatMessages.length === 0}
            <div class="text-center text-gray-500 text-sm">
                <p class="mb-2">Hi! I'm your newsletter AI assistant.</p>
                <p class="mb-2">I can help you create beautiful newsletters without any technical knowledge.</p>
                <p>Ask me anything about creating newsletters or use the templates from the onboarding guide.</p>
                <p class="mt-3 text-purple-400">Pro tip: You can reference context files using @filename in your messages!</p>
            </div>
        {/if}
        
        {#each chatMessages as message, i}
            <div class="flex flex-col space-y-2">
                <div class="flex items-start space-x-2">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                        {message.role === 'user' ? '👤' : '🤖'}
                    </div>
                    <div class="flex-1 bg-[#1a1a1a] rounded-lg p-4">
                        {#if message.role === 'assistant' && containsHtml(message.content)}
                            <div class="prose prose-sm prose-invert max-w-none break-words">
                                <!-- Display the text part of the message -->
                                {#if message.content.includes('```')}
                                    <!-- Extract text before the first code block -->
                                    {@html message.content.split('```')[0]}
                                {:else if message.content.includes('<!DOCTYPE html>') || message.content.includes('<html')}
                                    <!-- Extract text before the HTML content -->
                                    {@html message.content.split('<!DOCTYPE html>')[0].split('<html')[0]}
                                {:else if message.content.includes('<body')}
                                    <!-- Extract text before the body tag -->
                                    {@html message.content.split('<body')[0]}
                                {:else}
                                    <!-- If no clear HTML markers, try to find where HTML-like content starts -->
                                    {@html message.content.split(/<div|<style|<table|<section/)[0]}
                                {/if}
                                
                                <!-- Display code block with syntax highlighting -->
                                {#if extractHtml(message.content)}
                                    <div class="mt-4 bg-gray-900 rounded-md p-3 text-sm overflow-x-auto">
                                        <pre><code class="language-html">{extractHtml(message.content)}</code></pre>
                                    </div>
                                    
                                    <!-- Add Apply to Editor button -->
                                    <div class="mt-4">
                                        <button
                                            on:click={() => applyHtmlToEditor(message.content)}
                                            class="px-4 py-2 rounded-md text-sm font-medium text-white
                                                bg-gradient-to-r from-green-600 to-emerald-600 
                                                hover:from-green-500 hover:to-emerald-500
                                                transition-all"
                                        >
                                            Apply to Editor
                                        </button>
                                    </div>
                                {/if}
                            </div>
                        {:else}
                            <div class="prose prose-sm prose-invert max-w-none break-words text-base">
                                {#if message.role === 'user' && message.content.includes('@')}
                                    <!-- Highlight @filename mentions in user messages -->
                                    {@html highlightMentions(message.content)}
                                {:else}
                                    {message.content}
                                {/if}
                                
                                <!-- Show context files used for this message if it's a user message -->
                                {#if message.role === 'user' && message.selectedContexts && message.selectedContexts.length > 0}
                                    <div class="mt-2 text-xs text-purple-400 italic">
                                        Using context: {message.selectedContexts.join(', ')}
                                    </div>
                                {/if}
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        {/each}
        
        {#if isGenerating}
            <div class="flex items-center justify-center text-gray-400">
                <svg class="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                Generating...
            </div>
        {/if}
    </div>

    <!-- Chat Input -->
    <div class="p-3 border-t border-gray-800 flex-shrink-0">
        <div class="flex items-end space-x-2 relative">
            <div class="flex-1 relative">
                <textarea
                    bind:value={currentMessage}
                    placeholder="Ask me to create a newsletter..."
                    class="w-full bg-[#1a1a1a] rounded-lg pl-10 pr-4 py-2.5 text-base resize-none min-h-[44px] max-h-32 border border-gray-800 focus:border-purple-500 focus:outline-none transition-colors"
                    rows="1"
                    on:input={handleInput}
                    on:keydown={handleKeyDown}
                ></textarea>
                <div class="absolute left-3 bottom-2.5 text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                    </svg>
                </div>
                
                {#if $contexts.length > 0}
                    <button 
                        class="absolute right-3 bottom-2.5 text-purple-400 hover:text-purple-300 transition-colors"
                        on:click={() => showAddContext = true}
                        title="Reference context files"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                        </svg>
                    </button>
                {/if}
                
                <!-- Context Suggestions Dropdown -->
                {#if showContextSuggestions}
                    <div 
                        class="absolute left-0 bottom-full mb-2 w-64 max-h-48 overflow-y-auto bg-[#1a1a1a] border border-gray-800 rounded-md shadow-lg z-10"
                        transition:fade={{ duration: 150 }}
                    >
                        <div class="p-2 text-xs text-gray-400 border-b border-gray-800">
                            Context files matching "@{currentMentionText}"
                        </div>
                        <div class="py-1">
                            {#each contextSuggestions as suggestion}
                                <button
                                    class="w-full text-left px-3 py-2 text-sm hover:bg-gray-800 transition-colors"
                                    on:click={() => insertContextMention(suggestion.name)}
                                >
                                    {suggestion.name}
                                </button>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>
            
            <button
                on:click={handleChat}
                disabled={!currentMessage.trim() || isGenerating || quotaInfo.remaining_chats <= 0}
                class="p-2.5 rounded-md text-white
                    bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                    transition-all disabled:opacity-50 flex items-center justify-center"
                style="min-width: 44px; min-height: 44px;"
            >
                {#if isGenerating}
                    <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                {/if}
            </button>
        </div>
        
        {#if $contexts.length > 0 && !showAddContext}
            <div class="text-xs text-purple-400 mt-1.5 ml-1">
                Pro tip: Type @filename to reference a specific context file
            </div>
        {/if}
    </div>
</div>

<style>
    /* Add styles for chat panel scrollbar */
    .overflow-y-auto {
        scrollbar-width: thin;
        scrollbar-color: #4a5568 #1a1a1a;
    }

    .overflow-y-auto::-webkit-scrollbar {
        width: 6px;
    }

    .overflow-y-auto::-webkit-scrollbar-track {
        background: #1a1a1a;
    }

    .overflow-y-auto::-webkit-scrollbar-thumb {
        background-color: #4a5568;
        border-radius: 3px;
    }

    /* Ensure the chat panel takes full height on mobile */
    :global(.chat-panel-mobile) {
        height: 100vh;
        height: 100dvh;
        overflow: hidden;
    }

    /* Code block styling */
    pre {
        margin: 0;
        white-space: pre-wrap;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    
    code {
        font-family: 'Fira Code', 'Courier New', Courier, monospace;
    }
    
    /* HTML syntax highlighting */
    :global(.language-html) {
        color: #e2e8f0;
    }
    
    :global(.language-html .tag) {
        color: #9333ea;
    }
    
    :global(.language-html .attr-name) {
        color: #3b82f6;
    }
    
    :global(.language-html .attr-value) {
        color: #10b981;
    }
    
    :global(.language-html .comment) {
        color: #6b7280;
        font-style: italic;
    }
    
    /* Improve message styling */
    .prose {
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .prose p {
        margin-bottom: 0.75rem;
    }
</style> 