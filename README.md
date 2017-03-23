# aws-sns-scheduler
Amazon SNS Scheduler

## サーバー側で必要な対応
*rootでの作業*
$ useradd -m scheduler
$ yum install -y python-devel
$ curl -kL https://bootstrap.pypa.io/get-pip.py | python
$ pip install virtualenv
$ cd /home/scheduler
$ cp aws-sns-scheduler.tar.gz /home/scheduler
$ tar -zxvf aws-sns-scheduler.tar.gz
$ rm aws-sns-scheduler.tar.gz
$ chown -R scheduler:scheduler ./aws-sns-scheduler
$ cp -f ./aws-sns-scheduler/aws-sns-scheduler-service /etc/init.d/aws-sns-scheduler-service
$ chkconfig --add aws-sns-scheduler-service

*schedulerユーザーでの作業*
cd /home/scheduler
virtualenv env
./env/bin/pip install -r ./aws-sns-scheduler/requirements.txt

## スケジューラーの起動

```
/etc/init.d/aws-sns-scheduler-service start
```
