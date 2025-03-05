import type { Content, PaginatedResponse, SearchBenchmark, Source } from '@/types/api';

export const mockSources: Source[] = [
  {
    id: '1',
    name: 'TechCrunch',
    url: 'https://techcrunch.com',
    created_at: '2024-03-05T08:00:00Z',
    updated_at: '2024-03-05T08:00:00Z',
  },
  {
    id: '2',
    name: 'The Verge',
    url: 'https://theverge.com',
    created_at: '2024-03-05T08:01:00Z',
    updated_at: '2024-03-05T08:01:00Z',
  },
  {
    id: '3',
    name: 'Hacker News',
    url: 'https://news.ycombinator.com',
    created_at: '2024-03-05T08:02:00Z',
    updated_at: '2024-03-05T08:02:00Z',
  },
];

export const mockContent: Content[] = [
  {
    id: '1',
    source_id: '1',
    title: 'OpenAI Announces GPT-5',
    content: 'OpenAI has announced their latest language model, GPT-5, which shows unprecedented capabilities in reasoning and understanding. The model demonstrates significant improvements in areas such as mathematical problem-solving, code generation, and natural language understanding.',
    url: 'https://techcrunch.com/openai-gpt5',
    created_at: '2024-03-05T09:00:00Z',
    updated_at: '2024-03-05T09:00:00Z',
  },
  {
    id: '2',
    source_id: '2',
    title: "Apple's New MacBook Pro Review",
    content: 'The latest MacBook Pro with M3 Max chip sets new standards for laptop performance. Our extensive testing shows improvements in both CPU and GPU performance, with some tasks completing up to 40% faster than the previous generation.',
    url: 'https://theverge.com/macbook-pro-m3-review',
    created_at: '2024-03-05T09:30:00Z',
    updated_at: '2024-03-05T09:30:00Z',
  },
  {
    id: '3',
    source_id: '3',
    title: "Rust Becomes Linux Kernel's Second Official Language",
    content: 'In a historic move, Rust has been officially adopted as the second programming language for Linux kernel development, joining C. This decision aims to improve memory safety in kernel development while maintaining performance.',
    url: 'https://news.ycombinator.com/rust-linux-kernel',
    created_at: '2024-03-05T10:00:00Z',
    updated_at: '2024-03-05T10:00:00Z',
  },
];

export const mockPaginatedContent = (page: number = 1, size: number = 10): PaginatedResponse<Content> => {
  const start = (page - 1) * size;
  const end = start + size;
  return {
    items: mockContent.slice(start, end),
    total: mockContent.length,
    page,
    size,
  };
};

export const mockSearchBenchmark = (query: string): SearchBenchmark => {
  const results = mockContent.filter(
    (item) =>
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.content.toLowerCase().includes(query.toLowerCase())
  );

  return {
    query,
    results,
    analysis: {
      total_time: 0.156,
      preprocessing_time: 0.023,
      search_time: 0.089,
      ranking_time: 0.044,
    },
  };
}; 