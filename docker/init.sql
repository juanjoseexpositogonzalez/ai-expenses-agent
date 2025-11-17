-- Crear tabla de categorías si no existe (se creará automáticamente con SQLModel, pero esto asegura las predefinidas)
-- Las categorías se insertarán después de que SQLModel cree las tablas

-- Categorías predefinidas (se ejecutará después de la creación de tablas)
INSERT INTO category (name, description, is_system, created_at) VALUES
('Comida', 'Gastos en restaurantes, supermercados y alimentos', true, NOW()),
('Transporte', 'Taxi, autobús, metro, gasolina, peajes', true, NOW()),
('Alojamiento', 'Hoteles, Airbnb, hospedaje', true, NOW()),
('Entretenimiento', 'Cine, conciertos, eventos, hobbies', true, NOW()),
('Salud', 'Medicinas, consultas médicas, seguro', true, NOW()),
('Compras', 'Ropa, electrónicos, artículos varios', true, NOW()),
('Servicios', 'Luz, agua, internet, suscripciones', true, NOW()),
('Otros', 'Gastos varios no categorizados', true, NOW())
ON CONFLICT DO NOTHING;