<template>
    <div class="hero min-h-screen" style="background-image: url('/banner.webp');">
        <div class="hero-overlay bg-opacity-60"></div>
        <div class="hero-content text-center text-neutral-content">
            <div class="max-w-md">
                <h1 class="mb-5 text-5xl font-bold">Cloud OS</h1>
                <p class="mb-5">Effortlessly launch Alpine OS or any web browser instances for secure, disposable environments on Cloud OS, redefining your digital experience.</p>
                <NuxtLink to="/register">
                    <button class="btn btn-primary text-slate-200">Get Started</button>
                </NuxtLink>
            </div>
        </div>
    </div>
</template>

<script setup>

useHead({
  title:"Cloud OS: Effortlessly launch Alpine OS or any web browser instances for secure, disposable environments on Cloud.",
});
</script>