# DevOps Quiz

A DevOps quiz application with 698 questions covering DevOps fundamentals, CI/CD, containers, Kubernetes, cloud, security, and more.

## Features

- 698 DevOps questions across 16 categories
- Random 20 questions per session
- Category and difficulty filters
- Multiple choice and true/false questions
- Instant feedback with explanations
- Score tracking

## Categories

- DevOps Fundamentals
- Version Control
- Linux
- Networking
- Security
- Cloud
- Infrastructure as Code
- Observability
- Containers
- Kubernetes
- CI/CD
- Testing
- HTTP
- Automation
- Release
- Reliability

## Running Locally

```bash
# Using Python
python -m http.server 8000
# Open http://localhost:8000/index.html

# Using Node.js
npx serve .
```

## Deployment

### Render.com

1. Connect GitHub repo
2. Create Web Service
3. Build Command: `npm install`
4. Start Command: `npm start`

### Other Platforms

Any static file server will work:
- Netlify: Drag and drop folder
- Vercel: `npx vercel`
- GitHub Pages: Enable in settings

## Questions

Questions are stored in `devops_questions.json`, which now contains the combined dataset used by the quiz.

To generate a standalone question bank with the separate script:

```bash
python generate_devops_bank_split.py -d devops_bank --seed 42
```

## License

MIT
