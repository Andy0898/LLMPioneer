describe('Chat Functionality', () => {
  beforeEach(() => {
    cy.loginAsUser()
    cy.visit('/user/chat')
    cy.waitForPageLoad()
  })

  it('should display chat interface', () => {
    cy.get('[data-testid="chat-interface"]').should('be.visible')
    cy.get('[data-testid="message-input"]').should('be.visible')
    cy.get('[data-testid="send-button"]').should('be.visible')
  })

  it('should send a message', () => {
    const testMessage = 'Hello, this is a test message'
    
    cy.get('[data-testid="message-input"]').type(testMessage)
    cy.get('[data-testid="send-button"]').click()
    
    // Message should appear in chat
    cy.contains(testMessage).should('be.visible')
    
    // Input should be cleared
    cy.get('[data-testid="message-input"]').should('have.value', '')
  })

  it('should create new conversation', () => {
    cy.get('[data-testid="new-chat-button"]').click()
    
    // Should show empty chat interface
    cy.get('[data-testid="empty-state"]').should('be.visible')
    cy.contains('Start a conversation').should('be.visible')
  })

  it('should use quick actions', () => {
    cy.get('[data-testid="quick-action"]').first().click()
    
    // Should populate message input
    cy.get('[data-testid="message-input"]').should('not.have.value', '')
  })

  it('should show conversation list', () => {
    cy.get('[data-testid="conversation-list"]').should('be.visible')
    
    // Should have at least one conversation or empty state
    cy.get('[data-testid="conversation-item"]').should('exist')
      .or(cy.get('[data-testid="empty-conversations"]').should('exist'))
  })

  it('should allow message editing', () => {
    const originalMessage = 'Original message'
    const editedMessage = 'Edited message'
    
    // Send a message
    cy.get('[data-testid="message-input"]').type(originalMessage)
    cy.get('[data-testid="send-button"]').click()
    
    // Hover over message to show actions
    cy.contains(originalMessage).parent().trigger('mouseover')
    
    // Click edit button
    cy.get('[data-testid="edit-message"]').click()
    
    // Edit the message
    cy.get('[data-testid="edit-input"]').clear().type(editedMessage)
    cy.get('[data-testid="save-edit"]').click()
    
    // Verify message was edited
    cy.contains(editedMessage).should('be.visible')
    cy.contains(originalMessage).should('not.exist')
  })

  it('should export conversation', () => {
    // Send a message first
    cy.get('[data-testid="message-input"]').type('Test message for export')
    cy.get('[data-testid="send-button"]').click()
    
    // Export conversation
    cy.get('[data-testid="export-button"]').click()
    
    // Should show success message
    cy.contains('exported successfully').should('be.visible')
  })
})