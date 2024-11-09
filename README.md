
# Microservicios de Bibliokuna

### Microservicio **Users (MU)**

- Registro: Permite registrar usuarios y verifica el correo según el tenant.
- Inicio de Sesión: Proporciona detalles de sesión como color, URL y token.

### Microservicio **Environment (ME)**

- Ver Ambientes: Muestra una lista de ambientes disponibles.
- Reservar Ambientes: Permite reservar un ambiente a una hora específica.

### Microservicio **Book (MB)**

- Buscar Libros: Búsqueda de libros por título, autor o ISBN, con paginación y favoritos.
- Detalle de Libro: Muestra detalles completos de un libro específico.
- Reservar Libro: Reduce el stock de un libro al reservarlo.

### Microservicio **Reservations (MR)**

- Reserva de Libros: Permite reservar libros y ver el estado de la reserva.
- Reserva de Ambientes: Habilita la reserva de ambientes.
- Ver Reservas: Lista de reservas actuales y pasadas.

### Microservicio **Favorites (MF)**

- Marcar Favoritos: Agrega o quita libros de la lista de favoritos.
- Ver Favoritos: Muestra la lista de libros favoritos del usuario.
- Verificar Favoritos: Marca favoritos en las búsquedas.

### Microservicio **Notifications (MN)**

- Notificación de Bienvenida: Envía un correo de bienvenida opcional.

### Microservicio **Library (ML)**

- Verificar Correo: Confirma si el correo pertenece al tenant.
- Información de Biblioteca: Proporciona detalles como color y URL de la biblioteca.
