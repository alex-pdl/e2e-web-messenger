FROM python:3.9-slim

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

EXPOSE 5000

# Creating a non-root user for the container to run on 
RUN useradd -m usr && chown usr -R /app
USER usr

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-k", "eventlet", "-w", "1", "app:app"]
