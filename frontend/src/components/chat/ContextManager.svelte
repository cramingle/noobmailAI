<!-- ContextManager.svelte -->
<script lang="ts">
    import { writable, get } from 'svelte/store';
    import type { Context } from '$lib/types';
    import { slide } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';

    // Keep for compatibility, but no longer used for checkbox selection
    export let selectedContexts: string[] = [];
    export let contexts = writable<Context[]>([]);
    
    let showAddContext = false;
    let newContextText = '';
    let dragOver = false;
    
    const dispatch = createEventDispatcher();

    async function handleFileUpload(files: FileList | null | undefined) {
        if (!files) return;
        
        for (const file of files) {
            try {
                const content = await file.text();
                const newContext: Context = {
                    id: crypto.randomUUID(),
                    name: file.name,
                    type: 'file',
                    content,
                    dateAdded: new Date()
                };
                contexts.update(c => [...c, newContext]);
            } catch (error) {
                console.error('Error reading file:', error);
            }
        }
    }

    function addTextContext() {
        if (!newContextText.trim()) return;
        
        const newContext: Context = {
            id: crypto.randomUUID(),
            name: `Context ${get(contexts).length + 1}`,
            type: 'text',
            content: newContextText,
            dateAdded: new Date()
        };
        
        contexts.update(c => [...c, newContext]);
        newContextText = '';
        showAddContext = false;
    }

    function removeContext(id: string) {
        contexts.update(c => c.filter(context => context.id !== id));
    }

    function insertContextMention(context: Context) {
        // Dispatch an event to insert @filename in the message
        dispatch('insertMention', context.name);
    }

    function handleInputChange(event: Event) {
        const target = event.target as HTMLInputElement;
        if (target && target.files) {
            handleFileUpload(target.files);
        }
    }

    function handleDrop(event: DragEvent) {
        dragOver = false;
        if (event.dataTransfer) {
            handleFileUpload(event.dataTransfer.files);
        }
    }
</script>

<div class="space-y-4">
    <!-- Context Header -->
    <div class="flex justify-between items-center">
        <h3 class="text-sm font-medium">Context Library</h3>
        <button
            on:click={() => showAddContext = !showAddContext}
            class="text-xs text-gray-400 hover:text-white transition-colors"
        >
            {showAddContext ? '- Close' : '+ Add Context'}
        </button>
    </div>

    <!-- Add Context Panel -->
    {#if showAddContext}
        <div transition:slide class="space-y-3 bg-[#1a1a1a] rounded-lg p-3">
            <!-- File Drop Zone -->
            <div
                role="button"
                tabindex="0"
                class="border-2 border-dashed border-gray-700 rounded-lg p-4 text-center text-sm
                    {dragOver ? 'border-purple-500 bg-purple-500/10' : 'hover:border-gray-600'}"
                on:dragenter|preventDefault={() => dragOver = true}
                on:dragleave|preventDefault={() => dragOver = false}
                on:dragover|preventDefault
                on:drop|preventDefault={handleDrop}
                on:click={() => document.querySelector<HTMLInputElement>('input[type="file"]')?.click()}
                on:keydown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        document.querySelector<HTMLInputElement>('input[type="file"]')?.click();
                    }
                }}
            >
                <label class="cursor-pointer">
                    <input
                        type="file"
                        multiple
                        class="hidden"
                        on:change={handleInputChange}
                    />
                    <span class="text-gray-400">
                        Drop files or click to upload
                    </span>
                </label>
            </div>

            <!-- Text Input -->
            <div class="space-y-2">
                <textarea
                    bind:value={newContextText}
                    placeholder="Or paste text context here..."
                    class="w-full h-24 bg-[#2d2d2d] rounded-md border border-gray-800 px-3 py-2 text-sm
                        focus:outline-none focus:ring-1 focus:ring-gray-700 resize-none"
                ></textarea>
                <button
                    on:click={addTextContext}
                    disabled={!newContextText.trim()}
                    class="w-full px-3 py-1.5 rounded-md text-sm font-medium
                        bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                        transition-all disabled:opacity-50"
                >
                    Add Text Context
                </button>
            </div>
        </div>
    {/if}

    <!-- Context Usage Hint -->
    {#if $contexts.length > 0}
        <div class="text-xs text-purple-400 bg-purple-500/10 p-2 rounded-lg">
            Reference contexts by typing <span class="font-semibold">@filename</span> in your message
        </div>
    {/if}

    <!-- Context List -->
    <div class="space-y-2 max-h-48 overflow-y-auto pr-2">
        {#each $contexts as context}
            <div 
                class="bg-[#1a1a1a] rounded-lg p-2 flex items-start space-x-2 hover:bg-gray-800 cursor-pointer transition-colors"
                on:click={() => insertContextMention(context)}
                on:keydown={(e) => e.key === 'Enter' && insertContextMention(context)}
                tabindex="0"
                role="button"
            >
                <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between">
                        <span class="text-sm font-medium truncate">
                            <span class="text-purple-400">@</span>{context.name}
                        </span>
                        <button
                            on:click={(e) => {
                                e.stopPropagation();
                                removeContext(context.id);
                            }}
                            class="text-gray-500 hover:text-red-400 transition-colors text-xs"
                        >
                            ×
                        </button>
                    </div>
                    <p class="text-xs text-gray-400 truncate">
                        {context.type === 'file' ? '📄 File' : '📝 Text'} • 
                        {context.dateAdded.toLocaleDateString()}
                    </p>
                </div>
            </div>
        {/each}
    </div>
</div>

<style>
    .overflow-y-auto {
        scrollbar-width: thin;
        scrollbar-color: #4a5568 #1a1a1a;
    }

    .overflow-y-auto::-webkit-scrollbar {
        width: 4px;
    }

    .overflow-y-auto::-webkit-scrollbar-track {
        background: #1a1a1a;
    }

    .overflow-y-auto::-webkit-scrollbar-thumb {
        background-color: #4a5568;
        border-radius: 2px;
    }
</style> 