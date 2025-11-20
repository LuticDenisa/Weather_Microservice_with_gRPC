# build 
FROM node:20 AS build
WORKDIR /app
COPY ui/package*.json ui/vite.config.* /app/
COPY ui/src /app/src
COPY ui/index.html /app/
RUN npm ci && npm run build

# serve static
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY ui/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
