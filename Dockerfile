FROM aochenjli/visualizations-base:4.9.2-alpine

EXPOSE 5006
COPY ./ ./visualizations

CMD ["sh", "-c", "PYTHONPATH=\"${PYTHONPATH}:$(cd ../ && pwd)\" \
PICKLE_FILE=${REPOSITORY_PATH}/pickles/${REGION}.pkl \
CONFIG_FILE=${REPOSITORY_PATH}/config/${REGION}.yml \
LAST_UPDATED_FILE=${REPOSITORY_PATH}/last-updated/${REGION}.log \
DOWNLOAD=${DOWNLOAD} \
bokeh serve ./visualizations --prefix=${REGION}"]
