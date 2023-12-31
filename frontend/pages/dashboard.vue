<template>
    <div class="stats shadow">
        <div class="stat">
            <div class="stat-title">Launch</div>
            <div class="stat-value">{{userContainers.value}}</div>
            <!-- <div class="stat-desc"></div> -->
        </div>
    </div>
</template>
<script setup>

const userData = ref({});
const userContainers = ref({});

async function sendRequest(url, method, store) {
    try {
        const cookie = useCookie('token').value;
        console.log(cookie);
        const auth_header = {
            'Accept': 'application/json',
            'Authorization': `Bearer ${cookie}`,
            'Content-Type': 'application/json'
        }
        // console.log(auth_header)
        const response = await fetch(url, {
            method: method,
            headers: auth_header,
        });
        // console.log(response.status);
        if (response.status == 401) {
            return navigateTo('/login')
        }
        else if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        else {
            const data = await response.json();
            store.value = data;
            // console.log(store.value);
        }
    }
    catch (e) {
        console.log(e);
    }
}

await sendRequest("http://cloudos.us.to/api/user", "GET", userData);
await sendRequest("http://cloudos.us.to/api/user/containers", "GET", userContainers);
console.log(userData.value, "userdata");

definePageMeta({
    middleware: 'auth'
});
</script>