import axios from 'axios';
import type { Content, Source, SearchMethod } from '@/types/api';
import { mockSources, mockPaginatedContent, mockSearch, mockContent } from '@/mocks/data';

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
): Promise<Content[]> => {
  if (USE_MOCK_DATA) {
    return Promise.resolve(mockPaginatedContent(page, size));
  }
  const response = await api.get<Content[]>('/content', {
    params: { page, size },
  });
  return response.data;
};

export const getContentById = async (content_id: string): Promise<Content> => {
  if (USE_MOCK_DATA) {
    return Promise.resolve(mockContent[0]);
  }
  const response = await api.get<Content>(`/content/${content_id}`, {});
  return response.data;
};

export const getSimilarContent = async (piece_id: string): Promise<Content[]> => {
  if (USE_MOCK_DATA) {
    return Promise.resolve(mockContent.slice(0, 5));
  }
  const response = await api.get<Content[]>('/content/similar', {
    params: { piece_id },
  });
  return response.data.slice(0, 5);
}; 

export const searchContent = async (query: string, method: SearchMethod): Promise<Content[]> => {
  if (USE_MOCK_DATA) {
    return Promise.resolve(mockSearch(query));
  }
  const response = await api.get<Content[]>('/content/search', {
    params: { query, method },
  });
  return response.data;
}; 