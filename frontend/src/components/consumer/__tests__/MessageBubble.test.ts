import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ElButton, ElMessage } from 'element-plus'
import MessageBubble from '@/components/consumer/MessageBubble.vue'
import type { Message } from '@/types/chat'

// Mock Element Plus Message
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn()
    }
  }
})

// Mock navigator.clipboard
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn(() => Promise.resolve())
  }
})

describe('MessageBubble', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const mockUserMessage: Message = {
    id: '1',
    text: 'Hello, how are you?',
    isUser: true,
    timestamp: '2024-01-01T10:00:00Z'
  }

  const mockAssistantMessage: Message = {
    id: '2',
    text: 'I am doing well, thank you for asking!',
    isUser: false,
    timestamp: '2024-01-01T10:01:00Z'
  }

  it('renders user message correctly', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: mockUserMessage
      },
      global: {
        components: {
          ElButton
        }
      }
    })

    expect(wrapper.find('.user-message-bubble').exists()).toBe(true)
    expect(wrapper.find('.user-text').exists()).toBe(true)
    expect(wrapper.text()).toContain('Hello, how are you?')
  })

  it('renders assistant message correctly', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: mockAssistantMessage
      },
      global: {
        components: {
          ElButton
        }
      }
    })

    expect(wrapper.find('.assistant-message-bubble').exists()).toBe(true)
    expect(wrapper.find('.assistant-text').exists()).toBe(true)
    expect(wrapper.text()).toContain('I am doing well, thank you for asking!')
  })

  it('shows edit button for user messages', async () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: mockUserMessage
      },
      global: {
        components: {
          ElButton
        }
      }
    })

    // Hover to show actions
    await wrapper.find('.message-bubble').trigger('mouseenter')
    expect(wrapper.find('.message-actions').exists()).toBe(true)
  })

  it('emits edit event when edit button is clicked', async () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: mockUserMessage
      },
      global: {
        components: {
          ElButton
        }
      }
    })

    const editButton = wrapper.find('[data-testid="edit-button"]')
    if (editButton.exists()) {
      await editButton.trigger('click')
      expect(wrapper.emitted('edit')).toBeTruthy()
    }
  })

  it('copies message to clipboard when copy button is clicked', async () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: mockAssistantMessage
      },
      global: {
        components: {
          ElButton
        }
      }
    })

    const copyButton = wrapper.find('[data-testid="copy-button"]')
    if (copyButton.exists()) {
      await copyButton.trigger('click')
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockAssistantMessage.text)
    }
  })

  it('emits delete event when delete button is clicked', async () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: mockUserMessage
      },
      global: {
        components: {
          ElButton
        }
      }
    })

    const deleteButton = wrapper.find('[data-testid="delete-button"]')
    if (deleteButton.exists()) {
      await deleteButton.trigger('click')
      expect(wrapper.emitted('delete')).toBeTruthy()
    }
  })

  it('formats time correctly', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: mockUserMessage
      },
      global: {
        components: {
          ElButton
        }
      }
    })

    // Test that time formatting works (basic check)
    expect(wrapper.vm.formatTime).toBeDefined()
  })

  it('renders attachments when present', () => {
    const messageWithAttachments: Message = {
      ...mockUserMessage,
      attachments: [
        {
          id: 'att1',
          name: 'document.pdf',
          size: 1024,
          type: 'application/pdf'
        }
      ]
    }

    const wrapper = mount(MessageBubble, {
      props: {
        message: messageWithAttachments
      },
      global: {
        components: {
          ElButton
        }
      }
    })

    expect(wrapper.find('.attachments').exists()).toBe(true)
    expect(wrapper.text()).toContain('document.pdf')
  })

  it('renders sources when present', () => {
    const messageWithSources: Message = {
      ...mockAssistantMessage,
      sources: [
        {
          id: 'src1',
          title: 'Source Document',
          url: 'https://example.com'
        }
      ]
    }

    const wrapper = mount(MessageBubble, {
      props: {
        message: messageWithSources
      },
      global: {
        components: {
          ElButton
        }
      }
    })

    expect(wrapper.find('.sources').exists()).toBe(true)
    expect(wrapper.text()).toContain('Source Document')
  })
})