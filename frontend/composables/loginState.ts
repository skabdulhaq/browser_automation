
export const isUserLoggedIn = () => useState("LoggedIn", ()=> useCookie('token').value ? true:false )
export const isUserData = () => useState("isUserDataExists", ()=> false )
export const userData = () => useState("getUserData", ()=> { return {}} )
