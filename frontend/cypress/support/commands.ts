/// <reference types="cypress" />

// Custom commands for the application
declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to login as admin
       * @example cy.loginAsAdmin()
       */
      loginAsAdmin(): Chainable<void>
      
      /**
       * Custom command to login as user
       * @example cy.loginAsUser()
       */
      loginAsUser(): Chainable<void>
      
      /**
       * Custom command to wait for page load
       * @example cy.waitForPageLoad()
       */
      waitForPageLoad(): Chainable<void>
    }
  }
}

Cypress.Commands.add('loginAsAdmin', () => {
  cy.session('admin', () => {
    cy.visit('/admin/login')
    cy.get('[data-testid="username-input"]').type('admin')
    cy.get('[data-testid="password-input"]').type('admin123')
    cy.get('[data-testid="login-button"]').click()
    cy.url().should('include', '/admin/dashboard')
  })
})

Cypress.Commands.add('loginAsUser', () => {
  cy.session('user', () => {
    cy.visit('/user/login')
    cy.get('[data-testid="username-input"]').type('user')
    cy.get('[data-testid="password-input"]').type('user123')
    cy.get('[data-testid="login-button"]').click()
    cy.url().should('include', '/user/dashboard')
  })
})

Cypress.Commands.add('waitForPageLoad', () => {
  cy.window().its('document.readyState').should('equal', 'complete')
  // Wait for any loading spinners to disappear
  cy.get('[data-testid="loading"]', { timeout: 10000 }).should('not.exist')
})

export {}