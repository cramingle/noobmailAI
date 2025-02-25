<!-- ChatPanel.svelte -->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { ChatMessage } from '$lib/types';
    import { fade } from 'svelte/transition';
    import ContextManager from './ContextManager.svelte';
    import { onMount } from 'svelte';
    import { PUBLIC_AI_SERVICE_URL } from '$env/static/public';

    export let chatMessages: ChatMessage[] = [];
    export let isGenerating = false;
    export let quotaInfo = { remaining_chats: 10, max_chats: 10 };
    export let showQuotaWarning = false;
    export let showChatPanel = true;

    const dispatch = createEventDispatcher<{
        update: { message: string } | { showChatPanel: boolean };
    }>();
    let currentMessage = '';
    let selectedContexts: string[] = [];

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
        dispatch('update', { message: currentMessage });
        currentMessage = '';
    }

    function handleKeyDown(event: KeyboardEvent) {
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

    function generateNewsletter() {
        if (quotaInfo.remaining_chats <= 0) {
            showQuotaWarning = true;
            return;
        }
        
        handleChat();
    }
</script>

<div class="h-full border-l border-gray-800 bg-[#2d2d2d] flex flex-col">
    <!-- Chat Header -->
    <div class="p-4 border-b border-gray-800 flex justify-between items-center">
        <span class="text-sm font-medium text-white">AI Assistant</span>
        <button
            class="lg:hidden text-gray-400 hover:text-white transition-colors"
            on:click={() => dispatch('update', { showChatPanel: false })}
        >
            ✕
        </button>
    </div>

    <!-- Context Manager -->
    <div class="p-4 border-b border-gray-800">
        <ContextManager bind:selectedContexts />
    </div>

    <!-- Chat Messages -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
        {#if chatMessages.length === 0}
            <div class="text-center text-gray-500 text-sm">
                <p class="mb-2">Hi! I'm your newsletter AI assistant.</p>
                <p class="mb-2">I can help you create beautiful newsletters without any technical knowledge.</p>
                <p>Try asking me something like:</p>
                <ul class="mt-2 space-y-2">
                    <li class="bg-[#1a1a1a] rounded p-2 text-left">"Create a welcome newsletter with a modern design"</li>
                    <li class="bg-[#1a1a1a] rounded p-2 text-left">"Generate a product announcement with images and CTAs"</li>
                    <li class="bg-[#1a1a1a] rounded p-2 text-left">"Make a monthly update newsletter with sections"</li>
                </ul>
            </div>
        {/if}
        
        {#each chatMessages as message}
            <div class="flex flex-col space-y-2">
                <div class="flex items-start space-x-2">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                        {message.role === 'user' ? '👤' : '🤖'}
                    </div>
                    <div class="flex-1 bg-[#1a1a1a] rounded-lg p-3">
                        <div class="prose prose-sm prose-invert max-w-none">
                            {message.content}
                        </div>
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
    <div class="p-4 border-t border-gray-800">
        <div class="flex space-x-2">
            <textarea
                bind:value={currentMessage}
                placeholder="Ask me to create a newsletter..."
                class="flex-1 bg-[#1a1a1a] rounded-lg px-3 py-2 text-sm resize-none h-10 min-h-[40px] max-h-32"
                rows="1"
                on:input={autoGrow}
                on:keydown={handleKeyDown}
            ></textarea>
            <button
                on:click={handleChat}
                disabled={!currentMessage.trim() || isGenerating || quotaInfo.remaining_chats <= 0}
                class="px-3 py-2 rounded-md text-sm font-medium text-white
                    bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                    transition-all disabled:opacity-50 whitespace-nowrap"
            >
                {#if isGenerating}
                    <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                {:else}
                    Send
                {/if}
            </button>
        </div>
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
    }
</style> 