<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    
    export let message: string;
    export let type: 'success' | 'error' | 'info' = 'success';
    export let duration: number = 3000;
    
    const dispatch = createEventDispatcher();
    let visible = true;
    
    onMount(() => {
        const timer = setTimeout(() => {
            visible = false;
            dispatch('close');
        }, duration);
        
        return () => clearTimeout(timer);
    });
    
    function getTypeClasses() {
        switch (type) {
            case 'success':
                return 'bg-gradient-to-r from-green-600 to-emerald-600';
            case 'error':
                return 'bg-gradient-to-r from-red-600 to-pink-600';
            case 'info':
                return 'bg-gradient-to-r from-blue-600 to-indigo-600';
            default:
                return 'bg-gradient-to-r from-gray-600 to-gray-700';
        }
    }
</script>

{#if visible}
    <div 
        class="fixed bottom-4 right-4 px-4 py-3 rounded-md shadow-lg z-50 text-white {getTypeClasses()}"
        in:fly={{ y: 20, duration: 300 }}
        out:fade={{ duration: 200 }}
    >
        <div class="flex items-center">
            {#if type === 'success'}
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            {:else if type === 'error'}
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            {:else}
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            {/if}
            <span>{message}</span>
        </div>
    </div>
{/if} 