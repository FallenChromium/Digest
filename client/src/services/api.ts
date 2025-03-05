import axios from 'axios';
import type { Content, PaginatedResponse, SearchBenchmark, Source } from '@/types/api';
import { mockSources, mockPaginatedContent, mockSearchBenchmark } from '@/mocks/data';

const USE_MOCK_DATA = false; // Toggle this to switch between mock and real API

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getSources = async (): Promise<Source[]> => {
  if (USE_MOCK_DATA) {
    return Promise.resolve(mockSources);
  }
  const response = await api.get<Source[]>('/sources');
  return response.data;
};

export const getContent = async (
  page: number = 1,
  size: number = 10
): Promise<PaginatedResponse<Content>> => {
  if (USE_MOCK_DATA) {
    return Promise.resolve(mockPaginatedContent(page, size));
  }
  const response = await api.get<PaginatedResponse<Content>>('/content', {
    params: { page, size },
  });
  return response.data;
};

export const searchContent = async (
  query: string
): Promise<SearchBenchmark> => {
  if (USE_MOCK_DATA) {
    return Promise.resolve(mockSearchBenchmark(query));
  }
  const response = await api.get<SearchBenchmark>(`/content/search/benchmark`, {
    params: { query },
  });
  return response.data;
}; 