# Responsividad — primera pasada (entrega 15)

6 archivos. Sin migraciones.

## 1. Copia los 6 archivos a su ruta exacta

## 2. Qué encontré y corregí (con evidencia, no a ojo)

Revisé el proyecto completo buscando patrones típicos de layout roto
en móvil, no adiviné al azar. Esto fue lo que encontré:

**Bug real 1 — formulario de Eventos.** Los 4 campos que van en pareja
(Lugar/Horas, Fecha inicio/Fecha fin) tenían `class="col-md-6"` sin
ninguna clase base para móvil. Eso significa que por debajo del
tamaño "md", Bootstrap no les aplica ninguna regla de ancho — en un
celular se veían apretados el uno junto al otro en vez de apilarse.
Ahora es `col-12 col-sm-6`: apilados en celulares angostos, en
pareja desde tablet hacia arriba.

**Bug real 2 — formulario de Registro.** Mismo problema, más grave:
Nombres/Apellidos, Tipo de documento/Número, y las dos contraseñas
usaban `class="col-6"` **sin ningún prefijo de tamaño** — eso los
deja siempre al 50%, en *cualquier* pantalla, incluyendo un celular
de 320px de ancho. Corregido igual, a `col-12 col-sm-6`.

**Bug real 3 — el menú lateral del panel iba primero.** En el HTML,
el sidebar (hasta 8 enlaces si eres Administrador) aparecía antes que
el contenido de la página. En escritorio no se nota porque van uno al
lado del otro, pero en celular Bootstrap los apila uno debajo del
otro — así que tenías que desplazarte por todo el menú antes de ver
la tabla o el formulario que realmente buscabas. Ahora el sidebar es
un desplegable en celular (botón "Menú del panel", cerrado por
defecto) y sigue fijo y visible como siempre en escritorio.

**Ajuste — el círculo animado del index.** Dos de los 4 chips
("Asesorías" y "Deportes") tenían posiciones pensadas para pantallas
grandes (con leves desbordes hacia afuera del círculo) que en un
celular angosto se podían salir del borde de la pantalla. Se
encogen un poco y se acomodan hacia adentro, pero solo por debajo de
576px — en tablet/escritorio no cambia nada.

**Extra:** la tabla de Aprendices (la de django-tables2) quedó
envuelta en scroll horizontal por si acaso, igual que las otras 5.

## 3. Lo que NO toqué (ya estaba bien)

Ya había revisado antes de tocar nada: las tarjetas de "Áreas de
apoyo", la lista pública de publicaciones, los botones de
exportar/buscador/filtro de las 6 listas del panel, y los formularios
de catálogos (Programa, Jornada, Ficha) — todos ya tenían su base
`col-12` correcta desde que los construimos.

## 4. Esto es una primera pasada, no la última palabra

Revisé el código, no lo vi renderizado en un celular real. Ahora que
ya sabes cómo abrir el proyecto desde tu teléfono, sería buena idea
que lo recorras completo — panel de cada rol, formularios, listas — y
me mandes captura de cualquier cosa que se siga viendo mal. Con una
imagen puedo corregir exactamente ese punto, en vez de yo tratando de
adivinar qué más falta.
