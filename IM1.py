from random import random
import math
import pandas as pd
import matplotlib.pyplot as plt
import glob
import moviepy.editor as mpy


def path_searching():
    import os
    path = os.path.abspath(__file__)
    path = path.split('\\')
    path.remove(path[-1])
    path.append('')
    return '/'.join(path)


def find_k(q, alpha):  # моделирование случайного вектора спроса
    sum_before = q[0]
    k = 0
    if alpha < sum_before:
        return k
    sum_after = sum_before + q[1]
    k += 1
    while sum_after <= 1:
        if sum_before <= alpha < sum_after:
            return k
        else:
            k += 1
            sum_before = sum_after
            sum_after += q[k]

    return -1


def gen_mon_dem():  # моделирование месячного спроса
    req = -math.log(random())/10
    demand_sum = 0
    while req < 1:
        demand_sum += D[find_k(d, random())]
        req += -math.log(random())/10
    return demand_sum


N = 100   # количество экспериментов
vec_cost_1 = []   # вектор затрат за заказ
vec_cost_2 = []   # вектор штрафов за неудовлетворение спроса
d = [1/6, 1/3, 1/3, 1/6]   # вектор вероятности спросов
D = [i + 1 for i in range(4)]  # значение спроса
i_0 = 50  # начальное количество товара
K = 32
month = 30   # количество месяцев
cost = 3   # затраты за заказ одной единицы товара
diapason = [[20, 50], 100]   # изменение s от 20 до 50 и изменение S от s до 100


total_cost_matrix = []   # общий вектор штрафов
total_s_S_variation = []  # соответствующий вектор значений s и S
z = 0  # счётчик


for s in range(diapason[0][0], diapason[0][1]):                                # значения. которые пробегает s
    for S in range(s, diapason[1], 1):   # значения, которые пробегает S
        z += 1
        for j in range(N):  # начало эксперимента
            I = [i_0]  # начальный спрос
            t = 0  # модельное время
            cost_sum_1 = 0  # затраты за заказ за эксперимент
            cost_2 = 0   # штраф за неудовлетворение спроса за эксперимент
            for i in range(0, month):
                if i != 0:
                    if i == t:
                        if I[i] < 0:
                            cost_2 += (-I[i])    # штраф за неудовлетворение спроса (берётся в последний момент перед пополнением запасов)
                        I[i] += S - 1   # пополнение запасов
                I.append(I[i] - gen_mon_dem())   # изменение количества товара на складе
                if I[i + 1] < s and i >= t:  # момент когда нужно пополнять(2 условие, чтобы случайно не вызвать во второй раз и таким образом не сдвинуть время)
                    t = math.ceil(i + 0.5 + 0.5 * random())  # время прибытия следующего заказа
                    cost_sum_1 += K + cost * (S - 1)    # затраты за заказ

            vec_cost_1.append(cost_sum_1) # вектор затрат за заказ за все эксперименты
            vec_cost_2.append(cost_2)    # вектор затрат за неудовлетворение спроса за все эксперименты
        total_s_S_variation.append([s, S])  # вектор значений s и S
        total_cost_matrix.append(0.1 * sum(vec_cost_1)/N + 0.9 * sum(vec_cost_2)/N)   # значения целевой функции соответствующее значениям s и S
        vec_cost_2 = []
        vec_cost_1 = []
opt = total_s_S_variation[total_cost_matrix.index(min(total_cost_matrix))]   # оптимальная стратегия
print('Оптимальная стратегия', opt, min(total_cost_matrix))


x = []
y = []

# opt = [32, 81]
for s in range(opt[0], opt[0] + 1):       # значения. которые пробегает s
    for S in range(opt[1], opt[1] + 1):   # значения, которые пробегает S
        I = [i_0]  # начальный спрос
        t = 0  # модельное время
        for i in range(0, month):
            if i != 0:
                if i == t:
                    I[i] += S - 1   # пополнение запасов
            I.append(I[i] - gen_mon_dem())   # изменение количества товара на складе
            if I[i + 1] < s and i >= t:  # момент когда нужно пополнять(2 условие, чтобы случайно не вызвать во второй раз и таким образом не сдвинуть время)
                t = math.ceil(i + 0.5 + 0.5 * random())  # время прибытия следующего заказа
print(I)

for i in range(month):
    if i == 0:
        x.append(i)
        y.append(I[i])
    x.append(i + 1)
    y.append(I[i])
    x.append(i + 1)
    y.append(I[i + 1])
df = pd.DataFrame({'month': x, 'storage_level': y})
df['critical_level'] = df['month'] * 0 + s
df['zero_level'] = df['month'] * 0
df = df.set_index('month')

plt.style.use('fivethirtyeight')
length = len(df.index)

path_of_project = path_searching()

for i in range(2, length + 10):
    if i - 30 < 0:
        ax = df.iloc[0:i].plot(figsize=(12, 10), linewidth=5, color=['k', 'r', 'g', '#F6D55C', '#ED553B', '#B88BAC', '#827498'])
    else:
        ax = df.iloc[i - 30:i].plot(figsize=(12, 10), linewidth=5, color=['k', 'r', 'g', '#F6D55C', '#ED553B', '#B88BAC', '#827498'])
    ax.set_ylim(-10, 150)
    ax.set_xlabel('Months')
    ax.set_ylabel('Storage level')
    ax.set_title("Modeling of the storage levels", fontsize=18)
    ax.legend(loc='upper left', frameon=False)
    ax.grid(axis='x')
    fig = ax.get_figure()
    fig.savefig(path_of_project+f"png1/{1000 + i}.png")
gif_name = f'storage_case{1}.gif'
fps = 10
file_list = glob.glob(path_of_project+'png1/*.png')
clip = mpy.ImageSequenceClip(file_list, fps=fps)
clip.write_gif(path_of_project+'{}.gif'.format(gif_name), fps=fps)
