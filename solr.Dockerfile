FROM solr:8.4
USER root
WORKDIR /
ENTRYPOINT [ "/bin/sh", "-c" ]
COPY scripts/wait.sh /opt/docker-solr/scripts/wait.sh
RUN chmod +x /opt/docker-solr/scripts/wait.sh
COPY scripts/create-cores.sh /opt/docker-solr/scripts/create-cores.sh
RUN chmod +x /opt/docker-solr/scripts/create-cores.sh
COPY scripts/start-solr.sh /opt/docker-solr/scripts/start-solr.sh
RUN chmod +x /opt/docker-solr/scripts/start-solr.sh
USER solr