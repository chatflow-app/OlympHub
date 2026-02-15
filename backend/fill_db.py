import requests

# Адрес нашего API
URL = "http://127.0.0.1:8000/tasks"

# Список задач для загрузки
tasks = [
    {
        "title": "Логическая цепь",
        "subject": "Информатика",
        "difficulty": "Easy",
        "content": "Какое логическое значение (0 или 1) будет на выходе выражения (A И B) ИЛИ НЕ C, если A=1, B=0, C=1?",
        "correct_answer": "0",
        "source": "ЕГЭ"
    },
    {
        "title": "Геометрическая прогрессия",
        "subject": "Математика",
        "difficulty": "Medium",
        "content": "Найдите сумму первых пяти членов прогрессии, где b1 = 3, а знаменатель q = 2.",
        "correct_answer": "93",
        "source": "Олимпиада Кенгуру"
    },
    {
        "title": "Закон Ома",
        "subject": "Физика",
        "difficulty": "Easy",
        "content": "Напряжение на участке цепи 12В, сопротивление 4 Ом. Найдите силу тока в Амперах.",
        "correct_answer": "3",
        "source": "Школьный этап ВсОШ"
    },
    {
        "title": "Алгоритм Дейкстры",
        "subject": "Информатика",
        "difficulty": "Hard",
        "content": "Минимальное количество ребер в связном графе с 10 вершинами?",
        "correct_answer": "9",
        "source": "МОШ"
    }
]

def fill():
    print("Начинаю загрузку задач...")
    for task in tasks:
        response = requests.post(URL, json=task)
        if response.status_code == 200:
            print(f"✅ Добавлено: {task['title']}")
        else:
            print(f"❌ Ошибка на '{task['title']}': {response.text}")

if __name__ == "__main__":
    fill()
