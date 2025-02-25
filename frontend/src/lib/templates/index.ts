import type { Template } from '$lib/types';

export const defaultTemplates: Template[] = [
    {
        id: 'welcome',
        name: 'Welcome Email',
        subject: 'Welcome to Our Newsletter!',
        content: `
            <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
                <h1 style="color: #333;">Welcome to Our Newsletter!</h1>
                <p>Thank you for subscribing to our newsletter. We're excited to have you on board!</p>
                <p>Stay tuned for updates, news, and exciting content.</p>
            </div>
        `
    },
    {
        id: 'update',
        name: 'Monthly Update',
        subject: 'Monthly Newsletter Update',
        content: `
            <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
                <h1 style="color: #333;">Monthly Update</h1>
                <h2>What's New</h2>
                <p>Here are the latest updates and news from our team.</p>
                <h2>Featured Content</h2>
                <p>Check out our featured content for this month.</p>
            </div>
        `
    }
]; 