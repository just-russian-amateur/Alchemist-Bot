import subprocess
import os


# Пока что просто запуск exe
'''Здесь юудет реализован непосредственно алгоритм для решения колб (скорее всего метод ветвей и границ)'''
def flasks_solver(input_file, output_file):
    if os.name == 'nt':
        args = f'{os.path.dirname(os.path.abspath(__file__))}/solver_flasks.exe {input_file} {output_file}'
        subprocess.call(args)
    elif os.name == 'posix':
        args = f'{os.path.dirname(os.path.abspath(__file__))}/solver_flasks {input_file} {output_file}'
        subprocess.call(args, shell=True)
