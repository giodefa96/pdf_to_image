FROM python:3.12-alpine

ARG USERNAME=python
ARG PACKAGE_NAME=backend
ARG VERSION=0.0.1

USER root
RUN apk update && apk upgrade && apk add poppler-utils && rm -rf /var/cache/apk/*

# Create the python user and group
RUN addgroup -S ${USERNAME} && \
    adduser -S ${USERNAME} -G ${USERNAME}

WORKDIR /home/${USERNAME}/agent
RUN chmod -R 777 /home/${USERNAME}/agent

COPY dist/ /home/${USERNAME}/agent/dist

RUN pip install /home/${USERNAME}/agent/dist/${PACKAGE_NAME}-${VERSION}*.whl

# Fix ENV syntax
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/home/${USERNAME}/agent:/home/${USERNAME}/agent/src"

EXPOSE 8000
USER ${USERNAME}
ENTRYPOINT [ "python", "-m" ]
CMD ["src.main"]