import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

console.log('main.ts loading...');

try {
  console.log('Creating Vue app...');
  
  const app = createApp(App)
  
  // Add Pinia store
  app.use(createPinia())
  console.log('Pinia added successfully');
  
  // Add router
  app.use(router)
  console.log('Router added successfully');
  
  // Add Element Plus
  app.use(ElementPlus)
  console.log('Element Plus added successfully');
  
  app.mount('#app')
  console.log('App mounted successfully');
  
} catch (error) {
  console.error('Error in main.ts:', error);
  const appDiv = document.getElementById('app');
  if (appDiv) {
    appDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: red;"><h1>Error loading Vue app</h1><pre>' + error + '</pre></div>';
  }
}