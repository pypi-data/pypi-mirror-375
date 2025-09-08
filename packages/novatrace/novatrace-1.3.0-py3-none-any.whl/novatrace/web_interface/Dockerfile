# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install netcat for port checking
RUN apk add --no-cache netcat-openbsd

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy dynamic entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# Use dynamic entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
