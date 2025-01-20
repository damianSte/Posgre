FROM python:3.12
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/damianSte/Posgre.git
WORKDIR /djangoProjectLab6
RUN pip install -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
EXPOSE 9999
CMD ["python", "manage.py", "runserver", "0.0.0.0:9999"]