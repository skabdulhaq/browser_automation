<template>
    <div class="flex min-h-screen flex-col justify-center bg-base-200">
        <div class="flex gap-5 flex-col items-center mr-20 ml-20 mt-10">
            <div class="text-center">
                <h1 class="text-5xl font-bold">Login</h1>
            </div>

            <div class="card shrink-0 w-full max-w-sm shadow-2xl bg-base-100">
                <form onsubmit="return false" class="card-body">
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Email or Username</span>
                        </label>
                        <input type="text" v-model="loginData.identifier" placeholder="username"
                            class="input input-bordered" required />
                    </div>
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Password</span>
                        </label>
                        <input type="password" v-model="loginData.password" placeholder="password"
                            class="input input-bordered" required />
                    </div>
                    <div role="alert" v-if="error" class="alert alert-error">
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>{{ error_text }}</span>
                    </div>
                    <div class="form-control ">
                        <button @click="login" class="btn btn-primary">
                            {{ !loading ? "Login" : "" }}
                            <span v-if="loading" class="loading loading-spinner text-accent"></span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    <Footer></Footer>
</template>
<script setup>
import { isUserLoggedIn, userData, isUserData } from '~/composables/loginState';

const error = ref(false);
const error_text = ref("");
const loginData = ref({
    identifier: "",
    password: ""
})
const loading = ref(false);
const dataUser = userData();
const login = async () => {
    loading.value = true
    const url = "http://cloudos.us.to/api/token"
    const data = {
        grant_type: "password",
        username: loginData.value.identifier,
        password: loginData.value.password
    }
    const headers = {
        accept: 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    };
    const doseUserExisits = isUserData();
    console.log(doseUserExisits);
    const userLoggedIn = isUserLoggedIn();
    const body = new URLSearchParams(data);
    try {
        const response = await fetch(url, { method: 'POST', headers, body });
        const data = await response.json();

        if (!response.ok) {
            error.value = true;
            error_text.value = data.detail
        }
        if (data.token_type == "bearer") {
            const token = useCookie('token', { maxAge: 86400 })
            doseUserExisits.value = true;
            token.value = data.access_token;
            try {
                console.log(useCookie('token').value);
                const response = await fetch("http://cloudos.us.to/api/user", {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'Authorization': `Bearer ${data.access_token}`,
                    },
                });
                const result = await response.json();
                if (!response.ok) {
                    error.value = result.detail
                    throw new Error('Network response was not ok');
                }
                else {
                    dataUser.value = result
                    const userLoggedIn = isUserLoggedIn();
                    userLoggedIn.value = true;
                    await navigateTo('/dashboard')
                }
                if (route.query.to) {
                  await navigateTo(route.query.to);
                }
                else {
                }
            } catch (error) {
                userLoggedIn.value = false;
                console.error('Error fetching data:', error.message);
            }
        }
    }
    catch (e) {
        console.error('Error fetching data:', e.message);
    }
    loading.value = false;
}
</script>
