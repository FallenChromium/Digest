<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import {
  NConfigProvider,
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NPageHeader,
  NLoadingBarProvider,
  NDialogProvider,
  NNotificationProvider,
  NMessageProvider,
  NSpace,
  NButton,
} from 'naive-ui';

const router = useRouter();

const navigateToHome = () => {
  router.push('/');
};

const navigateToContent = () => {
  router.push('/content');
};

// Add navigation function for About page
const navigateToAbout = () => {
  router.push('/about');
};
</script>

<template>
  <n-config-provider>
    <n-loading-bar-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <n-message-provider>
            <n-layout class="layout">
              <n-layout-header bordered class="header">
                <n-page-header>
                  <template #title>
                    <div class="header-title" @click="navigateToHome">Digest Project</div>
                  </template>
                  <template #extra>
                    <n-space>
                      <n-button @click="navigateToHome">Home</n-button>
                      <n-button @click="navigateToContent">All Content</n-button>
                      <n-button @click="navigateToAbout">About</n-button>
                    </n-space>
                  </template>
                </n-page-header>
              </n-layout-header>
              <n-layout-content class="content">
                <router-view />
              </n-layout-content>
            </n-layout>
          </n-message-provider>
        </n-notification-provider>
      </n-dialog-provider>
    </n-loading-bar-provider>
  </n-config-provider>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  width: 100%;
}

#app {
  height: 100vh;
  width: 100vw;
  margin: 0 auto;
  font-weight: normal;
}

.layout {
  height: 100vh;
  width: 100vw;
}

.header {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
}

.header-title {
  cursor: pointer;
}

.content {
  height: calc(100vh - 64px);
  padding: 0;
  overflow-y: auto;
}
</style>
