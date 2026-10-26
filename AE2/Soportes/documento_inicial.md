# Documento inicial: perfil de barrios para arrendar o comprar vivienda

> Borrador construido a partir de la necesidad y los objetivos del proyecto. Ajústalo con tus palabras o reemplázalo por tu documento inicial si ya lo tienes.

## Propósito

Crear un informe con el que las personas puedan perfilar fácilmente los barrios de una ciudad y presupuestar el valor de arrendar o comprar un inmueble. El informe se plantea primero para una ciudad (por ejemplo, Medellín) y puede aplicarse a otras ciudades de Colombia. Debe servir como base para plantear la búsqueda de un inmueble según las necesidades de cada persona.

## Necesidad

Quien busca vivienda suele comparar barrios a partir de avisos sueltos, sin una referencia clara de cuánto cuesta un barrio frente a otro ni de cuánta oferta existe. Esto dificulta fijar un presupuesto realista y decidir si conviene arrendar o comprar.

## Objetivos específicos

1. Conocer, por barrio, el costo típico de arriendo y de venta.
2. Poder filtrar por barrio el costo y la cantidad de ofertas de arriendo y de venta.
3. Identificar los barrios con más ofertas.

## Datos

- **Dataset:** [`aptologia/arriendo-rentabilidad-por-barrio-colombia-2026`](https://huggingface.co/datasets/aptologia/arriendo-rentabilidad-por-barrio-colombia-2026)
- **Configuración:** `rentabilidad_arriendo_venta_barrio`, split `train`.
- **Autor y licencia:** Aptología, CC BY 4.0 (permite usarlo y redistribuirlo citando la fuente).
- **Contenido:** una fila por barrio, en 13 ciudades de Colombia, con la cantidad de avisos y el precio mediano de arriendo y de venta, y la rentabilidad bruta del arriendo. Corte de octubre de 2026.

## Usuarios

Personas que buscan arrendar o comprar vivienda, y quienes evalúan el negocio de arrendar un inmueble que ya tienen o que piensan comprar.

## Alcance y limitaciones

- Los precios son de **oferta** (lo que piden los avisos), no de cierre de negocio.
- Los datos están **agregados por barrio**: no describen inmuebles individuales.
- Es una foto de una fecha; los precios cambian con el tiempo.
- Los barrios con pocos avisos dan precios menos confiables; el dataset los marca con `ok_todos = False`.
