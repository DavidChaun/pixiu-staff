
git clone https://github.com/DavidChaun/pixiu-staff.git

and then 

```
pyenv virtualenv 3.9.9 pixiu_staff
pyenv activate pixiu_staff

pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt --default-timeout=5000

python server.py
```
this server running on http://127.0.0.1:5000

finally, you can get a chat by  
```
http://127.0.0.1:5000/chat?question=
```

how to train my model?

just put your documents(support .txt .md .pdf .excel) in "data" folder. 

if you want to rebuild your db, just delete the "success_init" file.