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
            <!-- {{ avaliableImages }} -->
            <div class="flex gap-4">
                <select class="select select-secondary w-full max-w-xs" v-model="selectedImage">
                    <option disabled selected>Pick your image to deploy</option>
                    <option 
                    v-for="image in avaliableImages" 
                    :value="image" 
                    :key="image" >
                        {{toTitleCase(image.split("/")[1].split(":")[0])}}
                    </option>
                </select>
                <button class="btn btn-secondary" @click="deploy">Launch</button>
            </div>
        </div>
    </div>
</template>
<script setup>
function toTitleCase(str) {
  return str.replace(
    /\w\S*/g,
    function(txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    }
  );
}

const userData = ref({});
const userContainers = ref();
const avaliableImages = ref();
const noContainers = ref(true);
const selectedImage = ref("");
async function sendRequest(url, method, store) {
    try {
        const cookie = useCookie('token').value;
        console.log(cookie);
        let req_header = {}
            req_header = {
                'Accept': 'application/json',
                'Authorization': `Bearer ${cookie}`,
                'Content-Type': 'application/json'
            }
        const response = await fetch(url, {
            method: method,
            headers: req_header,
        });
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
await sendRequest("http://cloudos.us.to/api/list/images", "GET", avaliableImages);
if (userContainers.value.length > 0) {
    noContainers.value = false;
}

function deploy(){
    // console.log(selectedImage.value)
    
}
definePageMeta({
    middleware: 'auth'
});
</script>