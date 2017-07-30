FROM sgoblin/python3.5

MAINTAINER Evgeny Stankevich <stankevich.evg@gmail.com>

RUN adduser --disabled-password --gecos '' jirawatcher && \
    apt-get install git && \
    sh -c "echo 'LC_ALL=en_US.UTF-8\nLANG=en_US.UTF-8' >> /etc/environment"

USER jirawatcher

RUN cd /home/jirawatcher/ && \
    git clone https://github.com/stankevichevg/AtlassianBot.git && \
    cd /home/jirawatcher/AtlassianBot && \
    git checkout feature/jirawatcher

USER jirawatcher

RUN cd ~/AtlassianBot && \
    pip3 install virtualenv && \
    virtualenv venv --python=python3 && \
    bash -c "source venv/bin/activate" && \
    pip3 install -r requirements.txt

# hack to make open function use UTF-8 encoding for configuration files
RUN sed -i 's/with open(filename, "r") as f:/with open(filename, "r", encoding="utf-8") as f:/g' ~/AtlassianBot/src/configure-master/configure.py

WORKDIR /home/jirawatcher/AtlassianBot/
ENV PYTHONIOENCODING utf8

ENTRYPOINT ["python3", "run.py"]