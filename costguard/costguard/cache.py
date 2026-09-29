"""
SQLite pricing cache module for CostGuard.
Persists Azure pricing lookups locally to speed up evaluations and allow offline capabilities.
"""

import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_DB_PATH = Path("pricing_cache.db")


class PricingCache:
    """Manages SQLite-based local cache for Azure resource pricing."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        """
        Initialize database connection and create cache table if missing.

        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        """Create table schema for pricing cache if not existing."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pricing_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sku_name TEXT NOT NULL,
                    region TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    unit_price REAL NOT NULL,
                    unit_of_measure TEXT,
                    updated_at INTEGER NOT NULL,
                    UNIQUE(sku_name, region, currency)
                )
            """)
            conn.commit()

    def get(self, sku_name: str, region: str, currency: str = "USD") -> Optional[Dict[str, Any]]:
        """
        Retrieve cached pricing information.

        Args:
            sku_name: Azure SKU identifier.
            region: Azure region name.
            currency: Currency code.

        Returns:
            Cached price dictionary or None if cache miss.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT unit_price, unit_of_measure, updated_at FROM pricing_cache WHERE sku_name=? AND region=? AND currency=?",
                (sku_name, region, currency)
            )
            row = cursor.fetchone()

        if row:
            return {
                "sku_name": sku_name,
                "region": region,
                "currency": currency,
                "unit_price": row[0],
                "unit_of_measure": row[1],
                "updated_at": row[2]
            }
        return None                         

    def set(self, sku_name: str, region: str, currency: str, unit_price: float, unit_of_measure: str = "1 Hour") -> None:
        """
        Store pricing information in cache.

        Args:
            sku_name: Azure SKU identifier.
            region: Azure region name.
            currency: Currency code.
            unit_price: Price per unit.
            unit_of_measure: Measurement unit.
        """
        now = int(time.time())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pricing_cache (sku_name, region, currency, unit_price, unit_of_measure, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(sku_name, region, currency) DO UPDATE SET
                    unit_price=excluded.unit_price,
                    unit_of_measure=excluded.unit_of_measure,
                    updated_at=excluded.updated_at
            """, (sku_name, region, currency, unit_price, unit_of_measure, now))
            conn.commit()
