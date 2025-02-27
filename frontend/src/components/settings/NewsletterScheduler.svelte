<script lang="ts">
    import { onMount } from 'svelte';
    import { PUBLIC_API_URL } from '$env/static/public';
    import type { RecipientGroup } from '$lib/types';
    
    export let recipientGroups: RecipientGroup[] = [];
    export let isCompact = false; // New prop for compact mode
    
    interface NewsletterSchedule {
        id: number;
        name: string;
        description?: string;
        template_content: string;
        recipient_group: string;
        frequency: 'monthly' | 'weekly';
        next_send_date: string;
        last_sent_date?: string;
        is_active: boolean;
    }

    let schedules: NewsletterSchedule[] = [];
    let isLoading = true;
    let showAddForm = false;
    let errorMessage = '';
    
    // Form data
    let newSchedule = {
        name: '',
        description: '',
        template_content: '',
        recipient_group: '',
        frequency: 'monthly',
        start_date: new Date().toISOString().split('T')[0]
    };
    
    onMount(async () => {
        await loadSchedules();
    });
    
    async function loadSchedules() {
        try {
            const response = await fetch(`${PUBLIC_API_URL}/scheduled-newsletters`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                mode: 'cors'
            });

            if (!response.ok) {
                throw new Error('Failed to load scheduled newsletters');
            }

            const data = await response.json();
            schedules = data;
        } catch (error) {
            console.error('Error loading scheduled newsletters:', error);
        } finally {
            isLoading = false;
        }
    }
    
    async function handleSubmit() {
        try {
            const response = await fetch(`${PUBLIC_API_URL}/schedule-newsletter`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                mode: 'cors',
                body: JSON.stringify({
                    name: newSchedule.name,
                    description: newSchedule.description,
                    template_content: newSchedule.template_content,
                    recipient_group: newSchedule.recipient_group,
                    frequency: newSchedule.frequency,
                    start_date: newSchedule.start_date
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to schedule newsletter');
            }

            const data = await response.json();
            schedules = [...schedules, data];
            showAddForm = false;
            resetNewSchedule();
        } catch (error) {
            console.error('Error scheduling newsletter:', error);
        }
    }
    
    async function deleteSchedule(id: number) {
        if (!confirm('Are you sure you want to delete this schedule?')) return;
        
        try {
            const response = await fetch(`${PUBLIC_API_URL}/schedule-newsletter/${id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                mode: 'cors'
            });
            
            if (!response.ok) throw new Error('Failed to delete schedule');
            
            await loadSchedules();
        } catch (error) {
            errorMessage = 'Failed to delete newsletter schedule';
            console.error(error);
        }
    }

    function resetNewSchedule() {
        newSchedule = {
            name: '',
            description: '',
            template_content: '',
            recipient_group: '',
            frequency: 'monthly',
            start_date: new Date().toISOString().split('T')[0]
        };
    }
</script>

<div class="space-y-4">
    <div class="flex justify-between items-center">
        {#if !isCompact}
            <h2 class="text-xl font-semibold text-white">Newsletter Schedules</h2>
        {/if}
        <button
            class="{isCompact ? 'w-full' : ''} bg-purple-600 hover:bg-purple-500 text-white px-3 py-1.5 rounded-md text-xs transition-colors flex items-center justify-center gap-2"
            on:click={() => showAddForm = !showAddForm}
        >
            <span>{showAddForm ? '✕' : '+'}</span>
            <span>{showAddForm ? 'Cancel' : 'Schedule Email'}</span>
        </button>
    </div>
    
    {#if errorMessage}
        <div class="bg-red-500/10 border border-red-500/20 text-red-400 p-2 rounded-md text-xs">
            {errorMessage}
        </div>
    {/if}
    
    {#if showAddForm}
        <form on:submit|preventDefault={handleSubmit} class="bg-[#2d2d2d] p-2 rounded-lg space-y-2 mb-3">
            <div>
                <input
                    type="text"
                    id="name"
                    bind:value={newSchedule.name}
                    placeholder="Schedule name"
                    required
                    class="w-full bg-[#1a1a1a] border border-gray-800 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-purple-500"
                />
            </div>
            
            <div>
                <select
                    id="recipient_group"
                    bind:value={newSchedule.recipient_group}
                    required
                    class="w-full bg-[#1a1a1a] border border-gray-800 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-purple-500"
                >
                    <option value="">Select recipients</option>
                    {#each recipientGroups as group}
                        <option value={group.name}>{group.name}</option>
                    {/each}
                </select>
            </div>
            
            <div class="grid grid-cols-2 gap-2">
                <select
                    id="frequency"
                    bind:value={newSchedule.frequency}
                    required
                    class="w-full bg-[#1a1a1a] border border-gray-800 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-purple-500"
                >
                    <option value="monthly">Monthly</option>
                    <option value="weekly">Weekly</option>
                </select>
                
                <input
                    type="date"
                    id="start_date"
                    bind:value={newSchedule.start_date}
                    required
                    class="w-full bg-[#1a1a1a] border border-gray-800 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-purple-500"
                />
            </div>
            
            <button
                type="submit"
                class="w-full bg-purple-600 hover:bg-purple-500 text-white px-2 py-1 rounded text-xs transition-colors"
            >
                Schedule
            </button>
        </form>
    {/if}
    
    {#if isLoading}
        <div class="text-center text-gray-400 py-2 text-xs">
            Loading schedules...
        </div>
    {:else if schedules.length === 0}
        <div class="text-center text-gray-400 py-2 text-xs">
            No scheduled emails
        </div>
    {:else}
        <div class="space-y-2 max-h-[200px] overflow-y-auto pr-1">
            {#each schedules as schedule}
                <div class="bg-[#2d2d2d] p-2 rounded-lg">
                    <div class="flex justify-between items-start gap-2">
                        <div class="min-w-0">
                            <h4 class="text-xs font-medium text-white truncate">{schedule.name}</h4>
                            <div class="flex flex-wrap gap-x-2 mt-1">
                                <span class="text-[10px] text-gray-400">
                                    {schedule.frequency}
                                </span>
                                <span class="text-[10px] text-gray-400">
                                    Next: {new Date(schedule.next_send_date).toLocaleDateString()}
                                </span>
                            </div>
                        </div>
                        <button
                            class="text-gray-500 hover:text-red-400 transition-colors flex-shrink-0"
                            on:click={() => deleteSchedule(schedule.id)}
                            title="Delete schedule"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    /* Custom scrollbar for better UX */
    .overflow-y-auto {
        scrollbar-width: thin;
        scrollbar-color: #4a5568 #1a1a1a;
    }

    .overflow-y-auto::-webkit-scrollbar {
        width: 4px;
    }

    .overflow-y-auto::-webkit-scrollbar-track {
        background: transparent;
    }

    .overflow-y-auto::-webkit-scrollbar-thumb {
        background-color: #4a5568;
        border-radius: 2px;
    }
</style> 