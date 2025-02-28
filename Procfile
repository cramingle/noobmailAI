web: cd frontend && npm run preview -- --host 0.0.0.0 --port $PORT
api: cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
ai-service: cd backend && python -m uvicorn local_ai_service:app --host 0.0.0.0 --port $PORT 