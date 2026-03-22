from __future__ import annotations

from dataclasses import dataclass

import db
from services.backup_service import BackupService
from services.client_service import ClientService
from services.dashboard_service import DashboardService
from services.order_service import OrderService
from services.production_service import ProductionService
from services.product_service import ProductService


@dataclass
class ServiceContainer:
    conn: object
    client_service: ClientService
    product_service: ProductService
    order_service: OrderService
    production_service: ProductionService
    dashboard_service: DashboardService
    backup_service: BackupService


def build_container() -> ServiceContainer:
    db.init_database()
    conn = db.connect()
    return ServiceContainer(
        conn=conn,
        client_service=ClientService(conn),
        product_service=ProductService(conn),
        order_service=OrderService(conn),
        production_service=ProductionService(conn),
        dashboard_service=DashboardService(conn),
        backup_service=BackupService(conn),
    )
