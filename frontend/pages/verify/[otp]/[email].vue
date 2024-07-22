<template>
    <div class="flex flex-col items-center align-center justify-center min-h-screen">
        <span class="text-2xl loading loading-spinner text-primary"></span>
        <div class="text-2xl">Successfully Verified redirecting to login page...</div>
    </div>
</template>
<script setup>
const route = useRoute();
const verificationCompleted = ref(false);
const failed = ref(false);
const path = route.path;
const message = ref('');
const api = "/api";
try {
    const response = await fetch(api + path, { method: 'GET', headers: { accept: 'application/json' } });
    const data = await response.json();
    if (!response.ok) {
        failed.value = true;
        message.value = data.detail
        setTimeout(
            async () =>await navigateTo({ path: '/register' })
            , 3000
        )
    }
    else {
        verificationCompleted.value = true;
        failed.value = false;
        setTimeout(
            async () => await navigateTo({ path: '/login' })
            , 3000
        )
    }
} catch (error) {
    console.error('Error fetching data:', error);
}
</script>
  