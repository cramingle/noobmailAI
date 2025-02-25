<!-- OnboardingGuide.svelte -->
<script lang="ts">
    import { slide } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher<{
        stepChange: number;
        complete: void;
    }>();
    export let currentStep = 1;

    interface Feature {
        icon: string;
        title: string;
        description: string;
    }

    interface Provider {
        name: string;
        icon: string;
        setup: string;
    }

    interface Instruction {
        step: string;
        action: string;
        detail: string;
    }

    interface Step {
        title: string;
        description: string;
        features?: Feature[];
        steps?: string[];
        instructions?: Instruction[];
        providers?: Provider[];
        tip?: string;
        image: string;
    }

    const steps: Step[] = [
        {
            title: "Welcome to NoobMail AI!",
            description: "Your AI-powered newsletter assistant",
            features: [
                {
                    icon: "",
                    title: "AI Writing Assistant",
                    description: "Just describe what you want, and AI creates it"
                },
                {
                    icon: "",
                    title: "Example Newsletters",
                    description: "Get inspired by pre-made examples"
                },
                {
                    icon: "",
                    title: "Quick & Easy",
                    description: "Create newsletters in minutes, not hours"
                }
            ],
            image: "/onboarding/welcome.png"
        },
        {
            title: "Make It Personal",
            description: "Help AI understand your style",
            steps: [
                "Upload your brand guidelines",
                "Add previous newsletters",
                "Include any reference materials",
                "AI uses these to match your style"
            ],
            tip: "💡 The more context you provide, the better the results!",
            image: "/onboarding/context.png"
        },
        {
            title: "Manage Your Audience",
            description: "Keep your contacts organized",
            instructions: [
                {
                    step: "1",
                    action: "Click Settings",
                    detail: "Find it in the top-right corner"
                },
                {
                    step: "2",
                    action: "Go to Recipients tab",
                    detail: "Create groups for different audiences"
                },
                {
                    step: "3",
                    action: "Add your contacts",
                    detail: "Import or add them manually"
                }
            ],
            image: "/onboarding/recipients.png"
        },
        {
            title: "Ready to Send!",
            description: "Final setup for your email",
            providers: [
                {
                    name: "Gmail",
                    icon: "",
                    setup: "Use App Password if 2FA enabled"
                },
                {
                    name: "Outlook",
                    icon: "",
                    setup: "Regular password or App Password"
                },
                {
                    name: "Custom SMTP",
                    icon: "",
                    setup: "Your own email server"
                }
            ],
            tip: "Need help? Click the AI Setup Helper in SMTP settings!",
            image: "/onboarding/smtp.png"
        }
    ];

    function handleNext() {
        if (currentStep < steps.length) {
            dispatch('stepChange', currentStep + 1);
        } else {
            dispatch('complete');
        }
    }

    function handleSkip() {
        dispatch('complete');
    }
</script>

<div class="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4" transition:slide>
    <div class="bg-gradient-to-br from-[#2d2d2d] to-[#1a1a1a] rounded-xl max-w-4xl w-full mx-auto overflow-hidden shadow-2xl">
        <!-- Progress Dots -->
        <div class="flex justify-center gap-2 pt-6">
            {#each steps as _, i}
                <div 
                    class="w-2 h-2 rounded-full transition-all duration-300 {i + 1 <= currentStep ? 'bg-purple-500' : 'bg-gray-600'}"
                ></div>
            {/each}
        </div>

        <!-- Content -->
        <div class="p-8">
            {#if currentStep === 1}
                <div class="space-y-8">
                    <div class="text-center">
                        <h2 class="text-3xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                            {steps[0].title}
                        </h2>
                        <p class="text-gray-400 mt-2">{steps[0].description}</p>
                    </div>
                    
                    {#if steps[0].features}
                        <div class="grid grid-cols-3 gap-4">
                            {#each steps[0].features as feature}
                                <div class="bg-[#2d2d2d]/50 rounded-lg p-4 text-center hover:bg-[#2d2d2d] transition-all">
                                    <div class="text-2xl mb-2">{feature.icon}</div>
                                    <h3 class="font-medium text-purple-400 mb-1">{feature.title}</h3>
                                    <p class="text-sm text-gray-400">{feature.description}</p>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            {:else if currentStep === 2}
                <div class="grid grid-cols-2 gap-8 items-center">
                    <div class="space-y-6">
                        <div>
                            <h2 class="text-2xl font-bold text-white mb-2">{steps[1].title}</h2>
                            <p class="text-gray-400">{steps[1].description}</p>
                        </div>
                        
                        {#if steps[1].steps}
                            <div class="space-y-3">
                                {#each steps[1].steps as step}
                                    <div class="flex items-center space-x-3 bg-[#2d2d2d]/50 p-3 rounded-lg">
                                        <div class="text-purple-400">✓</div>
                                        <div class="text-gray-300">{step}</div>
                                    </div>
                                {/each}
                            </div>
                        {/if}

                        {#if steps[1].tip}
                            <div class="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4 text-purple-300">
                                {steps[1].tip}
                            </div>
                        {/if}
                    </div>
                    <div class="flex items-center justify-center">
                        <div class="text-6xl">🎯</div>
                    </div>
                </div>
            {:else if currentStep === 3}
                <div class="grid grid-cols-2 gap-8 items-center">
                    <div class="space-y-6">
                        <div>
                            <h2 class="text-2xl font-bold text-white mb-2">{steps[2].title}</h2>
                            <p class="text-gray-400">{steps[2].description}</p>
                        </div>
                        
                        {#if steps[2].instructions}
                            <div class="space-y-4">
                                {#each steps[2].instructions as instruction}
                                    <div class="flex items-start space-x-4 bg-[#2d2d2d]/50 p-4 rounded-lg">
                                        <div class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-medium">
                                            {instruction.step}
                                        </div>
                                        <div>
                                            <div class="font-medium text-white">{instruction.action}</div>
                                            <div class="text-sm text-gray-400">{instruction.detail}</div>
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        {/if}
                    </div>
                    <div class="flex items-center justify-center">
                        <div class="text-6xl">👥</div>
                    </div>
                </div>
            {:else if currentStep === 4}
                <div class="grid grid-cols-2 gap-8 items-center">
                    <div class="space-y-6">
                        <div>
                            <h2 class="text-2xl font-bold text-white mb-2">{steps[3].title}</h2>
                            <p class="text-gray-400">{steps[3].description}</p>
                        </div>
                        
                        {#if steps[3].providers}
                            <div class="grid grid-cols-2 gap-4">
                                {#each steps[3].providers as provider}
                                    <div class="bg-[#2d2d2d]/50 p-4 rounded-lg">
                                        <div class="flex items-center space-x-2 mb-2">
                                            <span class="text-xl">{provider.icon}</span>
                                            <span class="font-medium text-white">{provider.name}</span>
                                        </div>
                                        <p class="text-sm text-gray-400">{provider.setup}</p>
                                    </div>
                                {/each}
                            </div>
                        {/if}

                        {#if steps[3].tip}
                            <div class="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 text-blue-300">
                                {steps[3].tip}
                            </div>
                        {/if}
                    </div>
                    <div class="flex items-center justify-center">
                        <div class="text-6xl">🚀</div>
                    </div>
                </div>
            {/if}
        </div>

        <!-- Navigation -->
        <div class="p-6 bg-[#2d2d2d]/50 flex justify-between items-center">
            <button
                class="text-gray-400 hover:text-white transition-colors text-sm flex items-center space-x-2"
                on:click={handleSkip}
            >
                <span>Skip Tour</span>
            </button>
            
            <div class="flex items-center space-x-4">
                <div class="text-sm text-gray-400">
                    Step {currentStep} of {steps.length}
                </div>
                <button
                    class="px-6 py-2 rounded-md text-sm font-medium
                        bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500
                        transition-all flex items-center space-x-2"
                    on:click={handleNext}
                >
                    <span>{currentStep === steps.length ? 'Get Started' : 'Next'}</span>
                    <span>→</span>
                </button>
            </div>
        </div>
    </div>
</div>

<style>
    :global(body) {
        overflow: hidden;
    }
</style> 