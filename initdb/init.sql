
CREATE TABLE clients (
    client_id    SERIAL PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    industry     VARCHAR(100),
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE analysts (
    analyst_id   SERIAL PRIMARY KEY,
    first_name   VARCHAR(100) NOT NULL,
    last_name    VARCHAR(100) NOT NULL,
    email        VARCHAR(255) UNIQUE NOT NULL,
    phone        VARCHAR(50),
    hire_date    DATE NOT NULL
);

CREATE TABLE projects (
    project_id   SERIAL PRIMARY KEY,
    client_id    INT NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    name         VARCHAR(255) NOT NULL,
    start_date   DATE NOT NULL,
    end_date     DATE,
    status       VARCHAR(50) NOT NULL CHECK (status IN ('planning','active','completed','on_hold','cancelled')),
    budget       NUMERIC(12,2)
);

CREATE TABLE project_analysts (
    project_id   INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    analyst_id   INT NOT NULL REFERENCES analysts(analyst_id) ON DELETE CASCADE,
    assigned_on  DATE NOT NULL DEFAULT CURRENT_DATE,
    role         VARCHAR(100),
    PRIMARY KEY (project_id, analyst_id)
);

CREATE TABLE reports (
    report_id    SERIAL PRIMARY KEY,
    project_id   INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    title        VARCHAR(255) NOT NULL,
    created_by   INT NOT NULL REFERENCES analysts(analyst_id),
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    file_path    VARCHAR(500)
);

CREATE TABLE invoices (
    invoice_id   SERIAL PRIMARY KEY,
    project_id   INT NOT NULL REFERENCES projects(project_id),
    issue_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date     DATE NOT NULL,
    amount       NUMERIC(12,2) NOT NULL,
    paid         BOOLEAN NOT NULL DEFAULT FALSE,
    paid_date    DATE
);

CREATE TABLE project_status_history (
    history_id   SERIAL PRIMARY KEY,
    project_id   INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    old_status   VARCHAR(50) NOT NULL,
    new_status   VARCHAR(50) NOT NULL,
    changed_by   INT REFERENCES analysts(analyst_id),
    changed_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO clients (name, industry, contact_name, contact_email, contact_phone)
VALUES
('ГазИнвест', 'Энергетика', 'Иван Петров', 'ivan.petrov@gazinvest.ru', '+7-495-111-22-33'),
('РосАналитика', 'Консалтинг', 'Ольга Смирнова', 'olga@rosanalytica.ru', '+7-495-222-33-44'),
('НаноТех', 'Технологии', 'Александр Кузнецов', 'a.kuznetsov@nanotech.ru', '+7-812-555-66-77'),
('АгроРесурс', 'Сельское хозяйство', 'Мария Волкова', 'm.volkova@agrores.ru', '+7-831-777-88-99'),
('СтройСфера', 'Строительство', 'Дмитрий Соколов', 'd.sokolov@stroysfera.ru', '+7-495-888-99-00');

INSERT INTO analysts (first_name, last_name, email, phone, hire_date)
VALUES
('Елена', 'Морозова', 'morozova@analytics.ru', '+7-495-123-45-67', '2021-03-15'),
('Сергей', 'Иванов', 'ivanov@analytics.ru', '+7-495-234-56-78', '2020-08-01'),
('Анна', 'Лебедева', 'lebedeva@analytics.ru', '+7-812-345-67-89', '2022-01-10'),
('Максим', 'Орлов', 'orlov@analytics.ru', '+7-343-456-78-90', '2019-11-25'),
('Юлия', 'Федорова', 'fedorova@analytics.ru', '+7-812-567-89-01', '2023-05-20');

INSERT INTO projects (client_id, name, start_date, end_date, status, budget)
VALUES
(1, 'Цифровизация сети газопроводов', '2023-01-01', NULL, 'active', 15000000),
(2, 'Разработка системы бизнес-аналитики', '2022-10-01', '2023-12-15', 'completed', 3000000),
(3, 'Исследование новых наноматериалов', '2024-03-10', NULL, 'active', 8000000),
(4, 'Анализ урожайности 2022', '2022-02-15', '2022-09-30', 'completed', 1200000),
(5, 'Автоматизация строительных процессов', '2023-05-05', NULL, 'on_hold', 5000000);

INSERT INTO project_analysts (project_id, analyst_id, assigned_on, role)
VALUES
(1, 1, '2023-01-01', 'Ведущий аналитик'),
(1, 2, '2023-01-10', 'Помощник'),
(2, 3, '2022-10-05', 'Ведущий аналитик'),
(3, 4, '2024-03-15', 'Научный консультант'),
(3, 5, '2024-03-16', 'Аналитик'),
(4, 1, '2022-02-20', 'Аналитик'),
(5, 2, '2023-05-10', 'Аналитик');

INSERT INTO reports (project_id, title, created_by, file_path)
VALUES
(1, 'Анализ цифровой зрелости', 1, '/reports/project1_report1.pdf'),
(2, 'Итоговая презентация BI-системы', 3, '/reports/project2_final.pdf'),
(3, 'Промежуточный отчёт по наноматериалам', 4, '/reports/project3_progress1.pdf'),
(4, 'Финальный отчёт по урожайности', 1, '/reports/project4_final.pdf'),
(5, 'Предварительный анализ процессов', 2, '/reports/project5_draft.pdf');

INSERT INTO invoices (project_id, issue_date, due_date, amount, paid, paid_date)
VALUES
(1, '2024-01-15', '2024-02-15', 7500000, TRUE, '2024-02-10'),
(2, '2023-01-05', '2023-02-05', 3000000, TRUE, '2023-01-30'),
(3, '2024-05-01', '2024-06-01', 4000000, FALSE, NULL),
(4, '2022-08-01', '2022-09-01', 1200000, TRUE, '2022-08-25'),
(5, '2023-07-01', '2023-08-01', 2500000, FALSE, NULL);

INSERT INTO project_status_history (project_id, old_status, new_status, changed_by)
VALUES
(1, 'planning', 'active', 1),
(2, 'active', 'completed', 3),
(3, 'planning', 'active', 4),
(5, 'active', 'on_hold', 2),
(4, 'active', 'completed', 1);

