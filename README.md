# EDAA
Proyecto del ramo Estructuras de Datos y Algoritmos Avanzados.

Repositorio de GitHub: https://github.com/ChileProtogen/EDAA

NOTA: Es estrictamente necesario que el archivo a ejecutar esté en la misma carpeta y que el dataset puntos_100.txt (u otro que se elija) exista dentro de la misma carpeta. Pues la carpeta datasets es exclusivamente para benchmarking y podría resultar en outcomes inesperados si no se prueba en la misma.

Para la ejecución de visual_graham.py se requiere que el archivo graham_scan.py esté en la misma carpeta y el dataset también (en este caso puntos_100.txt)

Ejemplo: python .\visual_graham.py .\puntos_100.txt para el archivo puntos_100.txt, se puede con otros sets de puntos. 

Para la ejecución de visual_jarvis.py se requiere que jarvismarch.py esté en la misma carpeta y que el dataset a probar también lo esté.

Ejemplo: python .\visual_jarvis.py .\puntos_100.txt para el archivo puntos_100.txt, se puede con otros sets de puntos.

Para la ejecución de visual_monotone.py y visual_incremental_monotone_chain.py se requiere que monotone_chain.py esté en la misma carpeta y que el dataset a probar también lo esté.

Ejemplo para visual_monotone.py: .\visual_monotone.py .\puntos_100.txt para el archivo puntos_100.txt, se puede con otros sets de puntos.

Ejemplo para visual_incremental_monotone_chain.py: python .\visual_incremental_monotone_chain.py .\puntos_100.txt para el archivo puntos_100.txt, se puede con otros sets de puntos.

En este se pueden agregar puntos incrementalmente y se actualiza el convex hull en tiempo real.
Funciona añadirlos en consola y clickeando con el mouse. No se permite poner dos puntos en la misma coordenada.
