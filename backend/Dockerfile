FROM python:3.9.12

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000

ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]