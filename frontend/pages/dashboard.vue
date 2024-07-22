<template>
    <div v-if="!pageLoading" class="flex justify-center items-center gap-16 min-h-screen flex-col">
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
            <div>
                <div class="flex flex-col gap-4 mt-4 ">
                    <div>
                        <div class="label">
                            <span class="label-text">Select a image to deploy</span>
                        </div>
                        <select class="select select-secondary w-full" v-model="selectedImage">
                            <option disabled selected>Pick your image to deploy</option>
                            <option v-for="image in avaliableImages" :value="image" :key="image">
                                {{ toTitleCase(image.split("/")[1].split(":")[0]) }}
                            </option>
                        </select>
                    </div>
                    <div v-if="selectedImage !== 'Pick your image to deploy'">
                        <div class="label">
                            <span class="label-text">Password for instance</span>
                        </div>
                        <input type="password" v-model="password" placeholder="Password"
                            class="input input-bordered input-secondary w-full" />
                        <div class="label">
                            <span class="label-text-alt" v-if="password.length < 6">Password should be greater than 6
                                characters</span>
                        </div>
                    </div>
                    <button v-if="!loading && password.length >= 6" class="btn btn-secondary" @click="deploy">
                        Launch
                    </button>
                    <button v-if="loading" class="btn btn-secondary">
                        <span class="loading loading-spinner text-primary"></span>
                    </button>
                    <div role="alert" v-if="showError" class="alert alert-error">
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>{{ errorText }}</span>
                    </div>
                    <div v-if="successful" role="alert" class="alert alert-success">
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>Instance Deployed Username Is "kasm_user"</span>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="userContainers.length" class="overflow-x-auto table-sm">
            <table class="table">
                <thead>
                    <tr>
                        <th>Container Name</th>
                        <th>Image</th>
                        <th>Time Left</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="containerData in userContainers" class="hover">
                        <td>
                            <a :href=containerData.service_url target="_blank" class="link">
                                {{ containerData.container_name }}
                            </a>
                        </td>
                        <td>{{ toTitleCase(containerData.container_image.split("/")[1].split(":")[0]) }}</td>
                        <td>
                            <Counter :hours=convertISOTimeToLocalDate(containerData.down_time).hours
                                :minutes=convertISOTimeToLocalDate(containerData.down_time).minutes
                                :seconds=convertISOTimeToLocalDate(containerData.down_time).seconds />
                        </td>
                        <td>
                            <button v-if="!deleteLoading[containerData.container_name]" class="btn btn-secondary"
                                @click="delete_container(containerData.container_name)">
                                DELETE
                            </button>
                            <button :key="containerData.container_name" v-else class="btn btn-secondary"
                                @click="delete_container(containerData.container_name)">
                                <span :key="containerData.container_name"
                                    class="loading loading-spinner text-primary"></span>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup>
const userData = ref({});
const userContainers = ref([]);
const avaliableImages = ref();
const noContainers = ref(true);
const password = ref("");
const selectedImage = ref("Pick your image to deploy");
const containerData = ref();
const deletedUserContainers = ref();
const loading = ref(false);
const deleteLoading = ref({});
const errorText = ref("");
const showError = ref(false);
const pageLoading = ref(false);
const successful = ref(false);


function toTitleCase(str) {
    return str.replace(
        /\w\S*/g,
        (txt) => {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    );
}

function convertISOTimeToLocalDate(utcISOTimeString) {
    const utcDate = new Date(utcISOTimeString);
    const userTimezoneOffset = new Date().getTimezoneOffset();
    const localDate = new Date(utcDate.getTime() - userTimezoneOffset * 60000);
    const present_time = new Date();
    const timeDifference = localDate.getTime() - present_time
    if (timeDifference > 0) {
        const hours = Math.floor(timeDifference / (1000 * 60 * 60));
        const minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);
        // console.log({ hours, minutes, seconds });
        return { hours, minutes, seconds };
    }
}

function toggleMessage(boolRef, messageRef, message) {
    boolRef.value = true;
    if (message) {
        messageRef.value = message;
    }
    setTimeout(
        () => {
            boolRef.value = false;
        }, 5000
    )
}

async function sendRequest(url, method, store, data, bodyMsg) {
    try {
        const cookie = useCookie('token').value;
        let req_header = {}
        req_header = {
            'Accept': 'application/json',
            'Authorization': `Bearer ${cookie}`,
            'Content-Type': 'application/json'
        }
        if (data) {
            const response = await fetch(url, {
                method: method,
                headers: req_header,
                body: JSON.stringify(bodyMsg)
            });
            const resp = await response.json()
            if (!response.ok) {
                console.log(resp.detail);
                toggleMessage(showError, errorText, resp.detail);
            }
            else {
                // console.log(resp)
                store.value = resp;
                if (method === "POST") {
                    // toggleMessage(successful, null, null)
                    successful.value = true
                    setTimeout(
                        () => {
                            successful.value = false;
                        }, 10000
                    )
                }
            }
        }
        else {
            const response = await fetch(url, {
                method: method,
                headers: req_header,
            });
            if (response.status === 401) {
                await navigateTo('/login')
            }
            else if (!response.ok) {
                toggleMessage(showError, errorText, response.detail);
            }
            else {
                const data = await response.json();
                store.value = data;
            }
        }
    }
    catch (e) {
        console.log(e);
    }
}

async function getUserContainers() {
    await sendRequest("http://cloudos.us.to/api/user/containers", "GET", userContainers, false, {});
    for (let i = 0; i < userContainers.value.length; i++) {
        deleteLoading[userContainers.value[i].container_name] = false
    }
}

async function deploy() {
    loading.value = true;
    await sendRequest("http://cloudos.us.to/api/user/container", "POST", containerData, true, {
        container_image: selectedImage.value,
        password: password.value,
    });
    // console.log(containerData.value)
    password.value = "";
    selectedImage.value = "Pick your image to deploy";
    await getUserContainers();
    loading.value = false;
}

async function delete_container(containerName) {
    deleteLoading.value[containerName] = true
    // console.log(containerName, "DELETING")
    await sendRequest(`http://cloudos.us.to/api/user/container?container_name=${containerName}`, "DELETE", deletedUserContainers, false, {});
    await getUserContainers();
    deleteLoading.value[containerName] = false
}
pageLoading.value = true;
if (userContainers.value.length > 0) {
    noContainers.value = false;
}
await sendRequest("http://cloudos.us.to/api/user", "GET", userData, false, {});
await getUserContainers();
await sendRequest("http://cloudos.us.to/api/list/images", "GET", avaliableImages, false, {});
pageLoading.value = false;
definePageMeta({
    middleware: 'auth'
});

useHead({
  title:"Cloud OS: Launch your image",
});
</script>