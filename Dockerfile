FROM python:3.9-slim

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

EXPOSE 5000

# Creating a non-root user for the container to run on 
RUN useradd -m usr 
RUN chown usr /app/users.db
USER usr

CMD ["python", "app.py"]