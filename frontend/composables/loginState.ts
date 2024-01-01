
export const useIsUserLoggedIn = () => useState("LoggedIn", ()=> useCookie('token').value ? true:false )
export const isUserData = () => useState("isUserDataExists", ()=> false )
// export const userData = () => useState("userData", ()=>{
//     if (useCookie('token').value){
//         // fetch()
//     }
// } )
