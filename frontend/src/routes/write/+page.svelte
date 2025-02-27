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
    import { writable } from 'svelte/store';
    import NewsletterScheduler from '../../components/settings/NewsletterScheduler.svelte';

    // Update page title
    const title = "NoobMail AI - Sending Beautiful and Professional Emails Easily";
    const description = "Create and send beautiful newsletters without any technical knowledge. AI-powered newsletter editor for beginners.";

    let onboardingStep = 1;
    let isSidebarCollapsed = false;
    let templatePrompt = '';
    let chatPanelComponent: ChatPanel;

    // Email type state
    let emailType: "newsletter" | "job_application" = "newsletter";

    // New state for sidebar navigation
    let activeSidebarTab: 'recipients' | 'scheduler' | 'smtp' = 'recipients';

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

    function handleContentUpdate(event: CustomEvent<string>) {
        htmlContent = event.detail;
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
            
            // Show a notification
            showNotificationMessage('Newsletter HTML applied to editor!', 'success');
        } else if ('notification' in event.detail) {
            // Handle notification events from the ChatPanel
            const { message, type } = event.detail.notification;
            showNotificationMessage(message, type);
        }
    }

    // Handle email type change from OnboardingGuide
    function handleEmailTypeChange(event: CustomEvent<"newsletter" | "job_application">) {
        emailType = event.detail;
    }
</script>

{#if $showOnboarding}
    <OnboardingGuide 
        currentStep={onboardingStep}
        on:stepChange={handleStepChange}
        on:complete={handleOnboardingComplete}
        on:useTemplate={handleUseTemplate}
        {emailType} 
        on:emailTypeChange={handleEmailTypeChange} 
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
    <Header />

    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden">
        <!-- Left Sidebar -->
        <div class="{isSidebarCollapsed ? 'w-12' : 'w-64'} bg-[#2d2d2d] border-r border-gray-800 flex flex-col transition-all duration-300 ease-in-out">
            <!-- Sidebar Navigation -->
            <div class="p-2 border-b border-gray-800 flex {isSidebarCollapsed ? 'flex-col' : 'gap-2'}">
                <!-- Toggle Button -->
                <button 
                    class="p-2 text-gray-400 hover:text-white rounded-md hover:bg-gray-800 transition-colors"
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

                <!-- Recipients Icon -->
                <button 
                    class="p-2 rounded-md transition-colors {activeSidebarTab === 'recipients' ? 'text-white bg-gray-800' : 'text-gray-400 hover:text-white hover:bg-gray-800'}"
                    on:click={() => activeSidebarTab = 'recipients'}
                    title="Recipients"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                </button>

                <!-- Scheduler Icon -->
                <button 
                    class="p-2 rounded-md transition-colors {activeSidebarTab === 'scheduler' ? 'text-white bg-gray-800' : 'text-gray-400 hover:text-white hover:bg-gray-800'}"
                    on:click={() => activeSidebarTab = 'scheduler'}
                    title="Scheduled Emails"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </button>

                <!-- SMTP Settings Icon -->
                <button 
                    class="p-2 rounded-md transition-colors {activeSidebarTab === 'smtp' ? 'text-white bg-gray-800' : 'text-gray-400 hover:text-white hover:bg-gray-800'}"
                    on:click={() => activeSidebarTab = 'smtp'}
                    title="SMTP Settings"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                </button>
            </div>
            
            <!-- Sidebar Content -->
            <div class="flex-1 flex flex-col justify-between p-3">
                <!-- Top Section -->
                <div class="{isSidebarCollapsed ? 'hidden' : 'block'} space-y-4">
                    {#if activeSidebarTab === 'recipients'}
                        <!-- Recipients Section -->
                        <div class="bg-[#1a1a1a] rounded-lg p-3">
                            <h3 class="text-sm font-semibold mb-3 flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                                </svg>
                                <span>Recipients</span>
                            </h3>
                            <div class="text-sm text-gray-400">
                                <div class="flex items-center justify-between">
                                    <span>{activeGroup.name}</span>
                                    <span class="text-xs bg-gray-800 px-2 py-0.5 rounded">
                                        {activeGroup.recipients.length}
                                    </span>
                                </div>
                            </div>
                            <RecipientsManager 
                                bind:recipientGroups 
                                bind:activeGroup 
                                {htmlContent}
                                {smtpConfig}
                            />
                        </div>
                    {:else if activeSidebarTab === 'scheduler'}
                        <!-- Scheduler Section -->
                        <div class="bg-[#1a1a1a] rounded-lg p-3">
                            <h3 class="text-sm font-semibold mb-3 flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span>Scheduled Emails</span>
                            </h3>
                            <NewsletterScheduler {recipientGroups} isCompact={true} />
                        </div>
                    {:else if activeSidebarTab === 'smtp'}
                        <!-- SMTP Settings Section -->
                        <div class="bg-[#1a1a1a] rounded-lg p-3">
                            <h3 class="text-sm font-semibold mb-3 flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                <span>SMTP Settings</span>
                            </h3>
                            <SmtpSettings bind:smtpConfig />
                        </div>
                    {/if}
                </div>
                
                <!-- Bottom Section with Chat Toggle Button -->
                <div class="mt-auto">
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
            <NewsletterEditor bind:htmlContent on:contentUpdate={handleContentUpdate} />
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
                        {emailType}
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