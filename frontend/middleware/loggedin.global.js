import {
    isUserLoggedIn
} from '~/composables/loginState';
export default defineNuxtRouteMiddleware((to, from) => {
    const token = useCookie('token').value
    const isLoggedIn = isUserLoggedIn()
    if (token) {
        isLoggedIn.value = true;
    } if(token === undefined) {
        isLoggedIn.value=false;
    }
})