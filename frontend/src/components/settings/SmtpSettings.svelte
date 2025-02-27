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

    const providers: EmailProvider[] = ['gmail', 'outlook', 'yahoo'];

    // Function to detect SMTP settings
    async function detectSmtpSettings() {
        isDetectingConfig = true;
        try {
            const response = await fetch(`${PUBLIC_API_URL}/detect-smtp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                mode: 'cors',
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
        const help = {
            gmail: {
                server: 'smtp.gmail.com',
                port: '587',
                instructions: `For Gmail:\n1. Enable 2-Step Verification\n2. Generate an App Password\n3. Use your Gmail address and the App Password`
            },
            outlook: {
                server: 'smtp.office365.com',
                port: '587',
                instructions: `For Outlook:\n1. Use your full email address\n2. Use your regular password or create an App Password if using 2FA`
            },
            yahoo: {
                server: 'smtp.mail.yahoo.com',
                port: '587',
                instructions: `For Yahoo:\n1. Enable 2-Step Verification\n2. Generate an App Password\n3. Use your Yahoo address and the App Password`
            }
        } as const;
        return help[provider];
    }

    async function testSmtpConfig() {
        isTestingConfig = true;
        try {
            const response = await fetch(`${PUBLIC_API_URL}/test-smtp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                mode: 'cors',
                body: JSON.stringify(smtpConfig)
            });

            if (response.ok) {
                message = 'SMTP configuration is valid!';
            } else {
                const errorData = await response.json();
                error = `Invalid SMTP configuration: ${errorData.detail}`;
            }
        } catch (e: any) {
            error = `Failed to test SMTP configuration: ${e.message}`;
        } finally {
            isTestingConfig = false;
        }
    }
</script>

<div class="space-y-4">
    <div class="flex justify-between items-center">
        <button
            on:click={() => showSmtpHelper = !showSmtpHelper}
            class="w-full px-2 py-1.5 rounded-md text-xs font-medium
                bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                transition-all flex items-center justify-center gap-2"
        >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>Auto Setup</span>
        </button>
    </div>

    {#if showSmtpHelper}
        <div class="bg-[#1a1a1a] rounded-lg p-2 border border-gray-800 text-xs" transition:slide>
            <p class="mb-2">Select your email provider:</p>
            <div class="grid grid-cols-3 gap-1">
                {#each providers as provider}
                    <button
                        class="p-1 rounded bg-[#2d2d2d] hover:bg-gray-700 transition-colors capitalize text-xs"
                        on:click={() => {
                            const help = getSmtpHelp(provider);
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
                <div class="mt-2 p-2 bg-[#2d2d2d] rounded text-[10px]">
                    <h3 class="font-medium mb-1">Setup Instructions:</h3>
                    <pre class="whitespace-pre-wrap text-gray-300">{smtpSuggestions}</pre>
                </div>
            {/if}
            <div class="flex items-center justify-between mt-2">
                <button
                    class="text-xs text-gray-400 hover:text-white transition-colors"
                    on:click={() => showSmtpHelper = false}
                >
                    Close
                </button>
                <button
                    on:click={detectSmtpSettings}
                    disabled={!smtpConfig.email || isDetectingConfig}
                    class="px-2 py-1 rounded-md text-xs font-medium
                        bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700
                        transition-all disabled:opacity-50"
                >
                    {#if isDetectingConfig}
                        <span class="flex items-center gap-1">
                            <svg class="animate-spin h-3 w-3" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                            </svg>
                            <span>Detecting...</span>
                        </span>
                    {:else}
                        Auto-detect
                    {/if}
                </button>
            </div>
        </div>
    {/if}

    <div class="space-y-2">
        <div>
            <label for="smtp-server" class="block text-xs font-medium mb-1">SMTP Server</label>
            <input
                id="smtp-server"
                type="text"
                bind:value={smtpConfig.server}
                placeholder="e.g., smtp.gmail.com"
                class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-2 py-1 text-xs
                    focus:outline-none focus:ring-1 focus:ring-gray-700"
            />
        </div>
        <div>
            <label for="smtp-port" class="block text-xs font-medium mb-1">Port</label>
            <input
                id="smtp-port"
                type="text"
                bind:value={smtpConfig.port}
                placeholder="587 or 465"
                class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-2 py-1 text-xs
                    focus:outline-none focus:ring-1 focus:ring-gray-700"
            />
        </div>
        <div>
            <label for="smtp-email" class="block text-xs font-medium mb-1">Email</label>
            <input
                id="smtp-email"
                type="email"
                bind:value={smtpConfig.email}
                placeholder="your@email.com"
                class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-2 py-1 text-xs
                    focus:outline-none focus:ring-1 focus:ring-gray-700"
            />
        </div>
        <div>
            <label for="smtp-password" class="block text-xs font-medium mb-1">Password</label>
            <input
                id="smtp-password"
                type="password"
                bind:value={smtpConfig.password}
                placeholder="SMTP Password or App Password"
                class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-2 py-1 text-xs
                    focus:outline-none focus:ring-1 focus:ring-gray-700"
            />
        </div>
        <div>
            <label for="smtp-sender" class="block text-xs font-medium mb-1">Sender Name</label>
            <input
                id="smtp-sender"
                type="text"
                bind:value={smtpConfig.name}
                placeholder="Your Name"
                class="w-full bg-[#1a1a1a] rounded-md border border-gray-800 px-2 py-1 text-xs
                    focus:outline-none focus:ring-1 focus:ring-gray-700"
            />
        </div>
        
        <button
            on:click={testSmtpConfig}
            disabled={isTestingConfig}
            class="w-full px-2 py-1.5 rounded-md text-xs font-medium
                bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                transition-all disabled:opacity-50 mt-2 flex items-center justify-center gap-2"
        >
            {#if isTestingConfig}
                <svg class="animate-spin h-3 w-3" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                <span>Testing...</span>
            {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Test Configuration</span>
            {/if}
        </button>
    </div>

    {#if message}
        <div class="bg-green-900/50 border border-green-800 text-green-100 px-2 py-1 rounded-md text-xs">
            {message}
        </div>
    {/if}

    {#if error}
        <div class="bg-red-900/50 border border-red-800 text-red-100 px-2 py-1 rounded-md text-xs">
            {error}
        </div>
    {/if}
</div> 