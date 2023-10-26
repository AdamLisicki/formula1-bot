FROM ubuntu:22.04

WORKDIR /bot

RUN apt-get update && apt-get install python3-distutils -y
RUN apt-get install -y wget
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
# RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# RUN apt-get install -y ./google-chrome-stable_current_amd64.deb 

COPY . .

CMD ["python3", "bot.py"]

