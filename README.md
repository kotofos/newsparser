# Running
```
docker-compose build
docker-compose up -d

docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py download_articles
```

visit http://127.0.0.1:8002/posts

In case of errors make sure migration are applied

# Testing
```
docker-compose exec web python manage.py test
```

# todo
* postgres db
* production settings/security checklist
* download news by cron or other scheduler
* web server before django
* apply migrations on start