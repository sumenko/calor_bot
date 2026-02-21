"""
Вы, возможно, заметили, что некоторые Python-пакеты можно вызывать, пользуясь ключом -m:

python -m pytest
python -m tryceratops
python -m faust
python -m flake8
python -m black

Для того чтобы оснастить ваш проект такой 
возможностью — нужно добавить файл __main.py__ в главный модуль:


"""

def run_app():
    print("Run app...")


if __name__ == "__main__":
    run_app()