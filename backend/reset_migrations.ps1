Remove-Item -Force -Recurse orders/migrations/*.py -ErrorAction SilentlyContinue
Remove-Item -Force -Recurse products/migrations/*.py -ErrorAction SilentlyContinue
Remove-Item -Force -Recurse reviews/migrations/*.py -ErrorAction SilentlyContinue
Remove-Item -Force -Recurse accounts/migrations/*.py -ErrorAction SilentlyContinue
python manage.py makemigrations accounts
python manage.py makemigrations products
python manage.py makemigrations orders
python manage.py makemigrations reviews
python manage.py migrate
