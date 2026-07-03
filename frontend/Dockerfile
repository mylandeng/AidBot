FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3010

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
