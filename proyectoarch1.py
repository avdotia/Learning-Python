import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

#download the csv. We use panda for managing csv
url = "https://vincentarelbundock.github.io/Rdatasets/csv/boot/melanoma.csv"
df = pd.read_csv(url)

print(df.head())
#print(df['thickness'].max())
#print(df.describe())
#print(dir(pd)) 

#create the file and connect to the sql 
conn = sqlite3.connect('melanoma.sqlite')
cur = conn.cursor()

#create the table

cur.execute('''
CREATE TABLE IF NOT EXISTS Melanoma (
    id INTERGER PRIMARY KEY,
    status INTEGER,
    sex INTEGER,
    age INTEGER,
    year INTEGER,
    thickness FLOAT,
    ulcer INTEGER)''')


try:
#add in the sqlite3 the csv. it is part of pandas
    df.to_sql('Melanoma', conn, if_exists='replace', index=False)
    # Carga la tabla completa a pandas
#    df = pd.read_sql("SELECT * FROM Melanoma", sqlite3.connect("melanoma.sqlite")) 
# Calcula la media en Pandas 
#    print(df["age"].mean())  
    print("Datos guardados en SQLite")
except:
    print('Error. database could not be created')
    quit()
conn.commit()

#¿Cuál es el promedio de edad de los pacientes?
cur.execute('SELECT AVG(age) FROM Melanoma')
print('Promedio de edad con melanoma: ', cur.fetchone()[0])

# ¿Cuántos casos tienen úlceras (ulcer = 1)?
cur.execute('SELECT COUNT(*) FROM Melanoma WHERE ulcer = 1')
print('Numero de casos de ulceras: ', cur.fetchone()[0])

#¿Cuál es el grosor promedio del melanoma en pacientes que fallecieron (status = 2)?
cur.execute('SELECT AVG(thickness) FROM Melanoma WHERE status = 2')
print('La media del tamanio del melanoma de los pacientes fallecidos: ', cur.fetchone()[0])

# Sobrevivencia vs. Factores de Riesgo:
#¿El grosor del melanoma afecta la tasa de supervivencia?
#¿Los pacientes más jóvenes tienen una mejor tasa de supervivencia?
#2️⃣ Tendencias a lo largo de los años:
#¿El número de casos aumentó con el tiempo?
#¿Ha cambiado la edad promedio de los pacientes con melanoma a lo largo de los años?
#3️⃣ Diferencias entre sexos:
#¿Hay diferencias en la tasa de supervivencia entre hombres y mujeres?
#¿El grosor del melanoma varía según el sexo del paciente?

#¿El grosor del melanoma afecta la tasa de supervivencia? status = 1
cur.execute('SELECT thickness FROM Melanoma WHERE status = 1 ')
lst = list()
#lst = [paciente[0] for paciente in cur.fetchall()]
for paciente in cur.fetchall() :
    lst.append(paciente[0])

print('Muertes por melanoma: ', len(lst))
if lst : 
    print('Grosor promedio: ', sum(lst)/len(lst))
    print('Grosor maximo: ', max(lst))
    print('Grosor minimo: ', min(lst))
else : print('no hay casos de muertes por melanoma')


#¿Los pacientes más jóvenes tienen una mejor tasa de supervivencia?
lst_vive = list()
lst_dormido = list()
lst_menor = list()
lst_mayor = list()
lst_menor_dor = list()
cur.execute('SELECT age, status FROM Melanoma')
for edad, estado in cur.fetchall() :
    if estado > 1 :
        lst_vive.append(edad) 
        if edad < 18 : lst_menor.append(edad)
        else : lst_mayor.append(edad)
    else : 
        if edad < 18 : lst_menor_dor.append(edad)
        lst_dormido.append(edad)


if lst_vive : 
    edad_media =sum(lst_vive)/len(lst_vive)
    print('Edad media de los pacientes afectados por el melanoma: ', edad_media)
    list_aux = sorted([edad for edad in lst_vive if edad < edad_media])
    print("Pacientes por debajo de la edad media:", list_aux)
else : print('No hay nadie afectado')
if lst_menor: 
    print('Cantidad de menores de edad afectados por el melanoma: ', len(lst_menor), '\nEdades de los menores: ', lst_menor)
    print('Edades de los menores:', sorted(lst_menor))
    print('Edad media de los pacientes menores afectados por el melanoma: ', sum(lst_menor)/len(lst_menor))
    tasa = len(lst_menor) / (len(lst_menor) + len(lst_menor_dor))
    print(f'Tasa de supervivencia: {tasa:.2%}')
else : print('No hay menores afectado')


#2️⃣ Tendencias a lo largo de los años:
#¿El número de casos aumentó con el tiempo?

cur.execute('SELECT year FROM Melanoma')
casos = dict()
anio = 0

for row  in cur.fetchall() :
    anio = row[0]
    casos[anio] = casos.get(anio, 0) + 1

casos = dict(sorted(casos.items()))
print(casos)
# Graficar la tendencia de los casos por año
plt.plot(list(casos.keys()), list(casos.values()), marker='o', linestyle='-')
plt.xlabel('Año')
plt.ylabel('Número de Casos')
plt.title('Tendencia de Casos de Melanoma por Año')
plt.grid()
plt.show()


#¿Ha cambiado la edad promedio de los pacientes con melanoma a lo largo de los años?

cur.execute('SELECT year, age FROM Melanoma')
casos = dict()
for anio, edad in cur.fetchall() :
    if anio not in casos :
        casos[anio] = list()
    casos[anio].append(edad)

edad_media = {anio: sum(edad)/len(edad) for anio, edad in casos.items()}
edad_media = dict(sorted(edad_media.items()))
print(edad_media)

#visualizacion matplotlib
#plt.plot(list(edad_media.keys()), list(edad_media.values()), marker='o', linestyle='-')
plt.plot(list(edad_media.keys()), list(edad_media.values()), marker='s', linestyle='--', color='r', markersize=5)
plt.xlabel('Anio')
plt.ylabel('Edad media casos')
plt.title('Edad promedio de los pacientes con melanoma a lo largo de los años')
plt.grid()
plt.show()

#¿Hay diferencias en la tasa de supervivencia entre hombres y mujeres? 1 == Male, 0 == Female
cur.execute('SELECT sex, status FROM Melanoma')

hombres = list()
mujeres = list()
hom_viv = 0
muj_viv = 0
for sexo, estado in cur.fetchall():
    if sexo == 1:
        if estado > 1 : hom_viv += 1
        hombres.append(estado)
        continue
    if estado > 1 : muj_viv += 1
    mujeres.append(estado)

if len(hombres) < 1 :
    print('No hay datos suficientes para calcular la tasa de supervivencia de los hombres.')
    quit()
if len(mujeres) <1 :
    print('No hay datos suficientes para calcular la tasa de supervivencia de las mujeres.')
    quit()

print(f'Media de hombres que sobreviven: {hom_viv / len(hombres):.2%}')
print(f'Media de mujeres que sobreviven: {muj_viv / len(mujeres):.2%}')
 
labels = ['Hombres', 'Mujeres']
plt.bar(labels, (hom_viv/len(hombres), muj_viv/len(mujeres)), color=['blue', 'pink'])
plt.xlabel('Genero')
plt.ylabel('Tasa de supervivencia')
plt.title('Tasa de supervivencia entre hombres y mujeres')
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
# Mostrar los valores en cada barra
survival = (hom_viv/len(hombres), muj_viv/len(mujeres))
for i, v in enumerate(survival):
    plt.text(i, v + 0.02, f"{v:.2%}", ha='center', fontsize=12)
# Mostrar el gráfico
plt.show()

#¿El grosor del melanoma varía según el sexo del paciente?
cur.execute('SELECT thickness, sex FROM Melanoma')


hombres = list()
mujeres = list()
for tam, sexo in cur.fetchall() :
    if sexo == 1 : 
        hombres.append(tam)
        continue
    mujeres.append(tam)
prom_hom = sum(hombres) / len(hombres) if len(hombres) > 0 else 0
prom_muj = sum(mujeres) / len(mujeres) if len(mujeres) > 0 else 0

if len(hombres) > 1:
    print('Tamanio promedio del melanoma en los hombres: ', prom_hom)
else :
    print('No hay datos suficientes para calcular el tamanio medio del melanoma en los hombres.')
if len(mujeres) >1 :
    print('Tamanio promedio del melanoma en las mujeres: ', prom_muj)
else :
    print('No hay datos suficientes para calcular el tamanio medio del melanoma en las mujeres.')

labels = ['hombres', 'mujeres']
plt.bar(labels, (prom_hom, prom_muj), color=['blue', 'pink'])
plt.xlabel('Genero')
plt.ylabel('Tamanio promedio melanoma')
plt.title('Tamanio del melanoma respecto al genero')
plt.grid(axis='y', linestyle='--', alpha=0.7)
promedio = prom_hom, prom_muj
for i, v in enumerate(promedio) :
    plt.text(i,v+0.02, v, ha='center', fontsize=12)
plt.show()
conn.close()