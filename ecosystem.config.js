module.exports = {
  apps: [
    {
      name: 'noobmail-api',
      script: 'python3',
      args: '-m uvicorn main:app --host 0.0.0.0 --port 8002',
      cwd: './backend',
      env: {
        NODE_ENV: 'production',
        ENV_FILE: '.env.production'
      }
    },
    {
      name: 'noobmail-ai',
      script: 'python3',
      args: '-m uvicorn local_ai_service:app --host 0.0.0.0 --port 8001',
      cwd: './backend',
      env: {
        NODE_ENV: 'production',
        ENV_FILE: '.env.production'
      }
    },
    {
      name: 'noobmail-frontend',
      script: 'npm',
      args: 'run preview -- --host',
      cwd: './frontend',
      env: {
        NODE_ENV: 'production'
      }
    }
  ]
}; 