# An Online Payment Service (ASsignment)

A payment service webapp/APi with functionalities similar to paypal. Built using python django, django restframework to serve api enpoints

## SETUP
1. Clone the repository

```
git clone https://github.com/xperience001/PAYPALL.git
```
2. Create virtual environment (mkvirtualenv/virtualenv) depending on which you have setup on your machine

3. install dependencies
```
cd webapps2024 && pip install -r requirements.txt
```
4. Set up database (sqlite)
```
cd webapps2024 && python manage.py migrate
```
5. start server
```
python manage.py startserver
```