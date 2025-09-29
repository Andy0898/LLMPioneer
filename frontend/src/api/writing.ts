import { api } from './client'

export const writingApi = {
  // Use writing tool
  useTool: (tool: string, content: string) =>
    api.post('/writing/tools/use', { tool, content }),

  // Get writing suggestions
  getSuggestions: (content: string) =>
    api.post('/writing/suggestions', { content }),

  // Get writing templates
  getTemplates: () =>
    api.get('/writing/templates'),

  // Save custom template
  saveTemplate: (template: { name: string; description: string; content: string }) =>
    api.post('/writing/templates', template),

  // Analyze text
  analyzeText: (content: string) =>
    api.post('/writing/analyze', { content })
}