<template>
  <div class="chart-wrapper">
    <div class="chart-header">
      <h3>{{ sequence.keywords.join(' → ') }}</h3>
      <button @click="$emit('remove')">×</button>
    </div>
    <div ref="chart" class="chart"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const props = defineProps({
  sequence: Object,
  filePath: String
})

const chart = ref(null)
let chartInstance = null

const initChart = () => {
  chartInstance = echarts.init(chart.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: async (params) => {
        if (params.data.status === 'missing') {
          return `Missing: ${params.name}`
        }
        const res = await axios.get('/api/get-log-line', {
          params: {
            position: params.data.position,
            file_path: props.filePath
          }
        })
        return res.data.content
      }
    },
    xAxis: { type: 'time' },
    yAxis: { show: false },
    series: [{
      type: 'line',
      symbolSize: 12,
      data: props.sequence.data.map(item => ({
        name: item.keyword,
        value: [item.timestamp * 1000, 0],
        position: item.position,
        status: item.status
      })),
      lineStyle: {
        color: '#1890ff'
      }
    }]
  }

  chartInstance.setOption(option)
}

watch(() => props.sequence, () => {
  chartInstance.dispose()
  initChart()
})

onMounted(initChart)
</script>

<style>
.chart-wrapper {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  background: white;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.chart {
  height: 200px;
}
</style>