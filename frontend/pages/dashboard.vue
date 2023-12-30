<template>
    Dashboard
</template>
<script setup>
const dataUser = userData();
if (dataUser) {
    console.log(dataUser.value);
}
</script>