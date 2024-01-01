<template>
    <div class="flex min-h-screen flex-col justify-center bg-base-200">
        <div class="flex gap-5 flex-col items-center mr-20 ml-20 mt-10">
            <div class="text-center">
                <h1 class="text-5xl font-bold">Register now!</h1>
            </div>

            <div class="card shrink-0 w-full max-w-sm shadow-2xl bg-base-100">
                <form onsubmit="return false" class="card-body">
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Username</span>
                        </label>
                        <input type="text" v-model="formData.username" placeholder="username" class="input input-bordered"
                            required />
                    </div>
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Full Name</span>
                        </label>
                        <input type="text" v-model="formData.full_name" placeholder="full name" class="input input-bordered"
                            required />
                    </div>
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Email</span>
                        </label>
                        <input type="email" v-model="formData.email" placeholder="email" class="input input-bordered"
                            required />
                    </div>
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Password</span>
                        </label>
                        <input type="password" v-model="formData.password" placeholder="password"
                            class="input input-bordered" required />
                        <div class="label">
                            <span class="label-text-alt">Click here to <NuxtLink class="link" to="/login">Login</NuxtLink></span>
                        </div>
                    </div>
                    <div role="alert" v-if="short_password" class="alert alert-error">
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>Password is short.</span>
                    </div>
                    <div role="alert" v-if="RegisterSuccessfull" class="alert alert-success">
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>Successfully registered and verification email is sent to your inbox</span>
                    </div>
                    <div role="alert" v-if="error" class="alert alert-error">
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>{{ error_text }}</span>
                    </div>
                    <div role="alert" v-if="passwordsNotMatch" class="alert alert-error">
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>Password does not match.</span>
                    </div>

                    <div class="form-control ">
                        <button @click="register" class="btn btn-primary">Register</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    <Footer></Footer>
</template>

<script setup>
const passwordsNotMatch = ref(false);
const short_password = ref(false);
const RegisterSuccessfull = ref(false);
const error = ref(false);
const error_text = ref("");
const successResult = ref("");
const formData = ref({
    username: "",
    email: "",
    full_name: "",
    password: "",
});
function verifyPassword() {
    if (formData.value.password != "") {
        if (formData.value.password.length < 8) {
            short_password.value = true
            setTimeout(
                async function () {
                    short_password.value = false
                }, 1000
            )
        } else {
            short_password.value = false;
            return true;
        }
    }
    else {
        return false;
    }
}

async function register() {
    // console.log(formData.value);
    const validPassword = verifyPassword();
    if (validPassword) {
        const response = await fetch('http://cloudos.us.to/api/register', {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData.value),
        });
        const result = await response.json();
        if (!response.ok) {
            error_text.value = await result.detail;
            error.value = true;
            console.log(error.value);
            setTimeout(
                function () {
                    error.value = false;
                    error_text.value = "";
                }, 2000
            )
        }
        else {
            RegisterSuccessfull.value = true;
            successResult.value = await result.detail;
        }
    }

}
</script>