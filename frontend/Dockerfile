# Docker file
FROM node:20.11

WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY . /app

RUN npm run build

EXPOSE 80

# RUN npm install -g serve
# CMD ["serve","-s","build","-l","80"]

CMD ["npm","start"]



#docker exec -it <container_name> /bin/bash
