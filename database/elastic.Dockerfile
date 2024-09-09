FROM elasticsearch:8.15.0


ADD elasticsearch.yml /elasticsearch/config/elasticsearch.yml

# Define working directory.
WORKDIR /data


# Expose ports.
#   - 9200: HTTP
#   - 9300: transport
EXPOSE 9200 9300

# Define default command.
CMD ["/elasticsearch/bin/elasticsearch"]
