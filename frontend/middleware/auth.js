import {
    isUserLoggedIn
} from '~/composables/loginState';
export default defineNuxtRouteMiddleware((to, from) => {
    const isLoggedIn = isUserLoggedIn()
    if (isLoggedIn.value) {
        console.log('user is logged in')
    } else {
        isLoggedIn.value=false;
        return navigateTo('/login')
    }
})