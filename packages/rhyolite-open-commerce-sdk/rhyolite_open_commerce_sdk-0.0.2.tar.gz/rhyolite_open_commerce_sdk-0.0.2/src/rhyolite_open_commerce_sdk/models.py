from typing import List, TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime



T = TypeVar('T')

class Category(BaseModel):
    id: str
    is_service: bool = Field(alias='isService')
    name: str
    parent_category_id: str = Field(..., alias='parentCategoryId')

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    lower_bound: int = Field(..., alias='lowerBound')
    page_no: int = Field(..., alias='pageNo')
    total_count: int = Field(..., alias='totalCount')
    total_pages: int = Field(..., alias='totalPages')
    upper_bound: int = Field(..., alias='upperBound')


class APIResponse(BaseModel, Generic[T]):
    error: Optional[Any]
    result: Optional[T]
    success: bool
    un_authorized_request: bool = Field(..., alias='unAuthorizedRequest')


class Branch(BaseModel):
    address: str = Field(..., alias='Address')
    branch_manager: Optional[str] = Field(default=None, alias='branchManager')
    city: Optional[str] = Field(default=None, alias='City')
    country_code: Optional[str] = Field(None, alias='countryCode')
    country_name: Optional[str] = Field(None, alias='countryName')
    id: str = Field(..., alias='Id')
    location: Optional[str] = Field(None, alias='Location')
    name: Optional[str] = Field(None, alias='Name')
    phone_no: Optional[str] = Field(None, alias='PhoneNo')
    region_or_state: Optional[str] = Field(None, alias='RegionOrState')


class ProductAttribute(BaseModel):
    """Model for product attributes/specifications"""
    id: UUID
    name: str
    price_adjustment: float = Field(alias='priceAdjustment')
    use_percentage: bool = Field(alias='usePercentage')
    value: str


class Product(BaseModel):
    """Model for individual product items"""
    id: UUID
    name: str
    sku: str
    short_description: str = Field(alias='shortDescription')
    full_description: str = Field(alias='fullDescription')
    
    # Pricing
    cost_price: float = Field(alias='costPrice')
    selling_price: float = Field(alias='sellingPrice')
    old_selling_price: float = Field(alias='oldSellingPrice')
    
    # Inventory
    stock_quantity: int = Field(alias='stockQuantity')
    minimum_cart_quantity: int = Field(alias='minimumCartQuantity')
    maximum_cart_quantity: int = Field(alias='maximumCartQuantity')
    
    # Category and Branch
    category_id: UUID = Field(alias='categoryId')
    category_name: str = Field(alias='categoryName')
    category_type: Optional[str] = Field(None, alias='categoryType')
    branch_id: UUID = Field(alias='branchId')
    branch_name: str = Field(alias='branchName')
    
    # Product Details
    images: List[str] = []
    product_attributes: Optional[List[ProductAttribute]] = Field(None, alias='productAttributes')
    product_specifications: Optional[str] = Field(None, alias='productSpecifications')
    
    # Physical Properties
    weight: float = 0
    height: float = 0
    length: float = 0
    width: float = 0
    
    # Unit of Measure
    uom_code: str = Field(alias='uomCode')
    uom_code_id: UUID = Field(alias='uomCodeId')
    
    # Flags and Settings
    is_published: bool = Field(alias='isPublished')
    is_deleted: bool = Field(alias='isDeleted')
    is_rental: bool = Field(alias='isRental')
    is_service: bool = Field(alias='isService')
    is_shipping_enabled: bool = Field(alias='isShippingEnabled')
    is_free_shipping: bool = Field(alias='isFreeShipping')
    ship_separately: bool = Field(alias='shipSeparately')
    mark_as_new: bool = Field(alias='markAsNew')
    not_returnable: bool = Field(alias='notReturnable')
    tax_exempt: bool = Field(alias='taxExempt')
    available_for_pre_order: bool = Field(alias='availableForPreOrder')
    allow_customer_reviews: bool = Field(alias='allowCustomerReviews')
    disable_buy_button: bool = Field(alias='disableBuyButton')
    disable_wishlist_button: bool = Field(alias='disableWishlistButton')
    
    # Dates
    creation_time: datetime = Field(alias='creationTime')
    last_modification_time: datetime = Field(alias='lastModificationTime')
    available_start_date: datetime = Field(alias='availableStartDate')
    available_end_date: datetime = Field(alias='availableEndDate')
    deletion_time: Optional[datetime] = Field(None, alias='deletionTime')
    
    # User IDs
    creator_user_id: Optional[int] = Field(None, alias='creatorUserId')
    last_modifier_user_id: Optional[int] = Field(None, alias='lastModifierUserId')
    deleter_user_id: Optional[int] = Field(None, alias='deleterUserId')
    
    # Tenant and Organization
    tenant_id: int = Field(alias='tenantId')
    manufacturer_id: UUID = Field(alias='manufacturerId')
    manufacturer_name: Optional[str] = Field(None, alias='manufacturerName')
    merchant_id: UUID = Field(alias='merchantId')
    merchant_name: Optional[str] = Field(None, alias='merchantName')
    
    # SEO and Additional Fields
    meta_title: Optional[str] = Field(None, alias='metaTitle')
    meta_description: Optional[str] = Field(None, alias='metaDescription')
    meta_keywords: Optional[str] = Field(None, alias='metaKeywords')
    search_engine_friendly_page_name: Optional[str] = Field(None, alias='searchEngineFriendlyPageName')
    admin_comment: str = Field(alias='adminComment')
    shelf_location: str = Field(alias='shelfLocation')
    item_qr: Optional[str] = Field(None, alias='itemQr')
    tag_list: Optional[str] = Field(None, alias='tagList')


class Inventory(BaseModel):
    """Model for the inventory items"""
    data: List[Product]

