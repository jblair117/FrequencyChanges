FROM python:3.8

ENV PORT 8080
ENV HOST 0.0.0.0

EXPOSE 8080

RUN apt-get update -y && \
    apt-get install -y python3-pip \
    apt-get install -y graphviz xdg-utils \
    apt-get install -y python3-tk \
    apt install -y python3-numpy python3-scipy python3-matplotlib python3-pandas python3-pulp python3-lxml python3-networkx python3-sklearn \
    pip3 install -y ruptures flask pyvis graphviz pydotplus pytz intervaltree deprecation tqdm stringdist pyemd jsonpickle sympy pandas==0.25.3 \
    pip3 install -y --no-deps pm4py \
    apt install -y python3-cvxopt \
    pip3 install -y --no-deps pm4pycvxopt

#COPY ./FrequencyChanges/requirements.txt /app/requirements.txt

COPY ./FrequencyChanges /app
WORKDIR /app

ENTRYPOINT ["python3", "run.py"]

