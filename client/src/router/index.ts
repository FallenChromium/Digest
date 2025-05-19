import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ContentDetail from '@/views/ContentDetail.vue';
import ContentListView from '@/views/ContentListView.vue';
import AboutView from '@/views/AboutView.vue';

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
    {
      path: '/about',
      name: 'About',
      component: AboutView,
    }
  ],
})

export default router;