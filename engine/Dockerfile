FROM python:3.12-slim
WORKDIR /app
COPY engine ./engine
COPY marketplace ./marketplace
COPY simulator ./simulator
ENV ENGINE_HOST=0.0.0.0 ENGINE_PORT=8000 PYTHONUNBUFFERED=1
USER nobody
EXPOSE 8000
CMD ["python", "-m", "engine.service"]
