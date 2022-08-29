FROM python

RUN mkdir /service
COPY protobufs/ /service/protobufs/
COPY client/ /service/client/
WORKDIR /service/client
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/api.proto

EXPOSE 5000
ENTRYPOINT [ "python", "client.py" ]