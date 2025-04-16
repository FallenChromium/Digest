<template>
  <div class="home-container">
    <n-space vertical size="large">
      <!-- Sources Section -->
      <n-card title="Sources" class="card-container">
        <n-space vertical>
          <n-data-table
            :columns="sourceColumns"
            :data="sources"
            :loading="loadingSources"
            :pagination="{
              pageSize: 10,
              showSizePicker: true,
              pageSizes: [5, 10, 15, 20],
            }"
            :bordered="false"
            class="clean-table"
          />
          <n-empty
            v-if="!loadingSources && sources.length === 0"
            description="No sources available"
          >
            <template #extra>
              <n-text depth="3">Add some sources to start collecting content</n-text>
            </template>
          </n-empty>
        </n-space>
      </n-card>

      <!-- Search Section -->
      <n-card title="Search Content" class="card-container">
        <n-space vertical>
          <span class="switch-label">Semantic search</span>
          <n-switch v-model:value="semanticSearch" label: />

          <n-input-group>
            <n-input
              v-model:value="searchQuery"
              placeholder="Search content..."
              @keyup.enter="handleSearch"
              class="search-input"
              clearable
            />
            <n-button
              type="primary"
              :loading="searching"
              @click="handleSearch"
              class="search-button"
            >
              Search
            </n-button>
          </n-input-group>

          <!-- Search Results -->
          <template v-if="searchResults">
            <n-divider>Results</n-divider>
            <n-list v-if="searchResults.length > 0" class="results-list">
              <n-list-item v-for="result in searchResults" :key="result.id">
                <n-thing :title="result.title" class="content-item">
                  <template #header>
                    <n-tag :bordered="false" type="info" size="small">
                      {{ getSourceName(result.source_id) }}
                    </n-tag>
                  </template>
                  <template #description>
                    <n-text depth="3">{{ formatDate(result.published_at) }}</n-text>
                  </template>
                  <div class="content-text">{{ result.content }}</div>

                  <template #footer>
                    <n-space align="center">
                      <n-button
                        text
                        type="primary"
                        tag="a"
                        :href="result.url"
                        target="_blank"
                        class="source-link"
                      >
                        View Source
                      </n-button>

                      <n-button
                        type="default"
                        @click="goToContentPage(result.id)"
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
                      v-for="similar in result.similar"
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
            <n-empty v-else description="No results found. Try different search terms."></n-empty>
          </template>
        </n-space>
      </n-card>

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
import { onMounted, ref, h } from 'vue';
import { useRouter } from 'vue-router';
import {
  NSpace,
  NCard,
  NDataTable,
  NInput,
  NInputGroup,
  NButton,
  NSwitch,
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
import type { DataTableColumns } from 'naive-ui';
import { getContent, getSources, searchContent, getSimilarContent } from '@/services/api';
import type { Content, Source } from '@/types/api';
import { SearchMethod } from '@/types/api';

const message = useMessage();
const router = useRouter();

// State
const sources = ref<Source[]>([]);
const content = ref<Content[]>([]);
const searchQuery = ref('');
const searchResults = ref<Content[] | null>(null);
const currentPage = ref(1);
const pageSize = ref(10);
const totalItems = ref(0);
const semanticSearch = ref(false);
const loadingSources = ref(false);
const loadingContent = ref(false);
const searching = ref(false);

// Source columns configuration
const sourceColumns: DataTableColumns<Source> = [
  {
    title: 'Name',
    key: 'name',
  },
  {
    title: 'URL',
    key: 'url',
    render: (row) => {
      return h(
        'a',
        {
          href: row.url,
          target: '_blank',
        },
        { default: () => row.url }
      );
    },
  },
  {
    title: 'Created At',
    key: 'created_at',
    render: (row) => formatDate(row.created_at),
  },
];

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

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    message.warning('Please enter a search query');
    return;
  }

  searching.value = true;
  try {
    searchResults.value = await searchContent(searchQuery.value, semanticSearch.value ? SearchMethod.SEMANTIC : SearchMethod.FTS);
    for (let result of searchResults.value) {
      const similarContent = await getSimilarContent(result.id);
      result.similar = similarContent;
    }
  } catch (error) {
    message.error('Failed to perform search');
    console.error('Failed to search content:', error);
  } finally {
    searching.value = false;
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
:root {
  --content-max-width: 1200px;
}

.home-container {
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 16px;
  box-sizing: border-box;
}

.n-card {
  margin-bottom: 16px;
}

.n-card:last-child {
  margin-bottom: 0;
}

.card-container {
  width: 100%;
}

.search-input {
  flex: 1;
}

.search-button {
  min-width: 100px;
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

.analysis-container {
  margin: 16px 0;
}

.results-list,
.content-list {
  margin: 16px 0;
  border-radius: 8px;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.clean-table :deep(th) {
  background-color: var(--n-table-header-color) !important;
}

:deep(.n-thing-main) {
  flex: 1;
}

:deep(.n-list-item) {
  padding: 0;
}

:deep(.n-layout-header) {
  padding: 8px 16px;
}

:deep(.n-page-header) {
  padding: 0;
}

:deep(.n-card) {
  background: var(--n-color);
}
</style>
