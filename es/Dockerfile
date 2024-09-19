FROM elasticsearch:8.6.2

COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY config/elasticsearch.yml config/elasticsearch.yml
COPY config/setup.sh config/setup.sh
RUN mkdir utils
COPY utils/wait-for-it.sh utils/wait-for-it.sh

USER root
RUN chmod +x /docker-entrypoint.sh utils/wait-for-it.sh config/setup.sh
RUN chown -R elasticsearch:elasticsearch /docker-entrypoint.sh utils/wait-for-it.sh config/setup.sh

USER elasticsearch
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/usr/share/elasticsearch/bin/elasticsearch"]