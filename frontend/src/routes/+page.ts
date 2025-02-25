import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const prerender = false;
export const ssr = true;

export const load: PageLoad = async ({ url }) => {
    // Only redirect if we're at the root path
    if (url.pathname === '/') {
        throw redirect(307, '/write');
    }
    return {};
}; 