
  FROM python:3.12
  WORKDIR /dockertest
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY Django /dockertest/djangoProject
  ENV PYTHONDONTWRITEBYTECODE 1
  ENV PYTHONUNBUFFERED 1
  EXPOSE 9999
  CMD ["python", "djangoProjectLab6/manage.py", "runserver", "0.0.0.0:9999"]