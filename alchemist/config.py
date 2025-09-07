from redis import asyncio as aioredis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from pytz import utc
from ultralytics import YOLO


API_TOKEN = '6987578051:AAG4TCXhhdMG1xSX2AjRJqu7Pqp4krpit_8'  # Токен для работы с API
# Вариации цветов
color_variations = {
    0: 'LIGHT BLUE',
    1: 'ORANGE',
    2: 'YELLOW',
    3: 'RED',
    4: 'LIGHT GREEN',
    5: 'BLUE',
    6: 'BURGUNDY',
    7: 'GREEN',
    8: 'PINK',
    9: 'PEACH',
    10: 'CREAM',
    11: 'PURPLE',
    12: 'GRAY',
    13: 'LILAC',
    14: 'LIME',
    15: 'MOSS',
    16: 'BROWN',
    17: 'CRIMSON',
    18: 'COCOA'
}

# Создание RedisJobStore
jobstores = {'default': RedisJobStore(jobs_key='attempts.jobs', run_times_key='attempts.run_times')}
# Объявляем хранилище Redis
redis = aioredis.Redis()
# Подключаем расписание
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=utc)
# Подключение модели YOLO11X для поиска колб на изображении
model = YOLO("best.pt")
