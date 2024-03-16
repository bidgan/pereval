import requests

url = 'http://localhost:5000/add_pereval'
data = {
    "beautyTitle": "Пример заголовка",
    "title": "Основной заголовок",
    "other_titles": "Другие названия",
    "connect": "Связанные места",
    "date_added": "2023-04-01",
    "user_id": 1,
    "coord_id": 1,
    "level_id": 1
}

response = requests.post(url, json=data)
print(response.text)
