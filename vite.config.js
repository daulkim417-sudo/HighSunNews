import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // 반드시 레포지토리 이름과 일치해야 해! 앞뒤 슬래시(/) 필수.
  base: '/HighSunNews/', 
})