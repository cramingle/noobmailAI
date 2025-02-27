<!-- RecipientsManager.svelte -->
<script lang="ts">
    import type { Recipient, RecipientGroup } from '$lib/types';
    import { slide } from 'svelte/transition';
    import { PUBLIC_API_URL } from '$env/static/public';

    export let recipientGroups: RecipientGroup[];
    export let activeGroup: RecipientGroup;
    export let htmlContent: string = '';
    export let smtpConfig: any;

    let newRecipient: Recipient = { name: '', email: '', organization: '' };
    let showNewGroupModal = false;
    let newGroupName = '';
    let showAddRecipientForm = false;
    let isSending = false;
    let showTooltip = false;
    let error = '';
    let success = '';
    let testRecipient: Recipient = { name: '', email: '', organization: '' };

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

    function getRequirementStatus() {
        const requirements = {
            recipients: activeGroup.recipients.length > 0,
            content: !!htmlContent,
            smtp: !!(smtpConfig?.server && smtpConfig?.email && smtpConfig?.password)
        };

        return {
            ...requirements,
            allMet: Object.values(requirements).every(Boolean)
        };
    }

    async function sendEmail() {
        isSending = true;
        try {
            const response = await fetch(`${PUBLIC_API_URL}/send-email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                mode: 'cors',
                body: JSON.stringify({
                    content: htmlContent,
                    recipients: activeGroup.recipients,
                    smtp: smtpConfig
                })
            });

            if (!response.ok) throw new Error('Failed to send email');
            
            const result = await response.json();
            if (result.status === 'success') {
                // Handle success
            }
        } catch (error) {
            console.error('Error sending email:', error);
        } finally {
            isSending = false;
        }
    }

    // Function to send test email
    async function sendTestEmail() {
        isSending = true;
        error = '';
        success = '';

        try {
            const response = await fetch(`${PUBLIC_API_URL}/send-email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                mode: 'cors',
                body: JSON.stringify({
                    content: htmlContent,
                    recipients: [
                        {
                            name: testRecipient.name,
                            email: testRecipient.email,
                            organization: testRecipient.organization || undefined
                        }
                    ],
                    smtp: smtpConfig,
                    use_ai: false
                })
            });

            const data = await response.json();

            if (response.ok) {
                success = 'Test email sent successfully!';
                testRecipient = { name: '', email: '', organization: '' };
            } else {
                error = data.detail || 'Failed to send test email';
            }
        } catch (e: any) {
            error = e.message || 'Failed to send test email';
        } finally {
            isSending = false;
        }
    }
</script>

<div class="space-y-3">
    <!-- Add Recipient Button -->
    <button
        class="w-full px-2 py-1.5 rounded-md text-xs font-medium
            bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
            transition-all flex items-center justify-center gap-2"
        on:click={() => showAddRecipientForm = !showAddRecipientForm}
    >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
        <span>{showAddRecipientForm ? 'Cancel' : 'Add Recipient'}</span>
    </button>

    <!-- Add Recipient Form -->
    {#if showAddRecipientForm}
        <div class="space-y-2" transition:slide={{ duration: 200 }}>
            <input
                type="text"
                bind:value={newRecipient.name}
                placeholder="Name"
                class="w-full bg-[#1a1a1a] rounded px-2 py-1.5 text-xs border border-gray-800
                    focus:outline-none focus:ring-1 focus:ring-gray-700"
            />
            <input
                type="email"
                bind:value={newRecipient.email}
                placeholder="Email"
                class="w-full bg-[#1a1a1a] rounded px-2 py-1.5 text-xs border border-gray-800
                    focus:outline-none focus:ring-1 focus:ring-gray-700"
            />
            <input
                type="text"
                bind:value={newRecipient.organization}
                placeholder="Organization (optional)"
                class="w-full bg-[#1a1a1a] rounded px-2 py-1.5 text-xs border border-gray-800
                    focus:outline-none focus:ring-1 focus:ring-gray-700"
            />
            <button
                on:click={addRecipient}
                disabled={!newRecipient.email || !newRecipient.name}
                class="w-full px-2 py-1.5 rounded text-xs font-medium
                    bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                    transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <span>Add</span>
            </button>
        </div>
    {/if}

    <!-- Recipients List -->
    <div class="space-y-1.5 max-h-[300px] overflow-y-auto pr-1">
        {#if activeGroup.recipients.length === 0}
            <div class="bg-[#1a1a1a] rounded p-2 text-center text-xs text-gray-400">
                No recipients in this group yet.
            </div>
        {:else}
            {#each activeGroup.recipients as recipient, i}
                <div class="bg-[#1a1a1a] rounded p-2 text-xs">
                    <div class="flex justify-between items-start gap-2">
                        <div class="min-w-0 flex-1">
                            <div class="font-medium truncate">{recipient.name}</div>
                            <div class="text-gray-400 truncate">{recipient.email}</div>
                            {#if recipient.organization}
                                <div class="text-gray-500 text-[10px] truncate">{recipient.organization}</div>
                            {/if}
                        </div>
                        <button
                            on:click={() => removeRecipient(i)}
                            class="text-gray-500 hover:text-red-400 transition-colors"
                            title="Remove recipient"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    </div>
                </div>
            {/each}
        {/if}
    </div>

    <!-- New Group Button -->
    <button
        class="w-full px-2 py-1.5 rounded-md text-xs font-medium
            bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700
            transition-all border border-gray-700 flex items-center justify-center gap-2"
        on:click={() => showNewGroupModal = true}
    >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>New Group</span>
    </button>

    <!-- New Group Modal -->
    {#if showNewGroupModal}
        <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" transition:slide>
            <div class="bg-[#2d2d2d] rounded-lg p-4 w-full max-w-xs mx-4 space-y-4">
                <h3 class="text-sm font-medium">Create New Group</h3>
                <input
                    type="text"
                    bind:value={newGroupName}
                    placeholder="Enter group name"
                    class="w-full bg-[#1a1a1a] rounded px-2 py-1.5 text-xs border border-gray-800
                        focus:outline-none focus:ring-1 focus:ring-gray-700"
                    on:keydown={(e) => e.key === 'Enter' && addGroup()}
                />
                <div class="flex justify-end gap-2">
                    <button
                        class="px-3 py-1.5 rounded text-xs font-medium text-gray-400 hover:text-white transition-colors"
                        on:click={() => {
                            showNewGroupModal = false;
                            newGroupName = '';
                        }}
                    >
                        Cancel
                    </button>
                    <button
                        class="px-3 py-1.5 rounded text-xs font-medium
                            bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                            transition-all disabled:opacity-50"
                        disabled={!newGroupName.trim()}
                        on:click={addGroup}
                    >
                        Create
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Send Email Section -->
    <div class="mt-4 space-y-2">
        <div class="relative">
            <button
                on:click={sendEmail}
                on:mouseenter={() => showTooltip = true}
                on:mouseleave={() => showTooltip = false}
                disabled={!getRequirementStatus().allMet || isSending}
                class="w-full px-3 py-2 rounded-md text-sm font-medium
                    bg-gradient-to-r from-green-600 to-emerald-600 
                    hover:from-green-500 hover:to-emerald-500
                    transition-all disabled:opacity-50 disabled:cursor-not-allowed
                    flex items-center justify-center gap-2"
            >
                {#if isSending}
                    <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    <span>Sending...</span>
                {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                    </svg>
                    <span>Send to {activeGroup.recipients.length} Recipients</span>
                {/if}
            </button>

            {#if showTooltip && !getRequirementStatus().allMet}
                <div class="absolute bottom-full left-0 right-0 mb-2 p-2 bg-gray-900 rounded-md text-xs text-white shadow-lg"
                    transition:slide={{ duration: 100 }}>
                    <div class="space-y-1">
                        <div class="flex items-center gap-2">
                            <span class={getRequirementStatus().recipients ? 'text-green-400' : 'text-red-400'}>
                                {getRequirementStatus().recipients ? '✓' : '✗'}
                            </span>
                            <span>Add at least one recipient</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class={getRequirementStatus().content ? 'text-green-400' : 'text-red-400'}>
                                {getRequirementStatus().content ? '✓' : '✗'}
                            </span>
                            <span>Create email content</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class={getRequirementStatus().smtp ? 'text-green-400' : 'text-red-400'}>
                                {getRequirementStatus().smtp ? '✓' : '✗'}
                            </span>
                            <span>Configure SMTP settings</span>
                        </div>
                    </div>
                </div>
            {/if}
        </div>

        {#if activeGroup.recipients.length > 0}
            <div class="text-xs text-gray-400 text-center">
                Ready to send to {activeGroup.recipients.length} recipient{activeGroup.recipients.length === 1 ? '' : 's'}
            </div>
        {/if}
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