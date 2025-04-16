<template>
  <n-space>
    <n-button type="default" @click="goBack" class="go-back-button"> Go Back </n-button>
  </n-space>
  <div class="content-detail-container" v-if="content">
    <n-card :title="content.title">
      <n-space vertical>
        <n-tag :bordered="false" type="info" size="small">
          {{ getSourceName(content.source_id) }}
        </n-tag>
        <n-text depth="3">{{ formatDate(content.published_at) }}</n-text>
        <div class="content-text">{{ content.content }}</div>

        <n-button
          text
          type="primary"
          tag="a"
          :href="content.url"
          target="_blank"
          class="source-link"
        >
          View Source
        </n-button>

        <n-divider>Similar Content</n-divider>
        <n-list hoverable clickable>
          <n-list-item
            v-for="similar in similarContents"
            :key="similar.id"
            @click="goToContentPage(similar.id)"
          >
            <n-text>
              {{ getSourceName(similar.source_id) }} | {{ similar.content.substring(0, 50) + '...' }}
            </n-text>
          </n-list-item>
        </n-list>
      </n-space>
    </n-card>
  </div>
  <div v-else>Loading...</div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import {
  NSpace,
  NCard,
  NButton,
  NDivider,
  NList,
  NListItem,
  NText,
  NTag,
  useMessage,
} from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'
import { getSources, getContentById, getSimilarContent } from '@/services/api'
import type { Content, Source } from '@/types/api'

const message = useMessage()
const router = useRouter()
const route = useRoute()

const sources = ref<Source[]>([])
const content = ref<Content | null>(null)
const loadingSources = ref(false)
const similarContents = ref<Content[]>([])

const loadSources = async () => {
  loadingSources.value = true
  try {
    sources.value = await getSources()
  } catch (error) {
    message.error('Failed to load sources')
    console.error('Failed to load sources:', error)
  } finally {
    loadingSources.value = false
  }
}
const loadContentDetail = async () => {
  const id = route.params.id as string
  try {
    content.value = await getContentById(id)
    similarContents.value = await getSimilarContent(id)
  } catch (error) {
    console.error('Failed to load content detail:', error)
  }
}

const goBack = () => {
  router.push('/')
}

const goToContentPage = (id: string) => {
  router.push({ name: 'ContentDetail', params: { id } })
}

const getSourceName = (sourceId: string): string => {
  const source = sources.value.find((s) => s.id === sourceId)
  return source?.name || 'Unknown Source'
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadSources()
  loadContentDetail()
})
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadContentDetail()
  }
})
</script>

<style scoped>
.content-detail-container {
  max-width: 800px;
  margin: 0 auto;
}
</style>
