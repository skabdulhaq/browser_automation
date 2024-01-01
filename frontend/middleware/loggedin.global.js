import {
    useIsUserLoggedIn
} from '~/composables/loginState';
export default defineNuxtRouteMiddleware((to, from) => {
    const token = useCookie('token').value
    const isLoggedIn = useIsUserLoggedIn()
    if (token) {
        isLoggedIn.value = true;
    } if(token === undefined) {
        isLoggedIn.value=false;
    }
})