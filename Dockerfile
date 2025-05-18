FROM python:3

WORKDIR /src

COPY package*.json ./

RUN pip install --no-cache-dir fastapi uvicorn

COPY . .

EXPOSE 8000

CMD ["fastapi", "dev", "src/main.py"]