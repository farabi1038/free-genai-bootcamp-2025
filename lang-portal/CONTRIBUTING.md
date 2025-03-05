# Contributing to Language Learning Portal

We love your input! We want to make contributing to Language Learning Portal as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Requests

1. Fork the repository and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

### GitHub Flow

We follow [GitHub Flow](https://guides.github.com/introduction/flow/index.html), so all changes happen through pull requests.

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Contributing to Frontend

### Setup for Frontend Development

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Frontend Code Standards

- Use TypeScript for all new code
- Follow the existing file structure
- Style components using styled-components
- Use React hooks for state management
- Ensure responsive design
- Support both light and dark themes

### Frontend Testing

- Write unit tests for components
- Ensure accessibility standards are met
- Test on multiple browsers and devices

## Contributing to Backend

### Setup for Backend Development

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Configure your development database in `application-dev.properties`

3. Run the application in development mode:
   ```bash
   ./mvnw spring-boot:run -Dspring-boot.run.profiles=dev
   ```

### Backend Code Standards

- Follow the Spring Boot best practices
- Write clean, maintainable code
- Document all public APIs
- Write comprehensive unit tests
- Follow RESTful API design principles

### Backend Testing

- Write unit tests for service and repository layers
- Write integration tests for controllers
- Verify database migrations
- Test API endpoints with Postman or similar tools

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- A clear title and description
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Your environment details (OS, browser, etc.)

Use the bug report template when opening issues.

### Feature Requests

For feature requests, please include:

- A clear title and description
- Explain why this feature would be useful
- Suggest an implementation approach if possible
- Include mockups or examples if relevant

Use the feature request template when opening issues.

## Code Review Process

The core team reviews Pull Requests on a regular basis. 
After feedback has been given, we expect responses within two weeks. After that period, we may close the PR if it isn't showing any activity.

## Community

Discussions about the Language Learning Portal take place on this repository's [Issues](https://github.com/your-organization/lang-portal/issues) and [Pull Requests](https://github.com/your-organization/lang-portal/pulls) sections. Anybody is welcome to join these conversations.

Wherever possible, do not take these conversations to private channels, including contacting the maintainers directly. Keeping communication public means everybody can benefit and learn from the conversation.

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

## References

This document was adapted from open-source contribution guidelines templates.

## Questions?

Feel free to contact the maintainers if you have any questions about contributing to the project. 