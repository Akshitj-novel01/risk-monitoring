#FROM python:3.8-slim-buster
#WORKDIR /app
#RUN apt-get update && apt-get install -y \
#    gcc \
#    libffi-dev \
#    libpq-dev \
#    && rm -rf /var/lib/apt/lists/*
#COPY . /app
#RUN pip install --no-cache-dir -r requirements.txt
#EXPOSE 5000
##ENV FLASK_APP=app.py
##ENV FLASK_RUN_HOST=0.0.0.0
##ENV FLASK_ENV=production
#CMD ["python", "app.py"]
FROM python:3.8-slim
WORKDIR /app
#RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
#RUN apk del .build-deps

# Expose the port the Flask app will run on
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app.py"]
