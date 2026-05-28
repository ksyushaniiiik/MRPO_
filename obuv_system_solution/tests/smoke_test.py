from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import authenticate
from app.db import ensure_database
from app.order_service import list_orders
from app.product_service import list_products


def main():
    ensure_database()
    assert authenticate('admin', 'admin123') is not None, 'admin authorization failed'
    products = list_products()
    orders = list_orders()
    print(f'OK: products={len(products)}, orders={len(orders)}')


if __name__ == '__main__':
    main()
