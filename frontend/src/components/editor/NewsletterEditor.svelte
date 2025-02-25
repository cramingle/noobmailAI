<!-- NewsletterEditor.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { writable, get } from 'svelte/store';
    import { slide } from 'svelte/transition';
    import type { Template } from '$lib/types';
    import { defaultTemplates } from '$lib/templates';

    export let htmlContent: string = '';
    let previewFrame: HTMLIFrameElement;
    let showTemplateDropdown = false;
    let viewMode = 'desktop';

    const templates = writable<Template[]>(defaultTemplates);

    onMount(() => {
        updatePreview();
    });

    function loadTemplate(templateId: string) {
        const template = get(templates).find((t: Template) => t.id === templateId);
        if (template) {
            htmlContent = template.content;
            updatePreview();
        }
    }

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

    function saveAsExample() {
        const name = prompt('Save current design as example:');
        if (name) {
            const currentTemplates = get(templates);
            templates.update(templates => [...templates, {
                id: `example-${currentTemplates.length + 1}`,
                name,
                subject: 'Custom Example',
                content: htmlContent
            }]);
        }
        showTemplateDropdown = false;
    }

    function toggleViewMode() {
        viewMode = viewMode === 'desktop' ? 'mobile' : 'desktop';
        updatePreview();
    }

    $: htmlContent && previewFrame && updatePreview();
</script>

<div class="flex-1 bg-[#2d2d2d] rounded-lg shadow-xl overflow-hidden">
    <!-- Content Area -->
    <div class="h-full flex flex-col">
        <!-- Preview Header -->
        <div class="p-3 md:p-4 border-b border-gray-800 flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
            <span class="text-sm font-medium">Newsletter Preview</span>
            <div class="flex space-x-2 w-full sm:w-auto">
                <!-- Template Dropdown -->
                <div class="relative flex-1 sm:flex-none">
                    <button
                        on:click={() => showTemplateDropdown = !showTemplateDropdown}
                        class="w-full sm:w-auto px-3 py-1.5 rounded-md text-sm font-medium
                            bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700
                            transition-all border border-gray-700 flex items-center justify-between space-x-2"
                    >
                        <span class="truncate">Example Newsletters</span>
                        <span class="text-xs flex-shrink-0">▼</span>
                    </button>

                    {#if showTemplateDropdown}
                        <div 
                            class="absolute z-10 mt-1 w-full sm:w-64 bg-[#1a1a1a] rounded-lg shadow-lg border border-gray-800 py-1"
                            transition:slide
                        >
                            {#each $templates as template}
                                <button
                                    class="w-full px-4 py-2 text-left text-sm hover:bg-gray-800 transition-colors flex items-center space-x-2"
                                    on:click={() => loadTemplate(template.id)}
                                >
                                    <span class="truncate">{template.name}</span>
                                </button>
                            {/each}
                        </div>
                    {/if}
                </div>

                <!-- View Mode Toggle -->
                <button
                    class="px-3 py-1.5 rounded-md text-sm font-medium
                        bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700
                        transition-all border border-gray-700 flex items-center space-x-2 whitespace-nowrap"
                    on:click={toggleViewMode}
                >
                    <span>{viewMode === 'desktop' ? '📱' : '🖥️'}</span>
                    <span class="hidden sm:inline">{viewMode === 'desktop' ? 'Mobile View' : 'Desktop View'}</span>
                </button>
            </div>
        </div>

        <!-- Preview Frame -->
        <div class="flex-1 bg-white overflow-hidden">
            <iframe
                bind:this={previewFrame}
                title="Newsletter Preview"
                class="w-full h-full {viewMode === 'mobile' ? 'max-w-sm mx-auto' : ''}"
            ></iframe>
        </div>
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
</style> 