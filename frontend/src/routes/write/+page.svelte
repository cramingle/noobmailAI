<script lang="ts">
    import { onMount } from 'svelte';
    import type { SmtpConfig, RecipientGroup, ChatMessage } from '$lib/types';
    import Header from '../../components/layout/Header.svelte';
    import ChatPanel from '../../components/chat/ChatPanel.svelte';
    import NewsletterEditor from '../../components/editor/NewsletterEditor.svelte';
    import SmtpSettings from '../../components/settings/SmtpSettings.svelte';
    import RecipientsManager from '../../components/settings/RecipientsManager.svelte';
    import OnboardingGuide from '../../components/OnboardingGuide.svelte';
    import { showOnboarding } from '$lib/stores';
    import { PUBLIC_API_URL } from '$env/static/public';

    // Update page title
    const title = "NoobMail AI - Newsletter Management Made Simple";
    const description = "Create and send beautiful newsletters without any technical knowledge. AI-powered newsletter editor for beginners.";

    let onboardingStep = 1;

    onMount(() => {
        document.title = title;
        // Add meta description
        const metaDescription = document.createElement('meta');
        metaDescription.name = 'description';
        metaDescription.content = description;
        document.head.appendChild(metaDescription);

        // Check if first visit
        const hasVisited = localStorage.getItem('noobmail_visited');
        if (!hasVisited) {
            $showOnboarding = true;
            localStorage.setItem('noobmail_visited', 'true');
        }
    });

    function handleStepChange(event: CustomEvent<number>) {
        onboardingStep = event.detail;
    }

    function handleOnboardingComplete() {
        $showOnboarding = false;
    }

    function showGuide() {
        onboardingStep = 1;
        $showOnboarding = true;
    }

    // State
    let htmlContent = '';
    let activeTab = 'main';
    let settingsTab = 'recipients';
    let isSending = false;
    let showChatPanel = true;
    let chatMessages: ChatMessage[] = [];
    let isGenerating = false;

    // SMTP Configuration
    let smtpConfig: SmtpConfig = {
        server: '',
        port: '587',
        email: '',
        password: '',
        name: ''
    };

    // Recipients Management
    let recipientGroups: RecipientGroup[] = [
        { name: 'All Recipients', recipients: [] }
    ];
    let activeGroup = recipientGroups[0];

    async function sendEmail() {
        isSending = true;
        let error = '';
        
        try {
            const response = await fetch(`${PUBLIC_API_URL}/send-email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: htmlContent,
                    recipients: activeGroup.recipients,
                    smtp: smtpConfig
                })
            });

            if (!response.ok) {
                error = 'Failed to send email';
            }
        } catch (e) {
            error = 'Something went wrong. Please try again.';
        } finally {
            isSending = false;
        }
    }

    function handleContentUpdate(event: CustomEvent<string>) {
        htmlContent = event.detail;
    }

    function handleTabChange(event: CustomEvent<string>) {
        activeTab = event.detail;
    }
</script>

{#if $showOnboarding}
    <OnboardingGuide 
        currentStep={onboardingStep}
        on:stepChange={handleStepChange}
        on:complete={handleOnboardingComplete}
    />
{/if}

<div class="min-h-screen bg-[#1a1a1a] text-gray-100 flex flex-col">
    <Header {activeTab} on:tabChange={handleTabChange} />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col lg:flex-row">
        <!-- Editor/Preview Section -->
        <div class="flex-1 p-2 md:p-4 flex flex-col">
            {#if activeTab === 'settings'}
                <!-- Settings Panel -->
                <div class="flex-1 p-2 md:p-4">
                    <div class="max-w-4xl mx-auto">
                        <div class="bg-[#2d2d2d] rounded-lg shadow-xl">
                            <!-- Settings Tabs -->
                            <div class="border-b border-gray-800">
                                <div class="flex">
                                    <button
                                        class="px-3 md:px-4 py-3 text-sm font-medium transition-all border-b-2
                                            {settingsTab === 'recipients' ? 'border-purple-500 text-white' : 'border-transparent text-gray-400 hover:text-white'}"
                                        on:click={() => settingsTab = 'recipients'}
                                    >
                                        👥 Recipients
                                    </button>
                                    <button
                                        class="px-3 md:px-4 py-3 text-sm font-medium transition-all border-b-2
                                            {settingsTab === 'smtp' ? 'border-purple-500 text-white' : 'border-transparent text-gray-400 hover:text-white'}"
                                        on:click={() => settingsTab = 'smtp'}
                                    >
                                        📧 SMTP Settings
                                    </button>
                                </div>
                            </div>

                            <!-- Settings Content -->
                            <div class="p-3 md:p-6">
                                {#if settingsTab === 'recipients'}
                                    <RecipientsManager bind:recipientGroups bind:activeGroup />
                                {:else}
                                    <SmtpSettings bind:smtpConfig />
                                {/if}
                            </div>
                        </div>
                    </div>
                </div>
            {:else}
                <NewsletterEditor bind:htmlContent on:contentUpdate={handleContentUpdate} />
            {/if}
        </div>

        <!-- Chat Panel - Hidden on mobile by default -->
        {#if showChatPanel}
            <div class="fixed inset-0 z-50 lg:static lg:z-auto">
                <button
                    type="button"
                    class="absolute inset-0 bg-black/50 lg:hidden"
                    aria-label="Close chat panel"
                    on:click={() => showChatPanel = false}
                    on:keydown={(e) => e.key === 'Escape' && (showChatPanel = false)}
                ></button>
                <div class="absolute right-0 top-0 bottom-0 w-full max-w-sm sm:max-w-md lg:w-96 lg:static">
                    <ChatPanel 
                        bind:chatMessages
                        bind:isGenerating
                        on:contentUpdate={handleContentUpdate}
                    />
                </div>
            </div>
        {/if}
    </div>

    <!-- Bottom Action Bar -->
    <div class="p-3 md:p-4 bg-[#2d2d2d] border-t border-gray-800">
        <div class="flex justify-between items-center">
            <div class="flex items-center space-x-4">
                <span class="text-sm text-gray-400">
                    {activeGroup.recipients.length} recipients selected
                </span>
            </div>
            <!-- Chat Toggle Button (Mobile Only) -->
            <button
                class="lg:hidden px-3 py-2 rounded-md text-sm font-medium
                    bg-gradient-to-r from-purple-600 to-blue-600 
                    hover:from-purple-500 hover:to-blue-500
                    transition-all mr-2"
                on:click={() => showChatPanel = !showChatPanel}
            >
                {showChatPanel ? 'Hide AI' : 'Show AI'}
            </button>
            <button
                on:click={sendEmail}
                disabled={isSending || !htmlContent || !activeGroup.recipients.length || !smtpConfig.server}
                class="px-4 md:px-6 py-2 rounded-md text-sm font-medium
                    bg-gradient-to-r from-green-600 to-emerald-600 
                    hover:from-green-500 hover:to-emerald-500
                    transition-all disabled:opacity-50 whitespace-nowrap"
            >
                {#if isSending}
                    <span class="flex items-center">
                        <svg class="animate-spin -ml-1 mr-2 h-4 w-4" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                        </svg>
                        Sending...
                    </span>
                {:else}
                    📤 Send
                {/if}
            </button>
        </div>
    </div>
</div>

<style>
    :global(body) {
        background-color: #1a1a1a;
        margin: 0;
        overflow-x: hidden;
        overflow-y: auto;
    }

    @media (max-width: 1024px) {
        :global(body) {
            overflow-y: auto;
        }
    }
</style> 