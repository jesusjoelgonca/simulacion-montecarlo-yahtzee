# Simulación de Monte Carlo aplicada al Yahtzee

Simulador del juego de dados Yahtzee para dos jugadores, construido como laboratorio
para aplicar el método de Monte Carlo, comparar estrategias de juego y verificar
experimentalmente la ley de los grandes números.

**Actividad 2, Módulo 1** · Simulación (PREICA2602B020045) · IU Digital
**Autor:** Jesús González · **Docente:** Julian Andres Loaiza · Octubre de 2026

---

## Qué hace este repositorio

| Pregunta | Dónde se responde |
|---|---|
| ¿Cuál es la probabilidad exacta de cada categoría en un lanzamiento? | `src/yahtzee/probabilidades.py`, sección 3.1 del informe |
| ¿Cuánto vale la pena conservar dados frente a elegir bien la casilla? | `resultados/comparacion_configuraciones.csv`, sección 3.4 |
| ¿Cómo se comporta el error de la estimación al crecer la muestra? | `resultados/tabla_convergencia.csv`, secciones 3.2 y 3.3 |
| ¿Por qué se cumple la ley de los grandes números en este experimento? | Sección 3.7 del informe |
| ¿Qué se usó, qué se modificó y qué se creó? | Sección 2.1 y `src/v0_base/` |

## Estructura

```
.
├── src/
│   ├── v0_base/
│   │   └── yahtzee_base.py      # Fase USA: la guía base, sin cambios
│   └── yahtzee/                 # Fase MODIFICA + CREA
│       ├── dados.py             # Lanzamiento de dados (ruta caliente, optimizada)
│       ├── puntuacion.py        # Las 13 categorías como tabla de funciones puras
│       ├── tarjeta.py           # Casillas libres frente a casillas cerradas con 0
│       ├── retencion.py         # Qué dados se conservan entre lanzamientos
│       ├── estrategia.py        # En qué casilla se anota
│       ├── juego.py             # Motor de la partida para dos jugadores
│       ├── probabilidades.py    # Enumeración exacta de los 7776 resultados
│       ├── montecarlo.py        # Réplicas, error estándar, convergencia
│       └── cli.py               # Interfaz de línea de comandos
├── tests/                       # 56 pruebas unitarias
├── scripts/
│   ├── experimentos.py          # Los cuatro experimentos -> resultados/*.csv
│   └── figuras.py               # Los CSV -> resultados/figuras/*.png
├── resultados/                  # Evidencia versionada (CSV + figuras + resumen.json)
└── docs/
    ├── Gonzalez_Jesus_Montecarlo.pdf    # Documento técnico
    └── Gonzalez_Jesus_Montecarlo.docx
```

## Instalación

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Para regenerar las figuras hace falta además `matplotlib`:

```bash
pip install -e ".[figuras]"
```

## Uso

```bash
# Una simulación rápida
python -m yahtzee simular --partidas 10000 --estrategia bono --semilla 2026

# Comparar las cinco configuraciones del diseño factorial
python -m yahtzee comparar --partidas 10000 --semilla 2026

# Tabla de probabilidades exactas por categoría
python -m yahtzee probabilidades

# Una partida jugada paso a paso, con el detalle de cada lanzamiento
python -m yahtzee demo --semilla 7

# Exportar los puntajes de una simulación a CSV
python -m yahtzee simular --partidas 50000 --csv puntajes.csv
```

Ejemplo de salida:

```
$ python -m yahtzee simular --partidas 10000 --estrategia bono --semilla 2026
bono: n=10,000 | media=207.34 | sd=41.92 | EE=0.419 | IC95 %=(206.52, 208.16) | min=88 max=334
  percentiles: p5=143  p50=203  p95=280
```

El comando `demo` juega una partida completa y muestra los tres lanzamientos de cada
turno, que es lo que se usa en el video para explicar cómo decide cada estrategia.

## Reproducir los resultados del informe

```bash
python scripts/experimentos.py     # ~8 minutos; escribe resultados/*.csv
python scripts/figuras.py          # escribe resultados/figuras/*.png
```

Los cuatro experimentos usan la semilla 2026 y tardaron 468 segundos en un portátil
de cuatro núcleos. Con `--rapido` se ejecuta una versión reducida en menos de un
minuto, útil para comprobar que todo funciona antes de la corrida completa.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

56 pruebas, menos de 30 segundos. Cubren las reglas de puntuación, la tarjeta, las
estrategias y el motor del juego.

## Metodología: usa, modifica y crea

**Usa.** `src/v0_base/yahtzee_base.py` reproduce la guía base sin cambios: un
jugador, cinco dados, tres lanzamientos por turno y dos formas de puntuar. Con
10 000 partidas produce 227.31 puntos, un valor que se puede comprobar a mano
(13 turnos × 5 dados × 3.5 = 227.5). Se conserva intacto como línea base.

**Modifica.** Se añaden las trece categorías, la tarjeta con casillas cerradas, el
bono de la sección superior, el segundo jugador y la retención de dados entre
lanzamientos. Cada categoría es una función pura registrada en una tabla de
despacho, de modo que cambiar de variante de reglas es sustituir una entrada y no
reescribir el motor.

**Crea.** Cuatro piezas que la guía no contempla: la enumeración exacta de los
7776 resultados posibles (que sirve de patrón de comparación), la capa de Monte
Carlo con intervalos de confianza, el orquestador de experimentos y la generación
automática de figuras.

## Resultados principales

Puntaje medio por configuración, 10 000 partidas cada una, semilla 2026:

| Estrategia | Retención | Media | Error estándar | IC 95 % |
|---|---|---|---|---|
| Aleatoria | Sin retención | 45.52 | 0.181 | 45.17 – 45.87 |
| Codiciosa | Sin retención | 110.69 | 0.287 | 110.13 – 111.25 |
| Codiciosa | Por objetivo | 205.92 | 0.389 | 205.16 – 206.68 |
| Bono | Sin retención | 109.46 | 0.284 | 108.90 – 110.01 |
| **Bono** | **Por objetivo** | **207.34** | **0.419** | **206.52 – 208.16** |

El diseño factorial separa los tres aportes: la retención de dados vale cerca de
95 puntos, la elección de la casilla unos 65 y la sofisticación de la regla de
elección apenas 1.4.

## Decisiones de diseño

- **Reglas como datos.** `REGLAS` es un diccionario de funciones puras. Añadir una
  variante (por ejemplo, aceptar un Yahtzee como full) es cambiar una entrada.
- **Retención y elección separadas.** Son dos decisiones distintas del jugador y
  viven en módulos distintos, lo que permite medirlas por separado en el
  experimento factorial. Es la razón por la que existe `retencion.py`.
- **Sin dependencias circulares.** `dados` y `puntuacion` no saben nada del juego;
  `juego` compone; `montecarlo` compone juegos. Cada módulo se puede probar solo.
- **Ruta caliente optimizada.** `lanzar()` usa `Generator.integers` con `.tolist()`
  en lugar de comprensiones de listas: 6.0 µs por llamada frente a 8.3, que sobre
  millones de lanzamientos es la diferencia entre esperar y no esperar.
- **Resultados versionados.** `resultados/` se versiona a propósito: las tablas y
  figuras del informe se generan de esos CSV, no de una corrida nueva.

## Limitaciones

La comparación es entre políticas razonables, no entre políticas óptimas. Encontrar
la óptima exigiría programación dinámica sobre el espacio de estados del turno. No
se aplican el bono por Yahtzee adicional ni la regla del comodín.

## Licencia

MIT. Ver `LICENSE`.
