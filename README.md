
# Backend de Bibliokuna

Este repositorio contiene los microservicios que conforman el backend de Bibliokuna, una aplicación diseñada para la gestión y exploración de colecciones de libros.

## Microservicios

El sistema está compuesto por los siguientes microservicios:

1. **Microservicio de Usuarios (MU)**
   - **Registro**: Permite registrar nuevos usuarios y verifica el correo electrónico según el tenant.
   - **Inicio de Sesión**: Proporciona detalles de sesión como color, URL y token.

2. **Microservicio de Ambientes (ME)**
   - **Ver Ambientes**: Muestra una lista de ambientes disponibles.
   - **Reservar Ambientes**: Permite reservar un ambiente en una hora específica.

3. **Microservicio de Libros (MB)**
   - **Buscar Libros**: Búsqueda de libros por título, autor o ISBN, con paginación y opción de marcar como favorito.
   - **Detalle de Libro**: Muestra información detallada de un libro específico.
   - **Reservar Libro**: Reduce el stock de un libro al realizar una reserva.

4. **Microservicio de Reservas (MR)**
   - **Reserva de Libros**: Permite reservar libros y consultar el estado de la reserva.
   - **Reserva de Ambientes**: Facilita la reserva de ambientes.
   - **Ver Reservas**: Lista las reservas actuales y pasadas.

5. **Microservicio de Favoritos (MF)**
   - **Marcar Favoritos**: Agrega o elimina libros de la lista de favoritos.
   - **Ver Favoritos**: Muestra la lista de libros favoritos del usuario.
   - **Verificar Favoritos**: Indica los libros marcados como favoritos en las búsquedas.

6. **Microservicio de Notificaciones (MN)**
   - **Notificación de Bienvenida**: Envía un correo de bienvenida opcional.

7. **Microservicio de Biblioteca (ML)**
   - **Verificar Correo**: Confirma si el correo pertenece al tenant.
   - **Información de Biblioteca**: Proporciona detalles como color y URL de la biblioteca.

## Tecnologías Utilizadas

- **Python**: Lenguaje principal para el desarrollo de los microservicios.
- **Docker**: Contenerización de los microservicios para facilitar su despliegue.
- **Swagger**: Documentación interactiva de las APIs.
- **PostgreSQL**: Base de datos relacional utilizada por algunos microservicios.
- **MongoDB**: Base de datos NoSQL utilizada por ciertos microservicios.

## Requisitos Previos

- **Docker**: Asegúrate de tener Docker instalado en tu sistema.
- **Docker Compose**: Necesario para orquestar los contenedores de los microservicios.

## Instalación y Despliegue

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/CS2032-Proyecto-Final/backend.git
   ```

2. **Navegar al directorio del proyecto**:

   ```bash
   cd backend
   ```

3. **Configurar las variables de entorno**: Crear un archivo `.env` en la raíz del proyecto con las variables necesarias para cada microservicio.

4. **Construir y levantar los contenedores**:

   ```bash
   docker-compose up -d
   ```

   Este comando construirá las imágenes y levantará los contenedores en segundo plano.

## Documentación de las APIs

Cada microservicio cuenta con su propia documentación de API accesible a través de Swagger UI en las siguientes URLs:

- **Microservicio de Usuarios**: `http://localhost:8001/docs`
- **Microservicio de Ambientes**: `http://localhost:8002/docs`
- **Microservicio de Libros**: `http://localhost:8003/docs`
- **Microservicio de Reservas**: `http://localhost:8004/docs`
- **Microservicio de Favoritos**: `http://localhost:8005/docs`
- **Microservicio de Notificaciones**: `http://localhost:8006/docs`
- **Microservicio de Biblioteca**: `http://localhost:8007/docs`

Asegúrate de que los puertos no estén en uso por otros servicios y que los contenedores correspondientes estén en ejecución.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. **Fork** el repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m 'Agregar nueva funcionalidad'`).
4. Sube tus cambios (`git push origin feature/nueva-funcionalidad`).
5. Abre un **Pull Request**.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Para más información, visita el [repositorio del proyecto](https://github.com/CS2032-Proyecto-Final/backend).
