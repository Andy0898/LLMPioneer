describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should redirect to user dashboard by default', () => {
    cy.url().should('include', '/user/dashboard')
  })

  it('should allow admin login', () => {
    cy.visit('/admin/login')
    
    // Fill login form
    cy.get('[data-testid="username-input"]').type('admin')
    cy.get('[data-testid="password-input"]').type('admin123')
    cy.get('[data-testid="login-button"]').click()
    
    // Should redirect to admin dashboard
    cy.url().should('include', '/admin/dashboard')
    cy.contains('Dashboard').should('be.visible')
  })

  it('should allow user login', () => {
    cy.visit('/user/login')
    
    // Fill login form
    cy.get('[data-testid="username-input"]').type('user')
    cy.get('[data-testid="password-input"]').type('user123')
    cy.get('[data-testid="login-button"]').click()
    
    // Should redirect to user dashboard
    cy.url().should('include', '/user/dashboard')
    cy.contains('Dashboard').should('be.visible')
  })

  it('should show error for invalid credentials', () => {
    cy.visit('/user/login')
    
    // Fill login form with invalid credentials
    cy.get('[data-testid="username-input"]').type('invalid')
    cy.get('[data-testid="password-input"]').type('invalid')
    cy.get('[data-testid="login-button"]').click()
    
    // Should show error message
    cy.contains('Invalid credentials').should('be.visible')
  })

  it('should logout successfully', () => {
    cy.loginAsUser()
    cy.visit('/user/dashboard')
    
    // Click logout button
    cy.get('[data-testid="logout-button"]').click()
    
    // Should redirect to login page
    cy.url().should('include', '/user/login')
  })
})