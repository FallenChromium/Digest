import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ContentDetail from '@/views/ContentDetail.vue';
import ContentListView from '@/views/ContentListView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/content/:id',
      name: 'ContentDetail',
      component: ContentDetail,
    },
    {
      path: '/content',
      name: 'ContentList',
      component: ContentListView,
    },
  ],
})

export default router;