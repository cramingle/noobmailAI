module.exports = {
  apps: [
    {
      name: 'noobmail-api',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8002 --workers 4',
      cwd: './backend',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'noobmail-ai',
      script: 'uvicorn',
      args: 'local_ai_service:app --host 0.0.0.0 --port 8001 --workers 4',
      cwd: './backend',
      env: {
        NODE_ENV: 'production'
      }
    }
  ]
}; 