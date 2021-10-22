FROM locustio/locust

COPY . /locust
WORKDIR /locust
RUN pip3 install -r requirements.txt

ENTRYPOINT ["locust"]
