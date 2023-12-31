<template>
    <div class="flex justify-center min-h-screen">
        <div class="flex-col flex justify-center">
            <div class="stats shadow">
                <div class="stat place-items-center">
                    <div class="stat-title">Active Containers</div>
                    <div class="stat-value text-secondary">{{ userContainers.length }}</div>
                </div>
                <div class="stat place-items-center">
                    <div class="stat-title">Maximum Containers</div>
                    <div class="stat-value">{{ userData.max_containers }}</div>
                </div>
            </div>
            <select class="select select-secondary w-full max-w-xs">
                <option disabled selected>Pick your favorite language</option>
                <option>Java</option>
                <option>Go</option>
                <option>C</option>
                <option>C#</option>
                <option>C++</option>
                <option>Rust</option>
                <option>JavaScript</option>
                <option>Python</option>
            </select>
        </div>
    </div>
</template>
<script setup>

const userData = ref({});
const userContainers = ref();
const noContainers = ref(true);

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
console.log(userContainers.value.length)
if (userContainers.value.length > 0) {
    noContainers.value = false;
}
definePageMeta({
    middleware: 'auth'
});
</script>