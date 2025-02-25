<!-- Header.svelte -->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { showOnboarding } from '$lib/stores';
    
    export let activeTab: string;
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
                <span class="text-xs text-gray-400 hidden sm:inline">Newsletter management for noob</span>
            </div>
            <div class="flex-1"></div>
            <!-- Settings Menu -->
            <div class="flex items-center space-x-2">
                <button
                    on:click={showGuide}
                    class="px-2 md:px-4 py-2 rounded-md text-sm font-medium text-gray-300 hover:text-white
                        border border-gray-700 hover:border-gray-600 transition-all flex items-center space-x-1 md:space-x-2"
                >
                    <span>📖</span>
                    <span class="hidden sm:inline">Guide</span>
                </button>
                <button
                    class="px-2 md:px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center space-x-1 md:space-x-2
                        {activeTab === 'settings' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}"
                    on:click={() => dispatch('tabChange', activeTab === 'settings' ? 'main' : 'settings')}
                >
                    <span>⚙️</span>
                    <span class="hidden sm:inline">Settings</span>
                </button>
            </div>
        </div>
    </div>
</div> 