<script lang="ts">
    import { onMount } from 'svelte';
    import type { SmtpConfig, RecipientGroup, ChatMessage } from '$lib/types';
    import Header from '../../components/layout/Header.svelte';
    import ChatPanel from '../../components/chat/ChatPanel.svelte';
    import NewsletterEditor from '../../components/editor/NewsletterEditor.svelte';
    import SmtpSettings from '../../components/settings/SmtpSettings.svelte';
    import RecipientsManager from '../../components/settings/RecipientsManager.svelte';
    import OnboardingGuide from '../../components/OnboardingGuide.svelte';
    import Notification from '../../components/Notification.svelte';
    import { showOnboarding } from '$lib/stores';
    import { PUBLIC_API_URL, PUBLIC_AI_SERVICE_URL } from '$env/static/public';

    // Update page title
    const title = "NoobMail AI - Newsletter Management Made Simple";
    const description = "Create and send beautiful newsletters without any technical knowledge. AI-powered newsletter editor for beginners.";

    let onboardingStep = 1;
    let isSidebarCollapsed = false;
    let templatePrompt = '';
    let chatPanelComponent: ChatPanel;

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
        
        // If a template was selected, set it as the current message in the chat
        if (templatePrompt && chatPanelComponent) {
            chatPanelComponent.setPrompt(templatePrompt);
            templatePrompt = '';
        }
    }

    function handleUseTemplate(event: CustomEvent<string>) {
        templatePrompt = event.detail;
    }

    function showGuide() {
        onboardingStep = 1;
        $showOnboarding = true;
    }

    function toggleSidebar() {
        isSidebarCollapsed = !isSidebarCollapsed;
    }

    // State
    let htmlContent = '';
    let activeTab = 'main';
    let settingsTab = 'recipients';
    let isSending = false;
    let showChatPanel = true;
    let chatMessages: ChatMessage[] = [];
    let isGenerating = false;
    
    // Notification state
    let showNotification = false;
    let notificationMessage = '';
    let notificationType: 'success' | 'error' | 'info' = 'success';

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
                showNotificationMessage('Failed to send email', 'error');
            } else {
                showNotificationMessage('Email sent successfully!', 'success');
            }
        } catch (e) {
            error = 'Something went wrong. Please try again.';
            showNotificationMessage('Something went wrong. Please try again.', 'error');
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
    
    function showNotificationMessage(message: string, type: 'success' | 'error' | 'info' = 'success') {
        notificationMessage = message;
        notificationType = type;
        showNotification = true;
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            showNotification = false;
        }, 3000);
    }

    function handleChatUpdate(event: CustomEvent) {
        if ('message' in event.detail) {
            const userPrompt = event.detail.message;
            const contextContents = event.detail.selectedContexts || [];
            
            // Check if the user is asking about a specific context file
            let userPromptModified = userPrompt;
            let contextIncluded = false;
            
            if (contextContents.length > 0) {
                // First, check for explicit mentions using @filename syntax
                const mentionRegex = /@([^\s@]+)/g;
                const mentions = userPrompt.match(mentionRegex);
                
                if (mentions) {
                    for (const mention of mentions) {
                        const fileName = mention.substring(1); // Remove the @ symbol
                        
                        // Find matching context file
                        const matchedContext = contextContents.find(
                            (ctx: {name: string, content: string, type: string}) => ctx.name.toLowerCase() === fileName.toLowerCase()
                        );
                        
                        if (matchedContext) {
                            userPromptModified += `\n\nHere is the content of ${matchedContext.name} that I'm referring to:\n\n${matchedContext.content}`;
                            contextIncluded = true;
                            break; // Only include the first matching file to avoid making the prompt too long
                        }
                    }
                }
                
                // If no @filename mentions were found, fall back to checking if the filename appears in the message
                if (!contextIncluded) {
                    for (const ctx of contextContents) {
                        // If the user mentions the file name in their message, append its content
                        if (userPromptModified.toLowerCase().includes(ctx.name.toLowerCase())) {
                            userPromptModified += `\n\nHere is the content of ${ctx.name} that I'm referring to:\n\n${ctx.content}`;
                            contextIncluded = true;
                            break; // Only include the first matching file to avoid making the prompt too long
                        }
                    }
                }
            }
            
            const userMessage: ChatMessage = {
                role: 'user' as const,
                content: contextIncluded ? userPromptModified : userPrompt,
                timestamp: new Date(),
                selectedContexts: event.detail.selectedContexts?.map((ctx: {name: string}) => ctx.name) || []
            };
            
            chatMessages = [...chatMessages, userMessage];
            isGenerating = true;
            
            // Make an actual API call to the AI service
            fetch(`${PUBLIC_AI_SERVICE_URL}/ai/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: userMessage.content,
                    context: chatMessages.map(msg => ({
                        role: msg.role,
                        content: msg.content
                    })).slice(0, -1), // Exclude the message we just added
                    contextFiles: contextContents // Add the selected context files
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('AI service request failed');
                }
                return response.json();
            })
            .then(data => {
                const assistantMessage: ChatMessage = {
                    role: 'assistant' as const,
                    content: data.response || data.message || 'Sorry, I could not generate a response.',
                    timestamp: new Date()
                };
                chatMessages = [...chatMessages, assistantMessage];
            })
            .catch(error => {
                console.error('Error calling AI service:', error);
                const errorMessage: ChatMessage = {
                    role: 'assistant' as const,
                    content: 'Sorry, there was an error processing your request. Please try again later.',
                    timestamp: new Date()
                };
                chatMessages = [...chatMessages, errorMessage];
            })
            .finally(() => {
                isGenerating = false;
            });
        } else if ('showChatPanel' in event.detail) {
            showChatPanel = event.detail.showChatPanel;
        } else if ('applyHtml' in event.detail) {
            // Apply the HTML to the editor
            htmlContent = event.detail.applyHtml;
            
            // Switch to the editor tab if we're not already there
            if (activeTab !== 'main') {
                activeTab = 'main';
            }
            
            // Show a notification
            showNotificationMessage('Newsletter HTML applied to editor!', 'success');
        } else if ('notification' in event.detail) {
            // Handle notification events from the ChatPanel
            const { message, type } = event.detail.notification;
            showNotificationMessage(message, type);
        }
    }
</script>

{#if $showOnboarding}
    <OnboardingGuide 
        currentStep={onboardingStep}
        on:stepChange={handleStepChange}
        on:complete={handleOnboardingComplete}
        on:useTemplate={handleUseTemplate}
    />
{/if}

{#if showNotification}
    <Notification 
        message={notificationMessage} 
        type={notificationType} 
        on:close={() => showNotification = false}
    />
{/if}

<div class="min-h-screen bg-[#1a1a1a] text-gray-100 flex flex-col h-screen overflow-hidden">
    <Header {activeTab} on:tabChange={handleTabChange} />

    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden">
        <!-- Left Sidebar -->
        <div class="{isSidebarCollapsed ? 'w-12' : 'w-64'} bg-[#2d2d2d] border-r border-gray-800 flex flex-col transition-all duration-300 ease-in-out">
            <!-- Toggle Button -->
            <button 
                class="p-3 text-gray-400 hover:text-white self-end"
                on:click={toggleSidebar}
                aria-label={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
                {#if isSidebarCollapsed}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                    </svg>
                {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                    </svg>
                {/if}
            </button>
            
            <!-- Sidebar Content -->
            <div class="flex-1 flex flex-col justify-between p-3">
                <!-- Top Section -->
                <div class="{isSidebarCollapsed ? 'hidden' : 'block'}">
                    <h3 class="text-sm font-medium mb-2">Recipients</h3>
                    <div class="text-sm text-gray-400 mb-4">
                        {activeGroup.recipients.length} recipients selected
                    </div>
                </div>
                
                <!-- Bottom Section with Send Button -->
                <div class="mt-auto">
                    {#if !isSidebarCollapsed}
                        <button
                            on:click={sendEmail}
                            disabled={isSending || !htmlContent || !activeGroup.recipients.length || !smtpConfig.server}
                            class="w-full px-4 py-2 rounded-md text-sm font-medium
                                bg-gradient-to-r from-green-600 to-emerald-600 
                                hover:from-green-500 hover:to-emerald-500
                                transition-all disabled:opacity-50 whitespace-nowrap"
                        >
                            {#if isSending}
                                <span class="flex items-center justify-center">
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
                    {:else}
                        <!-- Collapsed Send Button -->
                        <button
                            on:click={sendEmail}
                            disabled={isSending || !htmlContent || !activeGroup.recipients.length || !smtpConfig.server}
                            class="w-full p-2 rounded-md text-sm font-medium
                                bg-gradient-to-r from-green-600 to-emerald-600 
                                hover:from-green-500 hover:to-emerald-500
                                transition-all disabled:opacity-50 flex justify-center"
                            title="Send Email"
                        >
                            {#if isSending}
                                <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                                </svg>
                            {:else}
                                📤
                            {/if}
                        </button>
                    {/if}
                    
                    <!-- Chat Toggle Button (Mobile Only) -->
                    <button
                        class="lg:hidden w-full mt-2 px-3 py-2 rounded-md text-sm font-medium
                            bg-gradient-to-r from-purple-600 to-blue-600 
                            hover:from-purple-500 hover:to-blue-500
                            transition-all"
                        on:click={() => showChatPanel = !showChatPanel}
                    >
                        {#if isSidebarCollapsed}
                            {showChatPanel ? '🤖' : '🤖'}
                        {:else}
                            {showChatPanel ? 'Hide AI' : 'Show AI'}
                        {/if}
                    </button>
                </div>
            </div>
        </div>

        <!-- Editor/Preview Section -->
        <div class="flex-1 p-2 md:p-4 flex flex-col overflow-auto">
            {#if activeTab === 'settings'}
                <!-- Settings Panel -->
                <div class="flex-1 p-2 md:p-4 overflow-auto">
                    <div class="max-w-5xl mx-auto">
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
                            <div class="p-3 md:p-4 lg:p-5">
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
            <div class="fixed inset-0 z-50 lg:static lg:z-auto lg:h-full lg:flex-shrink-0">
                <button
                    type="button"
                    class="absolute inset-0 bg-black/50 lg:hidden"
                    aria-label="Close chat panel"
                    on:click={() => showChatPanel = false}
                    on:keydown={(e) => e.key === 'Escape' && (showChatPanel = false)}
                ></button>
                <div class="absolute right-0 top-0 bottom-0 w-full max-w-md sm:max-w-lg lg:w-[450px] lg:static lg:h-full overflow-hidden">
                    <ChatPanel 
                        bind:chatMessages
                        bind:isGenerating
                        bind:this={chatPanelComponent}
                        on:update={handleChatUpdate}
                    />
                </div>
            </div>
        {/if}
    </div>
</div>

<style>
    :global(body) {
        background-color: #1a1a1a;
        margin: 0;
        overflow: hidden;
        height: 100vh;
    }

    @media (max-width: 1024px) {
        :global(body) {
            overflow: hidden;
        }
    }
</style> 