from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Shop(_message.Message):
    __slots__ = ("id", "company_id", "shop_no", "name", "site_name", "logo", "created_at", "service_started_at", "base_domain", "primary_domain", "main_status", "sub_status", "timezone", "previous_main_status", "short_code", "is_visible")
    ID_FIELD_NUMBER: _ClassVar[int]
    COMPANY_ID_FIELD_NUMBER: _ClassVar[int]
    SHOP_NO_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SITE_NAME_FIELD_NUMBER: _ClassVar[int]
    LOGO_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SERVICE_STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    BASE_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    MAIN_STATUS_FIELD_NUMBER: _ClassVar[int]
    SUB_STATUS_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_MAIN_STATUS_FIELD_NUMBER: _ClassVar[int]
    SHORT_CODE_FIELD_NUMBER: _ClassVar[int]
    IS_VISIBLE_FIELD_NUMBER: _ClassVar[int]
    id: str
    company_id: str
    shop_no: str
    name: str
    site_name: str
    logo: str
    created_at: str
    service_started_at: str
    base_domain: str
    primary_domain: str
    main_status: str
    sub_status: str
    timezone: str
    previous_main_status: str
    short_code: str
    is_visible: str
    def __init__(self, id: _Optional[str] = ..., company_id: _Optional[str] = ..., shop_no: _Optional[str] = ..., name: _Optional[str] = ..., site_name: _Optional[str] = ..., logo: _Optional[str] = ..., created_at: _Optional[str] = ..., service_started_at: _Optional[str] = ..., base_domain: _Optional[str] = ..., primary_domain: _Optional[str] = ..., main_status: _Optional[str] = ..., sub_status: _Optional[str] = ..., timezone: _Optional[str] = ..., previous_main_status: _Optional[str] = ..., short_code: _Optional[str] = ..., is_visible: _Optional[str] = ...) -> None: ...

class ShopDetail(_message.Message):
    __slots__ = ("id", "shop_id", "category", "default", "active", "terms_and_privacy_agreement", "terms_and_privacy_agreement_agreed_at", "number_of_monthly_orders", "number_of_employees", "is_used_personal_data_masking", "is_cafe24_pro", "webhook_active_status", "webhook_active_updated_at", "webhook_blacklist_event_type", "webhook_active_status_reason")
    ID_FIELD_NUMBER: _ClassVar[int]
    SHOP_ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    TERMS_AND_PRIVACY_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    TERMS_AND_PRIVACY_AGREEMENT_AGREED_AT_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_MONTHLY_ORDERS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_EMPLOYEES_FIELD_NUMBER: _ClassVar[int]
    IS_USED_PERSONAL_DATA_MASKING_FIELD_NUMBER: _ClassVar[int]
    IS_CAFE24_PRO_FIELD_NUMBER: _ClassVar[int]
    WEBHOOK_ACTIVE_STATUS_FIELD_NUMBER: _ClassVar[int]
    WEBHOOK_ACTIVE_UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    WEBHOOK_BLACKLIST_EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    WEBHOOK_ACTIVE_STATUS_REASON_FIELD_NUMBER: _ClassVar[int]
    id: str
    shop_id: str
    category: str
    default: str
    active: str
    terms_and_privacy_agreement: str
    terms_and_privacy_agreement_agreed_at: str
    number_of_monthly_orders: str
    number_of_employees: str
    is_used_personal_data_masking: str
    is_cafe24_pro: str
    webhook_active_status: str
    webhook_active_updated_at: str
    webhook_blacklist_event_type: str
    webhook_active_status_reason: str
    def __init__(self, id: _Optional[str] = ..., shop_id: _Optional[str] = ..., category: _Optional[str] = ..., default: _Optional[str] = ..., active: _Optional[str] = ..., terms_and_privacy_agreement: _Optional[str] = ..., terms_and_privacy_agreement_agreed_at: _Optional[str] = ..., number_of_monthly_orders: _Optional[str] = ..., number_of_employees: _Optional[str] = ..., is_used_personal_data_masking: _Optional[str] = ..., is_cafe24_pro: _Optional[str] = ..., webhook_active_status: _Optional[str] = ..., webhook_active_updated_at: _Optional[str] = ..., webhook_blacklist_event_type: _Optional[str] = ..., webhook_active_status_reason: _Optional[str] = ...) -> None: ...

class ShopApp(_message.Message):
    __slots__ = ("id", "shop_id", "app_id", "installed_at", "removed_at", "main_status", "key_metric", "is_deleted", "deleted_at", "migrate_status")
    ID_FIELD_NUMBER: _ClassVar[int]
    SHOP_ID_FIELD_NUMBER: _ClassVar[int]
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    INSTALLED_AT_FIELD_NUMBER: _ClassVar[int]
    REMOVED_AT_FIELD_NUMBER: _ClassVar[int]
    MAIN_STATUS_FIELD_NUMBER: _ClassVar[int]
    KEY_METRIC_FIELD_NUMBER: _ClassVar[int]
    IS_DELETED_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    MIGRATE_STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    shop_id: str
    app_id: str
    installed_at: str
    removed_at: str
    main_status: str
    key_metric: str
    is_deleted: str
    deleted_at: str
    migrate_status: str
    def __init__(self, id: _Optional[str] = ..., shop_id: _Optional[str] = ..., app_id: _Optional[str] = ..., installed_at: _Optional[str] = ..., removed_at: _Optional[str] = ..., main_status: _Optional[str] = ..., key_metric: _Optional[str] = ..., is_deleted: _Optional[str] = ..., deleted_at: _Optional[str] = ..., migrate_status: _Optional[str] = ...) -> None: ...

class ShopServiceItem(_message.Message):
    __slots__ = ("id", "shop_id", "service_id", "main_status", "sub_status", "is_used_trial_subscription", "installed_at", "live_at", "stopped_at", "subscription_conversion_method")
    ID_FIELD_NUMBER: _ClassVar[int]
    SHOP_ID_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MAIN_STATUS_FIELD_NUMBER: _ClassVar[int]
    SUB_STATUS_FIELD_NUMBER: _ClassVar[int]
    IS_USED_TRIAL_SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INSTALLED_AT_FIELD_NUMBER: _ClassVar[int]
    LIVE_AT_FIELD_NUMBER: _ClassVar[int]
    STOPPED_AT_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_CONVERSION_METHOD_FIELD_NUMBER: _ClassVar[int]
    id: str
    shop_id: str
    service_id: str
    main_status: str
    sub_status: str
    is_used_trial_subscription: str
    installed_at: str
    live_at: str
    stopped_at: str
    subscription_conversion_method: str
    def __init__(self, id: _Optional[str] = ..., shop_id: _Optional[str] = ..., service_id: _Optional[str] = ..., main_status: _Optional[str] = ..., sub_status: _Optional[str] = ..., is_used_trial_subscription: _Optional[str] = ..., installed_at: _Optional[str] = ..., live_at: _Optional[str] = ..., stopped_at: _Optional[str] = ..., subscription_conversion_method: _Optional[str] = ...) -> None: ...
