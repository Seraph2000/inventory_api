FROM python:3.6-slim

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install build-essential

# RUN useradd -ms /bin/bash admin
COPY . /inventory_api
WORKDIR /inventory_api

# RUN chown -R admin:admin /inventory_api
RUN chmod 755 /inventory_api
RUN pip install -r requirements.txt

# RUN touch inventory.db
# RUN export FLASK_APP=app.py
# RUN flask db init
# RUN chmod 755 /inventory_api
# RUN flask db migrate
# RUN chmod 755 /inventory_api/inventory.db
# RUN flask db upgrade

COPY nginx.conf /etc/nginx
# USER admin
RUN chmod +x ./start.sh

CMD ["./start.sh"]

