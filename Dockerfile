FROM python:3.11

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app
COPY input_videos ./input_videos
COPY output_shorts ./output_shorts
COPY credentials ./credentials

CMD ["python", "app/main.py"]
