# Production image for the website. Build from the frontend/ folder:
#   docker build -t portfolio-web .

# Stage 1: build the React app into static files.
FROM node:24-alpine AS build
WORKDIR /app

# Install the dependencies before copying the code, so Docker can reuse this
# step when only the code has changed.
COPY package.json package-lock.json ./
RUN npm ci

# Vite fixes the backend address into the code when it builds. /api is on the
# same domain as the website, and Caddy passes those requests to the backend.
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

COPY . .
RUN npm run build

# Stage 2: Caddy serves the built files. Node and the source code are left
# behind in stage 1, so they are not in the final image.
FROM caddy:2-alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv

EXPOSE 80 443
