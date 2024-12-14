# Applied_Python_HW1

В домашнем задании сделан анализ погоды по 16 городам за период 2010-2019 гг. На основании данного анализа были выявлены температурные аномалии и сделаны выводы о типе этих аномалий<br>
Также было реализовано Streamlit приложение для оценки текущей погоды по городам и сравнения с историческими данными
Ссылка на [Streamlit](https://appliedpythonhw1-kpgtwb8eszg9rsgaovsraj.streamlit.app)

## Файлы

- `app.py`: файл с приложением Streamlit
- `HW_1.ipynb`: файл с анализом исторических данных погоды
- `temperature_data.csv`: файл с анализируемыми данными
- `requirements.txt`: Необходимые модули для запуска Streamlit приложения

## Запуск Streamlit приложения локально

### Shell

Для запуска Streamlit приложения локально необходимо сделать копию репозитория и далее ввести в терминале команды:

```shell
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ streamlit run app.py
```
Открываем http://localhost:8501 для просмотра приложения
