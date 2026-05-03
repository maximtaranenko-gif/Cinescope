import allure
from pprint import pformat
from typing import Any


#Мини-библиотека для ассертов с интеграцией Allure
def assert_equal(actual: Any, expected: Any, name: str = ""):
    with allure.step(f"ASSERT EQUAL: {name}"):
        allure.attach(pformat(actual), f"ACTUAL {name}", allure.attachment_type.TEXT)
        allure.attach(pformat(expected), f"EXPECTED {name}", allure.attachment_type.TEXT)

        if actual != expected:
            allure.attach("FAILED", "STATUS", allure.attachment_type.TEXT)
            raise AssertionError(f"{name}: {actual} != {expected}")
        else:
            allure.attach("PASSED", "STATUS", allure.attachment_type.TEXT)