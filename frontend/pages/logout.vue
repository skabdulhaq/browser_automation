<template>
    Logout
</template>

<script setup>
function logout() {
    const token = useCookie('token');
    try {
        if (token.value) {
            token.value = null;
        }
    } catch (e) {
        console.log(e)
    }
}
onMounted(async()=>{
    logout();
    await navigateTo({ path: '/login' })
});
</script>