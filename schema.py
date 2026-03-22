from __future__ import annotations

SCHEMA_VERSION = 1

DDL = """
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    sku TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco_cents INTEGER NOT NULL DEFAULT 0 CHECK(preco_cents>=0),
    custo_cents INTEGER NOT NULL DEFAULT 0 CHECK(custo_cents>=0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK(stock>=0),
    stock_minimo INTEGER NOT NULL DEFAULT 0 CHECK(stock_minimo>=0),
    tipo_producao TEXT NOT NULL CHECK(tipo_producao IN ('print_on_demand','stock_fisico','misto')),
    image_path TEXT,
    design_path TEXT,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK(ativo IN (0,1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT,
    telefone TEXT,
    nif TEXT,
    morada TEXT,
    notas TEXT,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK(ativo IN (0,1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    numero TEXT UNIQUE NOT NULL,
    client_id TEXT NOT NULL,
    estado_comercial TEXT NOT NULL CHECK(estado_comercial IN ('rascunho','confirmada','paga','cancelada')),
    estado_producao TEXT NOT NULL CHECK(estado_producao IN ('pendente','em_producao','produzida','pronta_envio')),
    estado_envio TEXT NOT NULL CHECK(estado_envio IN ('por_enviar','expedida','concluida')),
    pago INTEGER NOT NULL DEFAULT 0 CHECK(pago IN (0,1)),
    tracking TEXT,
    metodo_pagamento TEXT,
    subtotal_cents INTEGER NOT NULL DEFAULT 0 CHECK(subtotal_cents>=0),
    portes_cents INTEGER NOT NULL DEFAULT 0 CHECK(portes_cents>=0),
    total_cents INTEGER NOT NULL DEFAULT 0 CHECK(total_cents>=0),
    data_prevista TEXT,
    notas TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    sku_snapshot TEXT NOT NULL,
    nome_snapshot TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK(quantidade>0),
    preco_unit_cents INTEGER NOT NULL CHECK(preco_unit_cents>=0),
    custo_unit_cents INTEGER NOT NULL CHECK(custo_unit_cents>=0),
    tipo_producao_snapshot TEXT NOT NULL CHECK(tipo_producao_snapshot IN ('print_on_demand','stock_fisico','misto')),
    personalizacao TEXT,
    stock_deducted INTEGER NOT NULL DEFAULT 0 CHECK(stock_deducted IN (0,1)),
    stock_returned INTEGER NOT NULL DEFAULT 0 CHECK(stock_returned IN (0,1)),
    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS logs (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    entidade TEXT NOT NULL,
    entidade_id TEXT,
    acao TEXT NOT NULL,
    detalhe TEXT,
    payload_json TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_orders_client_id ON orders(client_id);
CREATE INDEX IF NOT EXISTS idx_orders_estado_producao ON orders(estado_producao);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp DESC);
"""
