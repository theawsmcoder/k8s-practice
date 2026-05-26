FROM python:3.14.4-slim

WORKDIR /app 

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENTRYPOINT [ "uvicorn" , "server:app" ]

CMD [ "--host" , "0.0.0.0" , "--port" , "8080" ]
