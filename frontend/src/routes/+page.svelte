<!-- Main page with login and signup forms -->
<script lang="ts">
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    // SEO metadata
    const title = "NoobMail AI - Newsletter Management Made Simple";
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

<div>Redirecting to dashboard...</div>

<style>
    /* Add any custom styles here */
</style>
