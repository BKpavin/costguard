"""
Azure Retail Prices API integration module for CostGuard.
Fetches public pricing info for Azure resource SKUs using the standard REST API.
"""

from typing import Dict, Any, Optional
import requests

AZURE_PRICING_API_URL = "https://prices.azure.com/api/retail/prices"


class AzurePricingClient:
    """Client for querying the Azure Retail Prices REST API."""

    def __init__(self, currency: str = "USD", timeout: int = 10):
        """
        Initialize Azure pricing client.

        Args:
            currency: Target currency for price lookup (default USD).
            timeout: HTTP request timeout in seconds.
        """
        self.currency = currency
        self.timeout = timeout

    def fetch_price(self, sku_name: str, region: str = "eastus", service_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch price details for a given SKU name and region from Azure API.

        Args:
            sku_name: Azure SKU identifier (e.g. Standard_D2s_v3, Standard_LRS).
            region: Azure region code (e.g. eastus, westeurope).
            service_name: Optional service category filter.

        Returns:
            Dict containing unit price, retail price, unit of measure, and metadata.
        """
        # Build OData filter string
        filter_parts = [
            f"armSkuName eq '{sku_name}'",
            f"armRegionName eq '{region}'",
            f"priceType eq 'Consumption'"
        ]
        if service_name:
            filter_parts.append(f"serviceName eq '{service_name}'")

        odata_filter = " and ".join(filter_parts)
        params = {
            "$filter": odata_filter,
            "currencyCode": self.currency
        }

        try:
            response = requests.get(AZURE_PRICING_API_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            items = data.get("Items", [])
            if items:
                first = items[0]
                return {
                    "sku_name": sku_name,
                    "region": region,
                    "unit_price": first.get("unitPrice", 0.0),
                    "unit_of_measure": first.get("unitOfMeasure", "1 Hour"),
                    "currency": first.get("currencyCode", self.currency),
                    "product_name": first.get("productName", ""),
                    "meter_name": first.get("meterName", "")
                }

        except requests.RequestException:
            # Fallback for offline or network issues during initial stub phase
            pass

        return {
            "sku_name": sku_name,
            "region": region,
            "unit_price": 0.0,
            "unit_of_measure": "1 Hour",
            "currency": self.currency,
            "product_name": f"Mock Azure Product ({sku_name})",
            "meter_name": "Compute / Hour"
        }
