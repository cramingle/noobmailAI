<!-- NewsletterEditor.svelte -->
<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';
    import { slide } from 'svelte/transition';

    export let htmlContent: string = '';
    let previewFrame: HTMLIFrameElement;
    let viewMode = 'desktop';
    let showHtmlEditor = false;
    let editableHtml = '';
    
    const dispatch = createEventDispatcher<{
        contentUpdate: string;
    }>();

    onMount(() => {
        editableHtml = htmlContent;
        updatePreview();
    });

    // Update editableHtml whenever htmlContent changes
    $: htmlContent && (editableHtml = htmlContent);

    function updatePreview() {
        if (previewFrame?.contentWindow) {
            previewFrame.contentWindow.document.open();
            previewFrame.contentWindow.document.write(htmlContent || `
                <div style="font-family: Inter, system-ui, sans-serif; max-width: 600px; margin: 20px auto; text-align: center; color: #666;">
                    <p>Your newsletter preview will appear here.</p>
                    <p style="font-size: 14px;">Ask the AI assistant to help you create a newsletter.</p>
                </div>
            `);
            previewFrame.contentWindow.document.close();
        }
    }

    function toggleViewMode() {
        viewMode = viewMode === 'desktop' ? 'mobile' : 'desktop';
        updatePreview();
    }

    function toggleHtmlEditor() {
        showHtmlEditor = !showHtmlEditor;
        if (showHtmlEditor) {
            editableHtml = htmlContent;
        }
    }

    function applyHtmlChanges() {
        // Update the htmlContent with the edited HTML
        htmlContent = editableHtml;
        
        // Dispatch the event to notify the parent component
        dispatch('contentUpdate', editableHtml);
        
        // Update the preview
        updatePreview();
        
        // Show a visual confirmation
        const applyButton = document.querySelector('#apply-html-button') as HTMLButtonElement;
        if (applyButton) {
            const originalText = applyButton.textContent;
            applyButton.textContent = '✓ Applied';
            applyButton.disabled = true;
            
            // Switch back to preview mode after a short delay
            setTimeout(() => {
                applyButton.textContent = originalText;
                applyButton.disabled = false;
                showHtmlEditor = false; // Switch back to preview mode
            }, 800);
        }
    }

    $: if (previewFrame && htmlContent) updatePreview();
</script>

<div class="flex-1 bg-[#2d2d2d] rounded-lg shadow-xl overflow-hidden">
    <!-- Content Area -->
    <div class="h-full flex flex-col">
        <!-- Preview Header -->
        <div class="p-3 md:p-4 border-b border-gray-800 flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
            <span class="text-sm font-medium">Preview</span>
            <div class="flex space-x-2 w-full sm:w-auto">
                <!-- HTML Editor Toggle -->
                <button
                    class="px-3 py-1.5 rounded-md text-sm font-medium
                        {showHtmlEditor ? 'bg-purple-600 hover:bg-purple-700' : 'bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700'}
                        transition-all border border-gray-700 flex items-center space-x-2 whitespace-nowrap"
                    on:click={toggleHtmlEditor}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                </button>
                
                <!-- View Mode Toggle -->
                <button
                    class="px-3 py-1.5 rounded-md text-sm font-medium
                        bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700
                        transition-all border border-gray-700 flex items-center space-x-2 whitespace-nowrap"
                    on:click={toggleViewMode}
                >
                    {#if viewMode === 'desktop'}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                    {:else}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                    {/if}
                </button>
            </div>
        </div>

        {#if showHtmlEditor}
            <!-- HTML Editor -->
            <div class="flex-1 flex flex-col" transition:slide={{ duration: 200 }}>
                <div class="flex-1 overflow-hidden">
                    <textarea 
                        bind:value={editableHtml}
                        class="w-full h-full p-4 bg-[#1a1a1a] text-gray-200 font-mono text-sm resize-none focus:outline-none"
                        spellcheck="false"
                        placeholder="Enter your HTML code here..."
                    ></textarea>
                </div>
                <div class="p-3 border-t border-gray-800 flex justify-end">
                    <button
                        id="apply-html-button"
                        on:click={applyHtmlChanges}
                        class="px-4 py-2 rounded-md text-sm font-medium text-white
                            bg-gradient-to-r from-green-600 to-emerald-600 
                            hover:from-green-500 hover:to-emerald-500
                            transition-all"
                    >
                        Apply Changes
                    </button>
                </div>
            </div>
        {:else}
            <!-- Preview Frame -->
            <div class="flex-1 bg-white overflow-hidden">
                <iframe
                    bind:this={previewFrame}
                    title="Newsletter Preview"
                    class="w-full h-full {viewMode === 'mobile' ? 'max-w-sm mx-auto' : ''}"
                ></iframe>
            </div>
        {/if}
    </div>
</div>

<style>
    iframe {
        border: none;
        margin: 0;
        padding: 0;
    }

    /* Add smooth transition for view mode changes */
    iframe {
        transition: max-width 0.3s ease;
    }

    /* Ensure the preview takes full height */
    :global(.preview-container) {
        height: 100%;
        min-height: 0;
    }
    
    /* Style for the HTML editor textarea */
    textarea {
        font-family: 'Fira Code', 'Courier New', Courier, monospace;
        line-height: 1.5;
    }
</style> 