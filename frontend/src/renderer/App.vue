<template>
  <div class="container">
    <div class="toolbar">
      <button @click="openFile">打开日志文件</button>
      <span v-if="currentFile">当前文件: {{ currentFile }}</span>
    </div>

    <div class="input-group">
      <input
        v-model="keywordsInput"
        placeholder="输入关键词（用逗号分隔）"
        @keyup.enter="searchSequence"
      >
      <button @click="searchSequence">搜索序列</button>
    </div>

    <div v-if="error" class="error-alert">
      {{ error }}
    </div>

    <div class="chart-container">
      <TimelineChart
        v-for="(sequence, index) in sequences"
        :key="index"
        :sequence="sequence"
        :file-path="currentFile"
        @remove="removeSequence(index)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import TimelineChart from './components/TimelineChart.vue'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const currentFile = ref(null)
const keywordsInput = ref('')
const sequences = ref([])
const error = ref(null)

const openFile = async () => {
  try {
    const file = await window.electronAPI.openFileDialog()
    if (file) {
      currentFile.value = file
      await axios.post(`${API_BASE}/index-file`, { file_path: file })
      error.value = null
    }
  } catch (err) {
    error.value = `文件处理失败: ${err.response?.data?.detail || err.message}`
  }
}

const searchSequence = async () => {
  if (!keywordsInput.value.trim()) return

  try {
    const response = await axios.get(`${API_BASE}/search-sequence`, {
      params: { keywords: keywordsInput.value }
    })
    sequences.value.push({
      keywords: keywordsInput.value.split(','),
      data: response.data.data
    })
    keywordsInput.value = ''
    error.value = null
  } catch (err) {
    error.value = `查询失败: ${err.response?.data?.detail || err.message}`
  }
}

const removeSequence = (index) => {
  sequences.value.splice(index, 1)
}
</script>

<style>
.error-alert {
  background-color: #f8d7da;
  color: #721c24;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
}

.toolbar {
  margin-bottom: 1.5rem;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.chart-container {
  display: grid;
  gap: 1.5rem;
}
</style>