<template>
    <div class="flex justify-center min-h-screen flex-col">
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
                    <button v-if="password.length >= 6" class="btn btn-secondary" @click="deploy">
                        <span v-if="loading" class="loading loading-spinner text-primary"></span>
                        <span v-else>Launch</span>
                    </button>
                </div>
            </div>
        </div>
        <div class="overflow-x-auto table-sm">
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
                        <td>{{ containerData.down_time }}</td>
                        <td>
                            <button class="btn btn-secondary" @click="delete_container(containerData.container_name)">
                                DELETE
                            </button>
                         </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup>
function toTitleCase(str) {

    return str.replace(
        /\w\S*/g,
        function (txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    );
}

const userData = ref({});
const userContainers = ref([]);
const avaliableImages = ref();
const noContainers = ref(true);
const errorVal = ref("");
const password = ref("");
const selectedImage = ref("Pick your image to deploy");
const containerData = ref();
const deletedUserContainers = ref();
const loading = ref(false);
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
            if (!resp.ok) {
                errorVal.value = resp.detail;
            }
            else {
                store.value = query;
            }
        }
        else {
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
    }
    catch (e) {
        console.log(e);
    }
}
async function getUserContainers(){
    await sendRequest("http://cloudos.us.to/api/user/containers", "GET", userContainers, false, {});
}
await sendRequest("http://cloudos.us.to/api/user", "GET", userData, false, {});
await getUserContainers();
await sendRequest("http://cloudos.us.to/api/list/images", "GET", avaliableImages, false, {});
if (userContainers.value.length > 0) {
    noContainers.value = false;
}

async function deploy() {
    loading.value = true;
    await sendRequest("http://cloudos.us.to/api/user/container", "POST", containerData, true, {
        container_image: selectedImage.value,
        password: password.value,
    });
    console.log(containerData.value)
    password.value = "";
    selectedImage.value = "Pick your image to deploy";
    await getUserContainers();
    loading.value = false;
}
async function delete_container(containerName){
    deleteLoading.value = true
    console.log(containerName, "DELETING")
    await sendRequest(`http://cloudos.us.to/api/user/containers?container_name=${containerName}`, "DELETE", deletedUserContainers, false, {});
    await getUserContainers();
    deleteLoading.value = false
}
definePageMeta({
    middleware: 'auth'
});
</script>