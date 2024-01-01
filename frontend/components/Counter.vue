<template>
    <div>
      <span>{{ formattedTime }}</span>
    </div>
  </template>
  
  <script setup>
  import { ref, watchEffect } from 'vue';
  
  const props = defineProps(['hours', 'minutes', 'seconds']);
  
  const totalSeconds = ref(calculateTotalSeconds());
  
  function calculateTotalSeconds() {
    return props.hours * 3600 + props.minutes * 60 + props.seconds;
  }
  
  function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
  }
  
  watchEffect(() => {
    totalSeconds.value = calculateTotalSeconds();
  });
  
  const formattedTime = ref(formatTime(totalSeconds.value));
  watchEffect(() => {
    const timer = setInterval(() => {
      totalSeconds.value--;
  
      if (totalSeconds.value >= 0) {
        formattedTime.value = formatTime(totalSeconds.value);
      } else {
        clearInterval(timer);
      }
    }, 1000);
  });
  
  </script>
  
  <style scoped>
  /* Add your styling here */
  </style>
  