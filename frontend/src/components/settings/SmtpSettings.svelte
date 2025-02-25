<!-- SmtpSettings.svelte -->
<script lang="ts">
    import type { SmtpConfig, EmailProvider } from '$lib/types';
    import { slide } from 'svelte/transition';
    import { PUBLIC_API_URL } from '$env/static/public';

    export let smtpConfig: SmtpConfig;
    
    let showSmtpHelper = false;
    let isDetectingConfig = false;
    let isTestingConfig = false;
    let smtpSuggestions = '';
    let message = '';
    let error = '';

    // Function to detect SMTP settings
    async function detectSmtpSettings() {
        isDetectingConfig = true;
        try {
            const response = await fetch(`${PUBLIC_API_URL}/detect-smtp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: smtpConfig.email })
            });

            if (response.ok) {
                const data = await response.json();
                smtpConfig.server = data.server;
                smtpConfig.port = data.port;
                message = 'SMTP settings detected! Please enter your password to complete the setup.';
            } else {
                error = 'Could not detect SMTP settings automatically';
            }
        } catch (e) {
            error = 'Failed to detect SMTP settings';
        } finally {
            isDetectingConfig = false;
        }
    }

    // Function to get SMTP help
    function getSmtpHelp(provider: EmailProvider) {
        const helpText = {
            'gmail': {
                server: 'smtp.gmail.com',
                port: '587',
                instructions: `
                    1. Go to your Google Account settings
                    2. Enable 2-Step Verification if not already enabled
                    3. Go to Security > App passwords
                    4. Generate a new app password for 'Mail'
                    5. Use that 16-character password here
                `
            },
            'outlook': {
                server: 'smtp.office365.com',
                port: '587',
                instructions: `
                    1. Use your complete Outlook email address
                    2. Use your regular Outlook password
                    3. If you have 2FA enabled, you'll need to create an app password
                `
            },
            'yahoo': {
                server: 'smtp.mail.yahoo.com',
                port: '587',
                instructions: `
                    1. Go to Yahoo Account Security settings
                    2. Enable 2-Step Verification if not already enabled
                    3. Generate an app password
                    4. Use that app password here
                `
            }
        };
        
        return helpText[provider];
    }

    async function testSmtpConfig() {
        isTestingConfig = true;
        try {
            const response = await fetch(`${PUBLIC_API_URL}/test-smtp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(smtpConfig)
            });

            if (response.ok) {
                message = 'SMTP configuration is valid!';
            } else {
                error = 'Invalid SMTP configuration';
            }
        } catch (e) {
            error = 'Failed to test SMTP configuration';
        } finally {
            isTestingConfig = false;
        }
    }
</script>

<div class="max-w-xl mx-auto space-y-6">
    <div class="flex justify-between items-center">
        <h2 class="text-lg font-bold">SMTP Configuration</h2>
        <button
            on:click={() => showSmtpHelper = !showSmtpHelper}
            class="px-3 py-1.5 rounded-md text-sm font-medium
                bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                transition-all flex items-center space-x-2"
        >
            <span>🤖</span>
            <span>AI Setup Help</span>
        </button>
    </div>

    {#if showSmtpHelper}
        <div class="bg-[#1a1a1a] rounded-lg p-4 border border-gray-800" transition:slide>
            <div class="text-sm space-y-4">
                <p>Select your email provider for automatic configuration:</p>
                <div class="grid grid-cols-3 gap-2">
                    {#each ['gmail', 'outlook', 'yahoo'] as provider}
                        <button
                            class="p-2 rounded bg-[#2d2d2d] hover:bg-gray-700 transition-colors capitalize"
                            on:click={() => {
                                const help = getSmtpHelp(provider as EmailProvider);
                                if (help) {
                                    smtpConfig.server = help.server;
                                    smtpConfig.port = help.port;
                                    smtpSuggestions = help.instructions;
                                }
                            }}
                        >
                            {provider}
                        </button>
                    {/each}
                </div>
                {#if smtpSuggestions}
                    <div class="mt-4 p-3 bg-[#2d2d2d] rounded">
                        <h3 class="font-medium mb-2">Setup Instructions:</h3>
                        <pre class="text-xs whitespace-pre-wrap text-gray-300">{smtpSuggestions}</pre>
                    </div>
                {/if}
                <div class="flex items-center justify-between mt-4">
                    <button
                        class="text-sm text-gray-400 hover:text-white transition-colors"
                        on:click={() => showSmtpHelper = false}
                    >
                        Close Helper
                    </button>
                    <button
                        on:click={detectSmtpSettings}
                        disabled={!smtpConfig.email || isDetectingConfig}
                        class="px-3 py-1.5 rounded-md text-sm font-medium
                            bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700
                            transition-all disabled:opacity-50"
                    >
                        {#if isDetectingConfig}
                            <span class="flex items-center space-x-2">
                                <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                                </svg>
                                <span>Detecting...</span>
                            </span>
                        {:else}
                            Auto-detect Settings
                        {/if}
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <div class="space-y-4">
        <div>
            <label for="smtp-server" class="block text-sm font-medium mb-1">SMTP Server</label>
            <div class="relative">
                <input
                    id="smtp-server"
                    type="text"
                    bind:value={smtpConfig.server}
                    placeholder="e.g., smtp.gmail.com"
                    class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-3 py-2 text-sm
                        focus:outline-none focus:ring-1 focus:ring-gray-700"
                />
                <div class="absolute right-3 top-2 text-gray-400 text-xs">
                    e.g., smtp.gmail.com
                </div>
            </div>
        </div>
        <div>
            <label class="block text-sm font-medium mb-1">Port</label>
            <div class="relative">
                <input
                    type="text"
                    bind:value={smtpConfig.port}
                    placeholder="587 or 465"
                    class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-3 py-2 text-sm
                        focus:outline-none focus:ring-1 focus:ring-gray-700"
                />
                <div class="absolute right-3 top-2 text-gray-400 text-xs">
                    Usually 587 (TLS) or 465 (SSL)
                </div>
            </div>
        </div>
        <div>
            <label class="block text-sm font-medium mb-1">Email</label>
            <input
                type="email"
                bind:value={smtpConfig.email}
                placeholder="your@email.com"
                class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-3 py-2 text-sm
                    focus:outline-none focus:ring-1 focus:ring-gray-700"
            />
        </div>
        <div>
            <label class="block text-sm font-medium mb-1">Password</label>
            <div class="relative">
                <input
                    type="password"
                    bind:value={smtpConfig.password}
                    placeholder="SMTP Password or App Password"
                    class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-3 py-2 text-sm
                        focus:outline-none focus:ring-1 focus:ring-gray-700"
                />
                <div class="absolute right-3 top-2 text-gray-400 text-xs">
                    Use app password if 2FA is enabled
                </div>
            </div>
        </div>
        <div>
            <label class="block text-sm font-medium mb-1">Sender Name</label>
            <input
                type="text"
                bind:value={smtpConfig.name}
                placeholder="Your Name"
                class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-3 py-2 text-sm
                    focus:outline-none focus:ring-1 focus:ring-gray-700"
            />
        </div>
        <button
            on:click={testSmtpConfig}
            disabled={isTestingConfig}
            class="w-full px-4 py-2 rounded-md text-sm font-medium
                bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                transition-all disabled:opacity-50 mt-4"
        >
            {#if isTestingConfig}
                <span class="flex items-center justify-center">
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Testing...
                </span>
            {:else}
                🔒 Test Configuration
            {/if}
        </button>
    </div>

    {#if message}
        <div class="bg-green-900/50 border border-green-800 text-green-100 px-4 py-2 rounded-md text-sm">
            {message}
        </div>
    {/if}

    {#if error}
        <div class="bg-red-900/50 border border-red-800 text-red-100 px-4 py-2 rounded-md text-sm">
            {error}
        </div>
    {/if}
</div> 