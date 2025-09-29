# Deployment

This guide covers deploying the LLM Pioneer frontend application.

## Build for Production

```bash
npm run build
```

This creates a `dist` directory with production-ready files.

## Environment Variables

Create appropriate `.env` files for each environment:

### Development (`.env.development`)
```
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=LLM Pioneer
VITE_JWT_SECRET=your_jwt_secret_here
VITE_ENVIRONMENT=development
```

### Production (`.env.production`)
```
VITE_API_BASE_URL=https://your-production-api.com
VITE_APP_TITLE=LLM Pioneer
VITE_JWT_SECRET=your_production_jwt_secret
VITE_ENVIRONMENT=production
```

## Deployment Options

### 1. Static Site Hosting (Recommended)

Since this is a SPA (Single Page Application), it can be deployed to any static hosting service:

#### Vercel
```bash
npm install -g vercel
vercel --prod
```

#### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

#### AWS S3 + CloudFront
1. Build the application
2. Upload `dist` contents to S3 bucket
3. Configure CloudFront distribution
4. Set up route redirects for SPA

### 2. Docker Deployment

Create `Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `nginx.conf`:

```nginx
worker_processes auto;
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        # Handle SPA routing
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # Gzip compression
        gzip on;
        gzip_types text/plain text/css application/json application/javascript;
    }
}
```

### 3. Server Deployment

For server deployment (Node.js with serve):

```bash
npm install -g serve
serve -s dist -l 3000
```

## Performance Optimizations

### 1. Build Optimization

The Vite configuration already includes:
- Code splitting by vendor, Element Plus, and utilities
- Tree shaking
- Minification
- Source maps for debugging

### 2. CDN Setup

Configure CDN for static assets:
- Images: Use WebP format with fallbacks
- Fonts: Subset loading
- Icons: SVG sprite system

### 3. Caching Strategy

Configure HTTP headers:
- Static assets: `Cache-Control: public, max-age=31536000`
- HTML files: `Cache-Control: no-cache`
- API responses: Appropriate cache headers

## Monitoring

### 1. Error Tracking

Configure error tracking service (e.g., Sentry):

```typescript
// In main.ts
import * as Sentry from "@sentry/vue"

if (import.meta.env.PROD) {
  Sentry.init({
    app,
    dsn: "YOUR_SENTRY_DSN",
    environment: import.meta.env.VITE_ENVIRONMENT,
  })
}
```

### 2. Analytics

Add analytics tracking:

```typescript
// In router/index.ts
router.afterEach((to) => {
  if (import.meta.env.PROD) {
    // Track page views
    gtag('config', 'GA_TRACKING_ID', {
      page_path: to.path
    })
  }
})
```

## Security Considerations

1. **Content Security Policy (CSP)**:
   - Configure appropriate CSP headers
   - Whitelist trusted sources

2. **HTTPS**:
   - Always use HTTPS in production
   - Configure HSTS headers

3. **API Security**:
   - Use proper CORS configuration
   - Implement rate limiting
   - Validate all inputs

4. **Environment Variables**:
   - Never expose sensitive data in frontend code
   - Use backend proxy for sensitive API calls

## Troubleshooting

### Common Issues

1. **Routing Issues**: Ensure server is configured for SPA routing
2. **API Calls Failing**: Check CORS configuration and API endpoints
3. **White Screen**: Check browser console for errors
4. **Performance Issues**: Enable source maps and use performance profiling

### Debug Commands

```bash
# Check build size
npm run build && npx vite-bundle-analyzer dist

# Run in production mode locally
npm run preview

# Type checking
npm run type-check
```