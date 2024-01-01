<template>
    <div class="navbar absolute bg-transprent top-0 z-50">
        <div class="navbar-start">
            <div class="dropdown">
                <div tabindex="0" role="button" class="btn btn-ghost md:hidden ">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
                    </svg>
                </div>
                
                <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
                    <li><a>Login</a></li>
                    <li><a>Register</a></li>
                </ul>
            </div>
            <a class="btn btn-ghost text-xl">
                <NuxtLink to="/">Cloud OS</NuxtLink>   
            </a>
        </div>
        <div class="navbar-end hidden md:flex">
            <div v-if="!userLogin" class="menu menu-horizontal px-1">
                <NuxtLink to="/login">
                    <span class="btn btn-secondary mr-4  ">Login</span>
                </NuxtLink>
                <NuxtLink to="/register">
                    <span class="btn btn-accent ">Register</span>
                </NuxtLink>
            </div>
            <div v-else class="menu menu-horizontal px-1">
                <NuxtLink to="/dashboard">
                    <span class="btn btn-accent mr-4">Dashboard</span>
                </NuxtLink>
                <NuxtLink to="/logout">
                    <span class="btn btn-secondary">Logout</span>
                </NuxtLink>
            </div>
        </div>
</div>
</template>

<script setup>
const userLogin = useIsUserLoggedIn();
</script>