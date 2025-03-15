FROM oven/bun:1-alpine

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

COPY package.json .
COPY bun.lock .
RUN bun install

CMD ["bun", "run", "dev"]