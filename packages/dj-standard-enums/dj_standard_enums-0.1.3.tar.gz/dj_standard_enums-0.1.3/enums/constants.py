from enums.framework.enum import StandardEnum
from enums.framework.item import StandardEnumItem


class TestNewEnum(StandardEnum):
    PASSED = StandardEnumItem(code="PASSED", extra_data={"category": "success"})
    FAILED = StandardEnumItem(code="FAILED", extra_data={"category": "danger"})
