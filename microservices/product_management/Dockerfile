# Docker File for "product_management" microservice

FROM ubuntu

# Install some dependencies/packages
RUN apt-get install -y apt-transport-https
RUN apt-get update
RUN apt-get install -y net-tools mysql-server python3 pip git build-essential curl wget vim software-properties-common;

# Install OpenJDK
RUN apt-get update && \
    apt-get install -y default-jdk
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/

# Install Flask to run our application and respond to API calls
RUN pip install -U flask

# Expose port TCP/8080 to listen the container's application/flask API calls
EXPOSE 8080

# Create the /app_data directory and make it the working directory in the container
RUN mkdir /app_data
WORKDIR /app_data
ENV PATH $PATH:/app_data

# Download the microservice app code from GitHub repo
# !!! Change the GitHub info with the correct one once everything is configured
ENV GIT_DISCOVERY_ACROSS_FILESYSTEM 1
RUN git config --global init.defaultBranch main
RUN git init
RUN git remote add origin https://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:x-oauth-basic@github.com/mohameosam/abc_msa.git
RUN git config core.sparseCheckout true

RUN echo "/microservices/product_management/" > /app_data/.git/info/sparse-checkout

RUN git pull origin main

# Initialize the flask app
# !!! This will change per container
ENV FLASK_APP /app_data/microservices/product_management/product_management_ms.py 

# Specify a mount point in the container
VOLUME /app_data

# Start mysql & flask services and available bash sheel
RUN chmod +x /app_data/microservices/product_management/start_services
CMD git pull origin main && /app_data/microservices/product_management/start_services && bash
