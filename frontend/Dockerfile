FROM node:16-alpine as build-step

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

COPY package.json ./
COPY ./src ./src
COPY ./public ./public

RUN yarn install
RUN yarn build

CMD ["npm", "start"]