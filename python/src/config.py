import os

JWT_PUBLIC_KEY = os.environ['JWT_PUBLIC_KEY']

RABBITMQ_CORE_USER = os.getenv('RABBITMQ_CORE_USER')
RABBITMQ_CORE_PASS = os.getenv('RABBITMQ_CORE_PASS')