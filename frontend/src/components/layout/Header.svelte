<!-- Header.svelte -->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { showOnboarding } from '$lib/stores';
    
    const dispatch = createEventDispatcher();

    function showGuide() {
        $showOnboarding = true;
    }
</script>

<div class="bg-[#2d2d2d] border-b border-gray-800">
    <div class="max-w-screen-xl mx-auto px-3 md:px-4">
        <div class="flex items-center h-14">
            <div class="flex items-center space-x-2">
                <span class="text-lg md:text-xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">NoobMail AI</span>
                <span class="text-xs text-gray-400 hidden sm:inline">Send email with style</span>
            </div>
            <div class="flex-1"></div>
            <!-- Settings Menu -->
            <div class="flex items-center space-x-2">
                <button
                    on:click={showGuide}
                    class="px-2 md:px-4 py-2 rounded-md text-sm font-medium text-gray-300 hover:text-white
                        border border-gray-700 hover:border-gray-600 transition-all flex items-center space-x-1 md:space-x-2"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    <span class="hidden sm:inline">Guide</span>
                </button>
            </div>
        </div>
    </div>
</div> 