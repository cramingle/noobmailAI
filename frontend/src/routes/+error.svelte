<script lang="ts">
    import { page } from '$app/stores';
</script>

<div class="flex min-h-screen items-center justify-center bg-[#1a1a1a] px-4 py-16 sm:px-6 sm:py-24 md:grid md:place-items-center lg:px-8">
    <div class="mx-auto max-w-max">
        <main class="sm:flex">
            <p class="text-4xl font-bold tracking-tight text-purple-600 sm:text-5xl">{$page.status}</p>
            <div class="sm:ml-6">
                <div class="sm:border-l sm:border-gray-700 sm:pl-6">
                    <h1 class="text-4xl font-bold tracking-tight text-white sm:text-5xl">
                        {$page.error?.message || 'Page not found'}
                    </h1>
                    <p class="mt-3 text-base text-gray-400">
                        Please check the URL in the address bar and try again.
                    </p>
                </div>
                <div class="mt-10 flex space-x-3 sm:border-l sm:border-transparent sm:pl-6">
                    <a
                        href="/"
                        class="inline-flex items-center rounded-md border border-transparent bg-purple-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
                    >
                        Go back home
                    </a>
                    <a
                        href="/write"
                        class="inline-flex items-center rounded-md border border-transparent bg-purple-100 px-4 py-2 text-sm font-medium text-purple-700 hover:bg-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
                    >
                        Go to editor
                    </a>
                </div>
            </div>
        </main>
    </div>
</div> 