
<template>
  <Navbar></Navbar>
  <main class="relative">
    <NuxtPage ></NuxtPage>
  </main>
</template>
<script>

useHead({
  title:"Cloud OS",
  meta: [
    { name: 'description', content: 'Launch Alpine OS or any other browser in one click' }
  ],
});
</script>