# Development stage with Vite
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

EXPOSE 5173

# Run Vite dev server
CMD ["npm", "run", "dev", "--", "--host"]
