import matplotlib.pyplot as plt
import csv
import time
import shutil
import os

def bus_en_txt(nombre, word):
    temperaturas = []
    with open(nombre, 'r', encoding='utf-8') as file:
        for numL, line in enumerate(file, 1):
            if word in line:
                temp = float(line.split()[2].replace('°C', '').replace('+', ''))
                temperaturas.append(temp)
                print(f"Encontrado en linea {numL}: {line.strip()}")
    return temperaturas

def obtener_espacio_disco():
    total, usado, libre = shutil.disk_usage("/")
    return round((usado / total) * 100, 2)

def leer_datos_csv(archivo):
    registros = []
    try:
        with open(archivo, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 1:
                    try:
                        uso_disco = float(row[0])
                        temperaturas = [float(temp) for temp in row[1:]]
                        registros.append((uso_disco, temperaturas))
                    except ValueError:
                        continue
    except FileNotFoundError:
        print("El archivo no existe.")
    return registros

def guardar_en_csv(temperaturas, uso_disco, archivo):
    with open(archivo, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([uso_disco] + temperaturas)

    with open(archivo, mode='r', encoding='utf-8') as file:
        lines = file.readlines()

    if len(lines) > 60:
        with open(archivo, mode='w', newline='', encoding='utf-8') as file:
            file.writelines(lines[-60:])

archivo_temp = "temp.txt"
archivo_csv = "datos_temperaturas.csv"

# Crear los archivos si no existen
if not os.path.exists(archivo_temp):
    with open(archivo_temp, 'w', encoding='utf-8') as file:
        pass  # Se crea un archivo vacío

if not os.path.exists(archivo_csv):
    with open(archivo_csv, 'w', encoding='utf-8') as file:
        pass  # Se crea un archivo vacío

plt.ion()
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()

while True:
    os.system(f'sensors > {archivo_temp}')
    temperaturas = bus_en_txt(archivo_temp, "Core")
    uso_disco = obtener_espacio_disco()
    guardar_en_csv(temperaturas, uso_disco, archivo_csv)

    registros = leer_datos_csv(archivo_csv)
    if not registros:
        print("Esperando datos en el CSV...")
        time.sleep(2)
        continue

    uso_disco_list = [reg[0] for reg in registros]
    num_nucleos = len(registros[0][1])
    series_temperaturas = [[] for _ in range(num_nucleos)]
    for _, temps in registros:
        for i in range(num_nucleos):
            series_temperaturas[i].append(temps[i])
    x = list(range(1, len(registros) + 1))

    ax1.cla()
    ax2.cla()

    for i in range(num_nucleos):
        ax1.plot(x, series_temperaturas[i], marker='o', label=f'Núcleo {i+1}')
    ax1.set_xlabel('Registro')
    ax1.set_ylabel('Temperatura (°C)')
    ax1.grid(True)

    ax2.plot(x, uso_disco_list, marker='x', linestyle='--', color='tab:red', label='Uso de Disco (%)')
    ax2.set_ylabel('Uso de Disco (%)', color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # Forzar actualización sin pausar
    fig.canvas.flush_events()  
    time.sleep(2)
