<!-- OnboardingGuide.svelte -->
<script lang="ts">
    import { slide } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher<{
        stepChange: number;
        complete: void;
        useTemplate: string;
    }>();
    export let currentStep = 1;

    interface Feature {
        title: string;
        description: string;
    }

    interface Provider {
        name: string;
        setup: string;
    }

    interface Instruction {
        step: string;
        action: string;
        detail: string;
    }

    interface Template {
        title: string;
        description: string;
        prompt: string;
    }

    interface Step {
        title: string;
        description: string;
        features?: Feature[];
        steps?: string[];
        instructions?: Instruction[];
        providers?: Provider[];
        templates?: Template[];
        tip?: string;
    }

    const steps: Step[] = [
        {
            title: "Welcome to NoobMail AI!",
            description: "Your AI-powered newsletter assistant",
            features: [
                {
                    title: "AI Writing Assistant",
                    description: "Just describe what you want, and AI creates it"
                },
                {
                    title: "Example Newsletters",
                    description: "Get inspired by pre-made examples"
                },
                {
                    title: "Quick & Easy",
                    description: "Create newsletters in minutes, not hours"
                }
            ],
            templates: [
                {
                    title: "Welcome Email",
                    description: "Perfect for new subscribers",
                    prompt: "Create a welcome newsletter with a modern design"
                },
                {
                    title: "Product Announcement",
                    description: "Showcase your latest offerings",
                    prompt: "Generate a product announcement with images and CTAs"
                },
                {
                    title: "Monthly Update",
                    description: "Keep your audience informed",
                    prompt: "Make a monthly update newsletter with sections"
                }
            ]
        },
        {
            title: "Using Context Files",
            description: "Make your newsletters truly yours",
            steps: [
                "Upload brand guidelines or style documents",
                "Add previous newsletters as examples",
                "Reference files with @filename in your prompts",
                "AI adapts to your style and content"
            ],
            tip: "💡 Type @filename in your message to reference a specific context file!",
            instructions: [
                {
                    step: "1",
                    action: "Add files to Context Library",
                    detail: "Click '+ Add Context' in the right panel"
                },
                {
                    step: "2",
                    action: "Reference in your prompt",
                    detail: "Type @filename when asking the AI for help"
                },
                {
                    step: "3",
                    action: "See highlighted references",
                    detail: "Context files appear in purple when mentioned"
                }
            ]
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
            ]
        },
        {
            title: "Ready to Send!",
            description: "Final setup for your email",
            providers: [
                {
                    name: "Gmail",
                    setup: "Use App Password if 2FA enabled"
                },
                {
                    name: "Outlook",
                    setup: "Regular password or App Password"
                },
                {
                    name: "Custom SMTP",
                    setup: "Your own email server"
                }
            ],
            tip: "Need help? Click the AI Setup Helper in SMTP settings!"
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
    
    function useTemplate(prompt: string) {
        // Close the onboarding guide and set the prompt
        dispatch('complete');
        dispatch('useTemplate', prompt);
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
                                    <h3 class="font-medium text-purple-400 mb-1">{feature.title}</h3>
                                    <p class="text-sm text-gray-400">{feature.description}</p>
                                </div>
                            {/each}
                        </div>
                    {/if}
                    
                    {#if steps[0].templates}
                        <div>
                            <h3 class="text-xl font-medium text-white mb-4 text-center">Try these templates</h3>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {#each steps[0].templates as template}
                                    <button 
                                        class="bg-[#2d2d2d]/50 rounded-lg p-4 text-left hover:bg-[#2d2d2d] transition-all border border-transparent hover:border-purple-500/30"
                                        on:click={() => useTemplate(template.prompt)}
                                    >
                                        <h4 class="font-medium text-purple-400 mb-1">{template.title}</h4>
                                        <p class="text-sm text-gray-400 mb-3">{template.description}</p>
                                        <div class="text-xs bg-[#1a1a1a] p-2 rounded text-gray-300">"{template.prompt}"</div>
                                    </button>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>
            {:else if currentStep === 2}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
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
                    
                    <div class="space-y-4">
                        {#if steps[1].instructions}
                            <div class="space-y-4">
                                {#each steps[1].instructions as instruction}
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
                        
                        <!-- Example of @filename usage -->
                        <div class="mt-4 bg-[#1a1a1a] rounded-lg p-4">
                            <div class="text-sm text-gray-400 mb-2">Example prompt with context:</div>
                            <div class="bg-[#2d2d2d] p-3 rounded text-gray-300 text-sm">
                                "Create a newsletter that matches the style in <span class="text-purple-400 font-semibold">@brand-guide.pdf</span> and includes information about our new product launch"
                            </div>
                        </div>
                    </div>
                </div>
            {:else if currentStep === 3}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
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
                    <div class="bg-[#1a1a1a] rounded-lg p-6">
                        <div class="text-center mb-4">
                            <div class="text-4xl mb-2">👥</div>
                            <div class="text-sm text-gray-400">Organize your contacts into groups for targeted sending</div>
                        </div>
                        <div class="bg-[#2d2d2d] rounded p-3 text-sm">
                            <div class="font-medium text-white mb-1">Example Groups</div>
                            <ul class="text-gray-400 space-y-1">
                                <li>• All Subscribers</li>
                                <li>• Premium Members</li>
                                <li>• New Customers</li>
                            </ul>
                        </div>
                    </div>
                </div>
            {:else if currentStep === 4}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                    <div class="space-y-6">
                        <div>
                            <h2 class="text-2xl font-bold text-white mb-2">{steps[3].title}</h2>
                            <p class="text-gray-400">{steps[3].description}</p>
                        </div>
                        
                        {#if steps[3].providers}
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {#each steps[3].providers as provider}
                                    <div class="bg-[#2d2d2d]/50 p-4 rounded-lg">
                                        <div class="font-medium text-white mb-2">{provider.name}</div>
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
                    <div class="bg-[#1a1a1a] rounded-lg p-6">
                        <div class="text-center mb-4">
                            <div class="text-4xl mb-2">🚀</div>
                            <div class="text-sm text-gray-400">Ready to send your beautiful newsletter!</div>
                        </div>
                        <div class="bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg p-3 text-center text-white font-medium">
                            Send Newsletter
                        </div>
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