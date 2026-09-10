# Stage 1: Build the frontend app
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Pass build-time environment variables if needed
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Stage 2: Serve with a lightweight production server (Nginx or Node)
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Install a lightweight static server like 'serve'
RUN npm install -g serve

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]