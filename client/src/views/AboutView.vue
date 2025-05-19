<template>
  <div class="about-container">
    <n-card title="About Digest" class="about-card">
      <n-space vertical size="large">
        <section>
          <h2>Purpose</h2>
          <p>
            Digest is a content aggregation and summarization platform designed to help users efficiently process and understand large amounts of information from various sources. The application collects content from different sources, allows users to search through it using both traditional and semantic search methods, and provides AI-powered summarization capabilities to extract key insights with the help of RAG.
          </p>
        </section>

        <section>
          <h2>Technologies & Tools</h2>
          <n-space vertical>
            <div>
              <h3>Frontend</h3>
              <ul>
                <li><strong>Vue.js 3</strong> - Progressive JavaScript framework with Composition API</li>
                <li><strong>TypeScript</strong> - For type-safe code</li>
                <li><strong>Naive UI</strong> - Vue component library for the user interface</li>
                <li><strong>Vue Router</strong> - For application routing</li>
                <li><strong>Vite</strong> - Next generation frontend tooling</li>
              </ul>
            </div>
            <div>
              <h3>Backend</h3>
              <ul>
                <li><strong>Python</strong> - Core backend language</li>
                <li><strong>FastAPI</strong> - Modern, high-performance web framework</li>
                <li><strong>SQLModel</strong> - SQL databases in Python with type annotations</li>
                <li><strong>Ollama</strong> - For running LLM models locally (llama3.1)</li>
              </ul>
            </div>
          </n-space>
        </section>

        <section>
          <h2>System Design</h2>
          <p>
            Digest follows a client-server architecture:
          </p>
          <ol>
            <li><strong>Content Collection</strong> - Backend services collect content from configured sources</li>
            <li><strong>Storage</strong> - Content is stored in a database with metadata</li>
            <li><strong>Search & Retrieval</strong> - Both full-text and semantic search capabilities</li>
            <li><strong>Summarization</strong> - AI-powered summarization using LLMs</li>
            <li><strong>User Interface</strong> - Vue.js frontend for content browsing, searching, and viewing</li>
          </ol>
        </section>

        <section>
          <h2>Key Challenges & Solutions</h2>
          <n-space vertical>
            <div>
              <h3>Challenge: Efficient Content Processing</h3>
              <p>Processing large amounts of content from various sources efficiently.</p>
              <p><strong>Solution:</strong> Implemented asynchronous content processing and pagination for better performance.</p>
            </div>
            <div>
              <h3>Challenge: Semantic Search</h3>
              <p>Implementing meaningful semantic search beyond simple keyword matching.</p>
              <p><strong>Solution:</strong> Utilized vector embeddings and similarity algorithms to enable semantic search capabilities.</p>
            </div>
            <div>
              <h3>Challenge: Summarization with Citing</h3>
              <p>Generating high-quality, accurate summaries of diverse content and cite it.</p>
              <p><strong>Solution:</strong> Leveraged LLM capabilities with carefully crafted prompts that include citation requirements for factual accuracy using RAG.</p>
            </div>
          </n-space>
        </section>
      </n-space>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { NCard, NSpace } from 'naive-ui';
</script>

<style scoped>
.about-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.about-card {
  margin-bottom: 24px;
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 16px;
  color: var(--primary-color);
}

h3 {
  font-size: 1.2rem;
  margin-bottom: 8px;
  margin-top: 16px;
}

p {
  line-height: 1.6;
  margin-bottom: 12px;
}

ul, ol {
  padding-left: 24px;
  margin-bottom: 16px;
}

li {
  margin-bottom: 8px;
  line-height: 1.5;
}

section {
  margin-bottom: 16px;
}
</style>
