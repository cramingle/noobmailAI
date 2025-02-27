<!-- Main page with login and signup forms -->
<script lang="ts">
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import OnboardingGuide from '../components/OnboardingGuide.svelte';
    import ChatPanel from '../components/chat/ChatPanel.svelte';
    import { writable } from 'svelte/store';

    // SEO metadata
    const title = "NoobMail AI - Send email with style";
    const description = "Create and send beautiful newsletters without any technical knowledge. AI-powered newsletter editor for beginners.";
    
    // JSON-LD structured data
    const structuredData = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "NoobMail AI",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        },
        "description": "AI-powered newsletter editor for beginners. Create and send beautiful newsletters without any technical knowledge.",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.8",
            "ratingCount": "127"
        }
    };

    // Add email type state
    let emailType: "professional" | "career" = "professional";
    
    // Add email type toggle function
    function toggleEmailType() {
        emailType = emailType === "professional" ? "career" : "professional";
    }

    onMount(() => {
        goto('/write');
        
        // Update document title and meta description
        document.title = title;
        
        // Add meta description
        const metaDescription = document.createElement('meta');
        metaDescription.name = 'description';
        metaDescription.content = description;
        document.head.appendChild(metaDescription);
        
        // Add JSON-LD structured data
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.textContent = JSON.stringify(structuredData);
        document.head.appendChild(script);
    });
</script>

<div class="flex h-screen bg-[#1a1a1a] text-white">
    <!-- Add email type toggle button -->
    <div class="absolute top-4 right-4 z-50">
        <button 
            on:click={toggleEmailType}
            class="px-4 py-2 rounded-md text-sm font-medium bg-purple-600 hover:bg-purple-500 transition-colors"
        >
            Switch to {emailType === "professional" ? "Career & Business" : "Professional & Academic"}
        </button>
    </div>

    <!-- Pass email type to components -->
    <OnboardingGuide {emailType} />
    <ChatPanel {emailType} />
</div>

<style>
    /* Add any custom styles here */
</style>
