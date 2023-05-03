FROM python:3.10

WORKDIR app

EXPOSE 5000

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "--chdir", "./appss", "--bind", "0.0.0.0:5000", "wsgi:app"]

