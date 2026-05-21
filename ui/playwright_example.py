import allure
from playwright.sync_api import Page, expect
from datetime import datetime
import pytest
from conftest import Tools


@allure.epic("Playwright")
@allure.feature("Взаимодействие с формой регистрации")
@pytest.mark.playwright
class TestPlaywright:

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Проверка формы регистрации")
    @pytest.mark.pwreg
    def test_registration_form(self, page: Page) -> None:
        #путь к картинке
        img_path = Tools.files_dir("img", "9.jpg")
        assert img_path.exists(), f"Файл картинки не найден: {img_path}"

        #Текущая дата
        today = datetime.now().strftime('%d %b %Y')

        #Линк на сайт
        test_url = "https://demoqa.com/automation-practice-form"
        page.goto(test_url)

        with allure.step("Заполнение формы регистрации"):
            page.get_by_placeholder("First Name").fill("example name")
            page.get_by_placeholder("Last Name").fill("Жмышенко")
            page.get_by_placeholder("name@example.com").fill("fasdf@mail.ru")
            page.check('#gender-radio-2')
            page.get_by_placeholder("Mobile Number").fill("7902940291")
            page.locator("#dateOfBirthInput").fill(today)
            page.check("#hobbies-checkbox-1")
            page.check("#hobbies-checkbox-3")
            page.locator('#uploadPicture').set_input_files(img_path)
            page.locator('#currentAddress').fill("ZALUPA BOBRA")
            page.locator("#state").click()
            page.get_by_text("NCR").click()
            page.locator("#city").click()
            page.get_by_text("Delhi").click()

        with allure.step("Подтверждение"):
            page.locator('#submit').click()

        with allure.step("Проверка, что день рождения равен сегодняшнему дню"):
            actual = page.locator("#dateOfBirthInput").get_attribute("value")
            assert actual == today

        with allure.step("Проверка на идентичность текста в футере"):
            footer = page.get_by_role("contentinfo")
            footer_check = "© 2013-2026 TOOLSQA.COM | ALL RIGHTS RESERVED."
            expect(footer).to_have_text(footer_check)

        with allure.step("Проверка на получение текста после регистрации:"):
            expect(page.get_by_text("Thanks for submitting the form")).to_be_visible()

    @allure.title("Проверка радиобатонов")
    @pytest.mark.pwrdbuttons
    def test_disabled_radio(self, page: Page):
        #линк на сайт
        test_url = 'https://demoqa.com/radio-button'
        page.goto(test_url)

        with allure.step("Проверка состояния радио кнопок"):
            is_yes_enabled = page.is_enabled("#yesRadio")
            is_impressive_enabled = page.is_enabled("#impressiveRadio")
            is_no_disabled = page.is_disabled("#noRadio")

            assert is_yes_enabled, "Элемент yes не активен"
            assert is_impressive_enabled, "Элемент impressive не виден"
            assert is_no_disabled, "Элемент no виден"

    @allure.title("Проверка чекбоксов")
    @pytest.mark.pwcheckbox
    def test_check_box(self, page: Page):
        #link
        test_url = "https://demoqa.com/checkbox"
        page.goto(test_url)

        with allure.step("Проверка видимости директории Home"):
            home_is_visible = page.is_visible("text=Home")
            assert home_is_visible, "Текст Home Не виден"

        with allure.step("Проверка того, что кнопка Desktop скрыта"):
            is_hidden = page.is_hidden("text=Desktop")
            assert is_hidden, "Кнопку Desktop видно"

        with allure.step("Нажатие на дерево"):
            page.locator(".rc-tree-switcher").first.click()

        with allure.step("Проверка, что кнопку Desktop теперь видно"):
            desktop_is_enabled = page.is_visible("text=Desktop")
            assert desktop_is_enabled, "Кнопку Desktop невидно"

    @allure.title("Проверка видимости элемента")
    @pytest.mark.pwelement
    def test_load_element(self, page: Page):
        #link
        test_url = "https://demoqa.com/dynamic-properties"
        page.goto(test_url)

        with allure.step("Проверка того, что элемент VisibleAfter 5 seconds виден на странице сразу"):
            assert page.locator("#visibleAfter").count() == 0, "элемент Visible after 5 seconds виден на странице"

        with allure.step("Проверка, что элемент VisibleAfter after 5 seconds виден после задержки в 5 секунд"):
            page.wait_for_selector("#visibleAfter", state="visible", timeout=6000)

        with allure.step("Проверка того, что элемент стал видимым"):
            assert page.is_visible("#visibleAfter"), "Элемент должен стать видимым после задержки"

    @allure.title("Проверка видимых и недоступных радиобатонов")
    @pytest.mark.pwbuttons
    def test_expect(self, page: Page):
        #link
        test_url = "https://demoqa.com/radio-button"
        page.goto(test_url)

        with allure.step("Получить локаторы радио-кнопок"):
            yes_radio = page.get_by_role("radio", name="Yes")
            impressive_radio = page.get_by_role("radio", name="Impressive")
            no_radio = page.get_by_role("radio", name="No")

        with allure.step("Проверить начальное состояние кнопок"):
            expect(yes_radio).to_be_enabled()
            expect(no_radio).to_be_disabled()
            expect(impressive_radio).to_be_enabled()

        with allure.step("Проверить результат выбора"):
            page.locator("#yesRadio").click()
            expect(yes_radio).to_be_checked()
            expect(impressive_radio).not_to_be_checked()