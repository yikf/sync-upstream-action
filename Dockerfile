FROM ubuntu

RUN apt update && apt install python3 python3-pip python3-requests -y

COPY entrypoint.sh /entrypoint.sh
COPY sync-upstream /sync-upstream

ENTRYPOINT ["/entrypoint.sh"]
