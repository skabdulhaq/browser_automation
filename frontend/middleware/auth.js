import {
    useIsUserLoggedIn
} from '~/composables/loginState';
export default defineNuxtRouteMiddleware((to, from) => {
    const isLoggedIn = useIsUserLoggedIn()
    if (isLoggedIn.value) {
        // console.log('user is logged in')
    } else {
        isLoggedIn.value=false;
        return navigateTo('/login')
    }
})