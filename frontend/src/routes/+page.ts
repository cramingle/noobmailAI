import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
    // If we're already on /write, don't redirect
    if (url.pathname === '/write') {
        return {};
    }
    
    // Otherwise redirect to /write
    throw redirect(307, '/write');
}; 