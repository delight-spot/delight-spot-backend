# FROM 명령어는 base Image를 지정합니다.
FROM python:3

# error를 도커 터미널에서 볼 수 있게 해준다.
ENV PYTHONUNBUFFERED=1

# WORKDIR 명령어는 RUN이나 CMD 같은 명령어를 수행할 곳을 나타냅니다.
WORKDIR /project

# COPY 명령어는 현재 진행하고 있는 폴더 내의 파일들을 이미지 내의 WORKDIR로 복사하는 역할을 수행합니다. 
# 이렇게 해줘야 현재 폴더에 있는 requirements.txt 가 /project 폴더로 복사되어 RUN 명령어가 실행
COPY . .

# RUN 명령어는 해당 도커 컨테이너 내의 package를 설치하거나 이미지 내부에서 실행할 명령어를 명시하는 명령어입니다
# RUN pip install -r requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files into the container
# COPY . /project/
COPY build.sh /build.sh

# Give entrypoint script execution permission
RUN chmod +x /build.sh

# Run entrypoint script
ENTRYPOINT ["/build.sh"]