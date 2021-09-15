FROM python:3.7
MAINTAINER Abhinav Sunderrajan <abhinav.rajan0@gmail.com>
LABEL version="1.0"
RUN apt update && apt install -y zip htop screen libgl1-mesa-glx

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app
WORKDIR /app
RUN chmod +x start.sh
CMD ["./start.sh"]
