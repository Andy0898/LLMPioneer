# LLM Pioneer Frontend

A modern Vue 3 + TypeScript frontend application for the LLM Pioneer platform, featuring dual portals for administrators and consumers.

## Features

### 🎯 Dual Portal Architecture
- **Admin Portal** (`/admin/*`): System management interface
- **Consumer Portal** (`/user/*`): End-user AI services interface

### 🔐 Authentication & Security
- JWT-based authentication with automatic refresh
- Role-based access control (RBAC)
- Portal-specific access management
- Secure route guards

### 💬 AI Chat System
- Real-time conversations with AI assistants
- Message editing and regeneration
- Conversation history and search
- Optimistic UI updates

### 📚 Knowledge Management
- Document upload with progress tracking
- Category-based organization
- Vector search capabilities
- Processing status monitoring

### 🎨 Modern UI/UX
- Element Plus component library
- Tailwind CSS for styling
- Responsive design
- Dark mode support
- Accessibility features

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Vue 3 | ^3.4.29 |
| Language | TypeScript | ~5.4.0 |
| Build Tool | Vite | ^5.3.1 |
| UI Library | Element Plus | ^2.7.6 |
| State Management | Pinia | ^2.1.7 |
| HTTP Client | Axios | ^1.7.2 |
| Routing | Vue Router | ^4.3.3 |
| Styling | Tailwind CSS | ^3.4.4 |

## Getting Started

### Prerequisites
- Node.js 18.0 or higher
- npm or yarn package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd llm-pioneer/frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.development.example .env.development
# Edit .env.development with your configuration
```

4. **Start development server**
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Code Quality
npm run type-check   # TypeScript type checking
npm run lint         # ESLint code linting
npm run format       # Prettier code formatting

# Testing
npm run test:unit    # Run unit tests
npm run test:e2e     # Run end-to-end tests
npm run test:coverage # Generate test coverage report
```

## Project Structure

```
src/
├── api/              # API service modules
│   ├── auth.ts       # Authentication API
│   ├── conversation.ts # Chat API
│   ├── knowledge.ts  # Knowledge base API
│   └── user.ts       # User management API
├── components/       # Reusable components
│   ├── AppHeader.vue
│   ├── AppSidebar.vue
│   ├── LoadingSpinner.vue
│   ├── ErrorBoundary.vue
│   └── ConfirmDialog.vue
├── layouts/          # Layout components
│   ├── AdminLayout.vue
│   └── ConsumerLayout.vue
├── router/           # Vue Router configuration
│   ├── index.ts      # Main router setup
│   ├── guards.ts     # Route guards
│   └── constants.ts  # Route constants
├── stores/           # Pinia state management
│   ├── auth.ts       # Authentication store
│   ├── conversation.ts # Chat store
│   └── knowledge.ts  # Knowledge base store
├── types/            # TypeScript type definitions
│   ├── auth.ts
│   ├── conversation.ts
│   ├── knowledge.ts
│   └── common.ts
├── utils/            # Utility functions
├── views/            # Page components
│   ├── admin/        # Admin portal pages
│   ├── consumer/     # Consumer portal pages
│   └── error/        # Error pages
└── assets/           # Static assets
    ├── images/
    └── styles/
```

## Architecture

### Component Architecture
The application follows a modular component architecture:

- **Layouts**: Define the overall page structure for each portal
- **Shared Components**: Reusable UI components across the application
- **Views**: Page-level components representing different routes
- **Portal-Specific Components**: Components unique to admin or consumer portals

### State Management
Pinia stores are organized by domain:

- **Auth Store**: User authentication and authorization
- **Conversation Store**: Chat conversations and messages
- **Knowledge Store**: Document management and search

### API Layer
Centralized API services with:

- Automatic JWT token injection
- Error handling and retry logic
- Request/response interceptors
- Type-safe interfaces

## Development Guidelines

### Code Style
- Follow Vue 3 Composition API patterns
- Use TypeScript for type safety
- Follow ESLint and Prettier configurations
- Use conventional commit messages

### Component Guidelines
- Use `<script setup>` syntax for Vue components
- Define proper TypeScript interfaces for props and emits
- Implement proper error boundaries
- Follow accessibility best practices

### State Management
- Use Pinia stores for global state
- Keep component state local when possible
- Implement proper error handling in stores
- Use computed properties for derived state

## Testing

### Unit Testing
```bash
npm run test:unit
```
- Test components with Vue Test Utils
- Test stores with Pinia testing utilities
- Test utility functions with Vitest

### End-to-End Testing
```bash
npm run test:e2e
```
- Test user workflows with Cypress
- Test authentication flows
- Test portal-specific features

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy
```bash
# Build for production
npm run build

# Preview production build locally
npm run preview

# Deploy to static hosting
# Upload dist/ folder to your hosting service
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |
| `VITE_APP_TITLE` | Application title | `LLM Pioneer` |
| `VITE_ENVIRONMENT` | Environment name | `development` |

## Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Performance

### Optimization Features
- **Code Splitting**: Automatic route-based and component-based splitting
- **Tree Shaking**: Unused code elimination
- **Asset Optimization**: Image compression and lazy loading
- **Caching**: Intelligent browser caching strategies

### Performance Targets
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Time to Interactive: < 3s
- Cumulative Layout Shift: < 0.1

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow
1. Follow the coding standards
2. Write tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting

## Troubleshooting

### Common Issues

**Development server won't start**
- Check Node.js version (18.0+)
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall

**Build fails**
- Run type checking: `npm run type-check`
- Check for ESLint errors: `npm run lint`
- Verify environment variables

**API calls fail**
- Check backend server is running
- Verify API base URL in environment variables
- Check network/CORS configuration

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation and deployment guide