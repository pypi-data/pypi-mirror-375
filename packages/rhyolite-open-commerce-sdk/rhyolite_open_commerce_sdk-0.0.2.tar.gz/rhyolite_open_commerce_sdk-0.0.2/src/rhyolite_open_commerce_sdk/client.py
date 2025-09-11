import requests
from typing import Type, TypeVar
from pydantic import ValidationError


from .models import APIResponse, PaginatedResponse, Category, Branch, Inventory

T = TypeVar("T")

class RhyoliteOpenCommerce:
    """
    A Python client for the Open Commerce API.
    """
    BASE_URL = "https://open-commerce-api.rhyoliteprime.com"

    def __init__(self, account_id: str, account_secret: str):
        """
        Initializes the RhyoliteOpenCommerce client.

        :param account_id: Your AccountId.
        :param account_secret: Your AccountSecret.
        """
        if not account_id:
            raise ValueError("AccountId is required.")
        if not account_secret:
            raise ValueError("AccountSecret is required.")

        self.account_id = account_id
        self.account_secret = account_secret
        self._session = requests.Session()
        self._session.headers.update({
            "AccountId": self.account_id,
            "AccountSecret": self.account_secret,
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, response_model: Type[T], **kwargs) -> T:
        """
        Internal method to make requests to the API and parse the response.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self._session.request(method, url, **kwargs)
            response.raise_for_status()
            json_data = response.json()
            return response_model.model_validate(json_data)
        except requests.exceptions.HTTPError as e:
            raise Exception(f"API request failed: {e.response.status_code} {e.response.text}") from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred during the API request: {e}") from e
        except ValidationError as e:
            raise Exception(f"Failed to validate API response: {e}") from e

    def get_categories(self, page_no: int = 1, page_size: int = 10) -> APIResponse[PaginatedResponse[Category]]:
        """
        Retrieves a list of categories.

        :param page_no: The page number to retrieve.
        :param page_size: The number of items per page.
        :return: An APIResponse object containing a paginated list of categories.
        """
        params = {
            "pageNo": page_no,
            "pageSize": page_size
        }

        # We need to construct the specific model type for the response
        CategoryPaginatedResponse = APIResponse[PaginatedResponse[Category]]
        return self._request("GET", "setups/get-categories", response_model=CategoryPaginatedResponse, params=params)
    
    def get_branches(self, page_no: int = 1, page_size: int = 10) -> APIResponse[PaginatedResponse[Branch]]:
        """
        Retrieves a list of branches.

        :param page_no: The page number to retrieve.
        :param page_size: The number of items per page.
        :return: An APIResponse object containing a paginated list of branches.
        """
        params = {
            "pageNo": page_no,
            "pageSize": page_size
        }
        # Assuming Branch model is defined similarly to Category
        BranchPaginatedResponse = APIResponse[PaginatedResponse[Branch]]
        return self._request("GET", "setups/get-branches", response_model=BranchPaginatedResponse, params=params)
    
    def get_inventory_items(self, page_no: int = 1, page_size: int = 10) -> APIResponse[PaginatedResponse[Inventory]]:
        """
        Retrieves a list of inventory items.

        :param page_no: The page number to retrieve.
        :param page_size: The number of items per page.
        :return: An APIResponse object containing a paginated list of inventory items.
        """
        params = {
            "pageNo": page_no,
            "pageSize": page_size
        }
        #Assuming Inventory model is defined similarly to Category
        InventoryItemPaginatedResponse = APIResponse[PaginatedResponse[Inventory]]
        return self._request("GET", "inventory/get-all-items", response_model=InventoryItemPaginatedResponse, params=params)
    
    def get_category_items(self, category_id: str, page_no: int = 1, page_size: int = 10) -> APIResponse[PaginatedResponse[Inventory]]:
        """
        Retrieves a list of inventory items in a specific category.

        :param category_id: The ID of the category to filter items.
        :param page_no: The page number to retrieve.
        :param page_size: The number of items per page.
        :return: An APIResponse object containing a paginated list of inventory items for the specific category.
        """
        params = {
            "categoryId": category_id,
            "pageNo": page_no,
            "pageSize": page_size
        }
        CategorizedInventoryItemPaginatedResponse = APIResponse[PaginatedResponse[Inventory]]
        return self._request("GET", "inventory/get-category-items", response_model=CategorizedInventoryItemPaginatedResponse, params=params)
    
