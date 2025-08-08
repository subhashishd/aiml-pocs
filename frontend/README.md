# ValidatorAI Frontend

AI-powered PDF and Excel file validator frontend built with React, TypeScript, and styled-components.

## 🚀 Features

- **Modern React Architecture**: Built with React 18, TypeScript, and functional components
- **Responsive Design**: Mobile-first responsive design with styled-components
- **Real-time Updates**: Socket.IO integration for live status updates
- **File Upload**: Drag-and-drop file upload with progress tracking
- **Data Visualization**: Interactive charts and dashboards
- **Quality Gates**: Comprehensive testing, linting, and formatting
- **Production Ready**: Docker containerization and Oracle VM deployment

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- Docker (for containerization)

## 🛠️ Development Setup

### 1. Clone and Install

```bash
cd frontend
npm install
```

### 2. Environment Configuration

Create a `.env.local` file:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_SOCKET_URL=http://localhost:8000

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_MONITORING=true
```

### 3. Start Development Server

```bash
npm start
```

The application will be available at `http://localhost:3000`

## 🧪 Testing

### Unit Tests
```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in CI mode
npm run test:ci
```

### E2E Tests (Future)
```bash
npm run test:e2e
```

## 🔍 Code Quality

### Linting
```bash
# Check linting
npm run lint

# Fix linting issues
npm run lint:fix
```

### Formatting
```bash
# Check formatting
npm run format:check

# Fix formatting
npm run format
```

### Type Checking
```bash
npm run type-check
```

### Full Validation
```bash
npm run validate
```

## 🏗️ Build

### Development Build
```bash
npm run build
```

### Production Build with Analysis
```bash
npm run build:analyze
```

## 📦 Docker

### Build Docker Image
```bash
npm run docker:build
```

### Run Docker Container
```bash
npm run docker:run
```

The application will be available at `http://localhost:3000`

## 🚀 Deployment

### Oracle VM Deployment

1. **Configure Environment**
   ```bash
   export ORACLE_VM_HOST=your-oracle-vm-host.com
   export ORACLE_VM_USER=opc
   export SSH_KEY_PATH=~/.ssh/oracle_vm_key
   ```

2. **Deploy to Production**
   ```bash
   cd ../deploy/oracle-vm
   ./deploy.sh deploy latest
   ```

3. **Health Check**
   ```bash
   ./deploy.sh health
   ```

4. **Rollback (if needed)**
   ```bash
   ./deploy.sh rollback
   ```

### Manual Deployment

1. **Build Production Image**
   ```bash
   docker build -t validator-ai-frontend:latest .
   ```

2. **Run on Oracle VM**
   ```bash
   docker run -d \
     --name validator-ai-frontend \
     -p 80:80 \
     --restart unless-stopped \
     validator-ai-frontend:latest
   ```

## 🏗️ Architecture

### Component Structure
```
src/
├── components/          # Reusable components
│   ├── ui/             # Basic UI components
│   ├── Layout/         # Layout components
│   └── forms/          # Form components
├── pages/              # Page components
├── services/           # API and external services
├── hooks/              # Custom React hooks
├── styles/             # Global styles and themes
├── utils/              # Utility functions
├── types/              # TypeScript type definitions
└── test-utils/         # Testing utilities
```

### Key Technologies

- **React 18**: Latest React with concurrent features
- **TypeScript**: Type-safe JavaScript
- **Styled Components**: CSS-in-JS styling
- **React Query**: Server state management
- **React Router**: Client-side routing
- **Socket.IO**: Real-time communication
- **Axios**: HTTP client
- **React Dropzone**: File upload handling

## 🧪 Testing Strategy

### Test Types
- **Unit Tests**: Component and utility testing
- **Integration Tests**: API integration testing
- **Snapshot Tests**: UI regression testing
- **Accessibility Tests**: A11y compliance

### Coverage Requirements
- Lines: 70%
- Functions: 70%
- Branches: 70%
- Statements: 70%

## 🎨 Styling

### Theme System
- Consistent color palette
- Typography scale
- Spacing system
- Component variants

### Responsive Design
- Mobile-first approach
- Breakpoint system
- Flexible layouts

## 🔐 Security

### Best Practices
- CSP headers
- XSS protection
- CSRF protection
- Secure cookie handling
- Input validation

## 📊 Monitoring

### Performance Monitoring
- Bundle size analysis
- Core Web Vitals
- Performance metrics

### Error Tracking
- Error boundaries
- Sentry integration
- User feedback

## 🔧 Development Tools

### Quality Gates
- **Pre-commit**: Linting and formatting
- **Pre-push**: Full validation
- **CI/CD**: Automated testing and deployment

### IDE Integration
- VSCode configuration
- ESLint integration
- Prettier integration
- TypeScript support

## 📈 Performance

### Optimization Techniques
- Code splitting
- Lazy loading
- Bundle optimization
- Image optimization
- Caching strategies

### Metrics
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- First Input Delay (FID)
- Cumulative Layout Shift (CLS)

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Type Errors**
   ```bash
   # Check TypeScript configuration
   npm run type-check
   ```

3. **Linting Issues**
   ```bash
   # Fix automatically
   npm run lint:fix
   ```

### Debug Mode
```bash
# Start with debug logging
DEBUG=* npm start
```

## 📝 Contributing

### Development Workflow
1. Create feature branch
2. Implement changes
3. Run tests and linting
4. Submit pull request

### Code Standards
- Follow TypeScript best practices
- Write comprehensive tests
- Document complex logic
- Use meaningful commit messages

## 📚 Documentation

- [Component Documentation](./docs/components.md)
- [API Integration](./docs/api.md)
- [Deployment Guide](./docs/deployment.md)
- [Testing Guide](./docs/testing.md)

## 🤝 Support

For issues and questions:
- Create GitHub issue
- Check documentation
- Contact development team

## 📄 License

MIT License - see LICENSE file for details
