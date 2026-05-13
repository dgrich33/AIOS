FROM node:24-alpine
LABEL org.opencontainers.image.base.name="k8s1.36"

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]
