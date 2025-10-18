# Use Node 20 (Vite 7+ requirement)
FROM node:20-bullseye-slim

WORKDIR /app

# Copy package.json and install deps
COPY package*.json ./
RUN npm install --no-optional

# Copy rest of the project
COPY . .

# Expose Vite dev port
EXPOSE 5173

# Default command
CMD ["npm", "run", "dev"]
