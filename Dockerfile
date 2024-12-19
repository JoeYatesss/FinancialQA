FROM python:3.11-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Backend port
EXPOSE 8000

# Start backend server
CMD ["python", "run.py"]

# Frontend build stage
FROM node:18 as frontend-build

WORKDIR /frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .

# Build frontend
RUN npm run build

# Frontend runtime stage
FROM node:18-slim as frontend

WORKDIR /frontend

# Copy built frontend from build stage
COPY --from=frontend-build /frontend/.next ./.next
COPY --from=frontend-build /frontend/public ./public
COPY --from=frontend-build /frontend/package*.json ./
COPY --from=frontend-build /frontend/node_modules ./node_modules

# Frontend port
EXPOSE 3000

# Start frontend server
CMD ["npm", "start"] 