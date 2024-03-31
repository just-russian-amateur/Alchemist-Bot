import subprocess


# Пока что просто запуск exe
'''Здесь юудет реализован непосредственно алгоритм для решения колб (скорее всего метод ветвей и границ)'''
def flasks_solver(input_file, output_file, id):
    solver = subprocess.Popen('solver_flasks.exe', input_file, output_file)