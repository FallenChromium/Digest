<template>
  <div class="content-list-container">
    <n-space vertical size="large">
      <!-- Content Section -->
      <n-card title="All Content" class="card-container">
        <n-space vertical>
          <n-list v-if="content.length > 0" class="content-list">
            <n-list-item v-for="item in content" :key="item.id">
              <n-thing :title="item.title" class="content-item">
                <template #header>
                  <n-tag :bordered="false" type="info" size="small">
                    {{ getSourceName(item.source_id) }}
                  </n-tag>
                </template>
                <template #description>
                  <n-text depth="3">{{ formatDate(item.published_at) }}</n-text>
                </template>
                <div class="content-text">{{ item.content }}</div>

                <template #footer>
                  <n-space align="center">
                    <n-button
                      text
                      type="primary"
                      tag="a"
                      :href="item.url"
                      target="_blank"
                      class="source-link"
                    >
                      View Source
                    </n-button>

                    <n-button
                      type="default"
                      @click="goToContentPage(item.id)"
                      class="details-button"
                    >
                      Details
                    </n-button>
                  </n-space>
                </template>

                <!-- Display Similar Content -->
                <n-divider>Similar Content</n-divider>
                <n-space align="center" wrap>
                  <n-button
                    v-for="similar in item.similar"
                    :key="similar.id"
                    @click="goToContentPage(similar.id)"
                    size="small"
                  >
                  {{ getSourceName(similar.source_id) }} | {{ similar.content.substring(0, 20) + '...' }}
                  </n-button>
                </n-space>
              </n-thing>
            </n-list-item>
          </n-list>
          <n-empty
            v-else-if="totalItems === 0"
            description="No content available. Content will appear here once sources start collecting data"
          ></n-empty>

          <n-pagination
            v-if="totalItems > 0"
            v-model:page="currentPage"
            v-model:page-size="pageSize"
            :item-count="totalItems"
            show-size-picker
            :page-sizes="[10, 20, 30, 40]"
            @update:page="loadContent"
            @update:page-size="handlePageSizeChange"
            class="pagination"
          />
        </n-space>
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import {
  NSpace,
  NCard,
  NButton,
  NDivider,
  NList,
  NListItem,
  NThing,
  NText,
  NTag,
  NPagination,
  NEmpty,
  useMessage,
} from 'naive-ui';
import { getContent, getSources, getSimilarContent } from '@/services/api';
import type { Content, Source } from '@/types/api';

const message = useMessage();
const router = useRouter();

// State
const sources = ref<Source[]>([]);
const content = ref<Content[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const totalItems = ref(0);
const loadingSources = ref(false);
const loadingContent = ref(false);

// Methods
const loadSources = async () => {
  loadingSources.value = true;
  try {
    sources.value = await getSources();
  } catch (error) {
    message.error('Failed to load sources');
    console.error('Failed to load sources:', error);
  } finally {
    loadingSources.value = false;
  }
};

const loadContent = async () => {
  loadingContent.value = true;
  try {
    const response = await getContent(currentPage.value, pageSize.value);
    content.value = response;
    totalItems.value = response.length;

    // Fetch similar content for each piece
    for (let item of content.value) {
      const similarContent = await getSimilarContent(item.id);
      item.similar = similarContent;
    }
  } catch (error) {
    message.error('Failed to load content');
    console.error('Failed to load content:', error);
  } finally {
    loadingContent.value = false;
  }
};

const handlePageSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  loadContent();
};

const getSourceName = (sourceId: string): string => {
  const source = sources.value.find((s) => s.id === sourceId);
  return source?.name || 'Unknown Source';
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const goToContentPage = (id: string) => {
  router.push({ name: 'ContentDetail', params: { id } });
};

onMounted(() => {
  loadSources();
  loadContent();
});
</script>

<style scoped>
.content-list-container {
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 16px;
  box-sizing: border-box;
}

.card-container {
  width: 100%;
}

.content-item {
  padding: 16px;
}

.content-text {
  margin: 12px 0;
  line-height: 1.6;
  color: var(--n-text-color);
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.source-link {
  font-size: 14px;
}

.details-button {
  font-size: 14px;
  margin-left: 8px;
}

.content-list {
  margin: 16px 0;
  border-radius: 8px;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

:deep(.n-thing-main) {
  flex: 1;
}

:deep(.n-list-item) {
  padding: 0;
}
</style>