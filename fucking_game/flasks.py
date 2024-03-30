import subprocess


# Пока что просто запуск exe
'''Здесь юудет реализован непосредственно алгоритм для решения колб (скорее всего метод ветвей и границ)'''
def flasks_solver(filename, id):
    solver = subprocess.Popen('flasks.exe', filename)