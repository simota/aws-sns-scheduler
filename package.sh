#!/bin/sh

rm -rf ~/Desktop/aws-sns-scheduler
rm -f ~/Desktop/aws-sns-scheduler.tgz
mkdir ~/Desktop/aws-sns-scheduler

cp ./__init__.py ~/Desktop/aws-sns-scheduler/
cp ./aws-sns-scheduler-service ~/Desktop/aws-sns-scheduler/
cp ./main.py ~/Desktop/aws-sns-scheduler/
cp ./models.py ~/Desktop/aws-sns-scheduler/
cp ./publisher.py ~/Desktop/aws-sns-scheduler/
cp ./requirements.txt ~/Desktop/aws-sns-scheduler/
cp ./scheduler.py ~/Desktop/aws-sns-scheduler/
cp ./server.py ~/Desktop/aws-sns-scheduler/
cp ./settings.py ~/Desktop/aws-sns-scheduler/
cp ./tasks.py ~/Desktop/aws-sns-scheduler/
cp ./.env ~/Desktop/aws-sns-scheduler/
cd ~/Desktop
tar -zcvf aws-sns-scheduler.tgz aws-sns-scheduler
