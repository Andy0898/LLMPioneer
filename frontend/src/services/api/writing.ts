import { httpClient } from './http'

export const writingApi = {
  // Use writing tool
  useTool: (tool: string, content: string) =>
    httpClient.post('/writing/tools/use', { tool, content }),

  // Get writing suggestions
  getSuggestions: (content: string) =>
    httpClient.post('/writing/suggestions', { content }),

  // Get writing templates
  getTemplates: () =>
    httpClient.get('/writing/templates'),

  // Save custom template
  saveTemplate: (template: { name: string; description: string; content: string }) =>
    httpClient.post('/writing/templates', template),

  // Analyze text
  analyzeText: (content: string) =>
    httpClient.post('/writing/analyze', { content })
}