<template>
  <div class="summarize-container">
    <n-button
      type="primary"
      :disabled="!contentIds || contentIds.length === 0"
      @click="handleSummarize"
    >
      Summarize Results
    </n-button>
    
    <!-- Summary Results Section -->
    <div v-if="showSummary" class="summary-section">
      <div v-if="error" class="error-message">
        <n-alert type="error" title="Summarization Failed">
          {{ error }}
        </n-alert>
      </div>
      <div v-else>
        <n-card title="Summary" class="summary-card">
          <div v-if="summarizing" class="loading-container">
            <n-spin size="small" />
            <div class="streaming-text">{{ streamedText }}</div>
          </div>
          <div v-else class="summary-content">
            {{ streamedText }}
          </div>
        </n-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps } from 'vue';
import { NButton, NCard, NSpace, NSpin, NAlert, useMessage } from 'naive-ui';
import { summarizeContent } from '@/services/api';

const props = defineProps({
  contentIds: {
    type: Array as () => string[],
    required: true
  }
});

const message = useMessage();
const summarizing = ref(false);
const showSummary = ref(false);
const streamedText = ref('');
const error = ref('');

/**
 * Handles the summarization process
 * Fetches streaming summary from the API and updates UI accordingly
 */
const handleSummarize = async () => {
  if (!props.contentIds || props.contentIds.length === 0) {
    message.warning('No content to summarize');
    return;
  }

  summarizing.value = true;
  showSummary.value = true;
  streamedText.value = '';
  error.value = '';

  try {
    const response = await summarizeContent(props.contentIds);

    const characters = response.split('');
    for (const char of characters) {
        streamedText.value += char;
        // Add a small delay to simulate streaming
        await new Promise(resolve => setTimeout(resolve, 10));
    }
  } catch (err) {
    console.error('Summarization failed:', err);
    error.value = err instanceof Error ? err.message : 'Failed to generate summary';
    message.error('Failed to generate summary');
  } finally {
    summarizing.value = false;
  }
};
</script>

<style scoped>
.summarize-container {
  margin: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-section {
  margin-top: 16px;
}

.summary-card {
  width: 100%;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.streaming-text {
  white-space: pre-wrap;
  line-height: 1.6;
  min-height: 50px;
}

.summary-content {
  white-space: pre-wrap;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
}

.error-message {
  margin-bottom: 16px;
}
</style>