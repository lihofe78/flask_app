FROM python:3.10

WORKDIR app

EXPOSE 5000

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "appss/fllll.py"]

