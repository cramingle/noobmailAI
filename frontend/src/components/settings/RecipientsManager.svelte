<!-- RecipientsManager.svelte -->
<script lang="ts">
    import type { Recipient, RecipientGroup } from '$lib/types';
    import { slide } from 'svelte/transition';

    export let recipientGroups: RecipientGroup[];
    export let activeGroup: RecipientGroup;

    let newRecipient: Recipient = { name: '', email: '', organization: '' };
    let showNewGroupModal = false;
    let newGroupName = '';
    let showAddRecipientForm = false;

    function addRecipient() {
        if (newRecipient.name && newRecipient.email) {
            activeGroup.recipients = [...activeGroup.recipients, { ...newRecipient }];
            newRecipient = { name: '', email: '', organization: '' };
            showAddRecipientForm = false;
        }
    }

    function removeRecipient(index: number) {
        activeGroup.recipients = activeGroup.recipients.filter((_, i) => i !== index);
    }

    function addGroup() {
        if (newGroupName.trim()) {
            recipientGroups = [...recipientGroups, { name: newGroupName, recipients: [] }];
            newGroupName = '';
            showNewGroupModal = false;
        }
    }
</script>

<div class="space-y-4">
    <div class="flex justify-between items-center">
        <h2 class="text-lg font-bold">Recipients</h2>
        <button
            class="px-3 py-1.5 rounded-md text-sm font-medium
                bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700
                transition-all border border-gray-700"
            on:click={() => showNewGroupModal = true}
        >
            ➕ New Group
        </button>
    </div>

    <!-- New Group Modal -->
    {#if showNewGroupModal}
        <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" transition:slide>
            <div class="bg-[#2d2d2d] rounded-lg p-6 w-full max-w-md mx-4 space-y-4">
                <h3 class="text-lg font-medium">Create New Group</h3>
                <div>
                    <input
                        type="text"
                        bind:value={newGroupName}
                        placeholder="Enter group name"
                        class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-3 py-2 text-sm
                            focus:outline-none focus:ring-1 focus:ring-gray-700"
                        on:keydown={(e) => e.key === 'Enter' && addGroup()}
                    />
                </div>
                <div class="flex justify-end space-x-2">
                    <button
                        class="px-3 py-1.5 rounded-md text-sm font-medium text-gray-400 hover:text-white transition-colors"
                        on:click={() => {
                            showNewGroupModal = false;
                            newGroupName = '';
                        }}
                    >
                        Cancel
                    </button>
                    <button
                        class="px-3 py-1.5 rounded-md text-sm font-medium
                            bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                            transition-all disabled:opacity-50"
                        disabled={!newGroupName.trim()}
                        on:click={addGroup}
                    >
                        Create Group
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Groups and Recipients Layout -->
    <div class="flex flex-col lg:flex-row gap-4">
        <!-- Groups List - Fixed width on larger screens, full width on mobile -->
        <div class="w-full lg:w-64 flex-shrink-0">
            <div class="bg-[#1a1a1a] rounded-lg p-3">
                <div class="font-medium mb-2">Groups</div>
                <div class="space-y-1 max-h-[300px] overflow-y-auto pr-1">
                    {#each recipientGroups as group}
                        <button
                            class="w-full px-3 py-2 rounded text-left text-sm
                                {activeGroup === group ? 'bg-gray-700' : 'hover:bg-gray-800'}
                                transition-all flex justify-between items-center"
                            on:click={() => activeGroup = group}
                        >
                            <span class="truncate flex-1">{group.name}</span>
                            <span class="text-gray-400 ml-2 flex-shrink-0">
                                {group.recipients.length}
                            </span>
                        </button>
                    {/each}
                </div>
                
                <!-- Add Group Button -->
                <button
                    class="w-full mt-2 px-3 py-2 rounded-md text-sm font-medium
                        bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                        transition-all flex items-center justify-center space-x-2"
                    on:click={() => showNewGroupModal = true}
                >
                    <span>+ Add Group</span>
                </button>
            </div>
        </div>

        <!-- Recipients Management - Flexible width -->
        <div class="flex-1 min-w-0">
            <div class="bg-[#2d2d2d] rounded-lg p-3">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-3 space-y-2 sm:space-y-0">
                    <div>
                        <h2 class="text-lg font-bold">{activeGroup.name}</h2>
                        <p class="text-sm text-gray-400">{activeGroup.recipients.length} recipients</p>
                    </div>
                    
                    <!-- Toggle Add Recipient Form Button -->
                    <button
                        class="px-3 py-1.5 rounded-md text-sm font-medium
                            bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                            transition-all"
                        on:click={() => showAddRecipientForm = !showAddRecipientForm}
                    >
                        {showAddRecipientForm ? 'Cancel' : '+ Add Recipient'}
                    </button>
                </div>

                <!-- Add Recipient Form -->
                {#if showAddRecipientForm}
                    <div class="bg-[#1a1a1a] rounded-lg p-3 mb-3" transition:slide={{ duration: 200 }}>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <input
                                type="text"
                                bind:value={newRecipient.name}
                                placeholder="Name"
                                class="w-full bg-[#2d2d2d] rounded px-3 py-2 text-sm border border-gray-800
                                    focus:outline-none focus:ring-1 focus:ring-gray-700"
                            />
                            <input
                                type="email"
                                bind:value={newRecipient.email}
                                placeholder="Email"
                                class="w-full bg-[#2d2d2d] rounded px-3 py-2 text-sm border border-gray-800
                                    focus:outline-none focus:ring-1 focus:ring-gray-700"
                            />
                            <input
                                type="text"
                                bind:value={newRecipient.organization}
                                placeholder="Organization (optional)"
                                class="w-full bg-[#2d2d2d] rounded px-3 py-2 text-sm border border-gray-800
                                    focus:outline-none focus:ring-1 focus:ring-gray-700 sm:col-span-2"
                            />
                        </div>
                        <div class="mt-3 flex justify-end">
                            <button
                                on:click={addRecipient}
                                disabled={!newRecipient.email || !newRecipient.name}
                                class="px-4 py-2 rounded text-sm font-medium whitespace-nowrap
                                    bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                                    transition-all disabled:opacity-50"
                            >
                                Add Recipient
                            </button>
                        </div>
                    </div>
                {/if}

                <!-- Recipients List -->
                <div class="space-y-2 max-h-[400px] overflow-y-auto pr-1">
                    {#if activeGroup.recipients.length === 0}
                        <div class="bg-[#1a1a1a] rounded-lg p-4 text-center text-gray-400">
                            No recipients in this group yet.
                        </div>
                    {:else}
                        {#each activeGroup.recipients as recipient, i}
                            <div class="bg-[#1a1a1a] rounded-lg p-3 flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
                                <div class="min-w-0 flex-1">
                                    <div class="font-medium truncate">{recipient.name}</div>
                                    <div class="text-sm text-gray-400 truncate">{recipient.email}</div>
                                    {#if recipient.organization}
                                        <div class="text-xs text-gray-500">{recipient.organization}</div>
                                    {/if}
                                </div>
                                <button
                                    on:click={() => removeRecipient(i)}
                                    class="text-gray-400 hover:text-red-400 transition-colors flex-shrink-0"
                                >
                                    Remove
                                </button>
                            </div>
                        {/each}
                    {/if}
                </div>
            </div>
        </div>
    </div>
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
        background: #1a1a1a;
    }

    .overflow-y-auto::-webkit-scrollbar-thumb {
        background-color: #4a5568;
        border-radius: 2px;
    }
</style> 