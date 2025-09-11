from random import randint

from playwright.sync_api import Page

def add_mouse_position_listener(page: Page):
    page.add_init_script("""
      window._mousePos = {x: 0, y: 0};
      document.addEventListener('mousemove', e => {
        window._mousePos.x = e.clientX;
        window._mousePos.y = e.clientY;
      });
    """)

def mouse_position(page: Page):
    return page.evaluate("window._mousePos")

def click(page: Page, selector: str):
    element = page.wait_for_selector(selector)
    box = element.bounding_box()

    x_element = box['x'] + box['width']/2
    y_element = box['y'] + box['height']/2

    while True:
        position = mouse_position(page)
        in_x = box['x'] < position['x'] < box['x'] + box['width']
        in_y = box['y'] < position['y'] < box['y'] + box['height']

        if in_x and in_y:
            page.mouse.click(position['x'], position['y'])
            break

        if x_element - position['x'] > 0:
            x_new = position['x'] + randint(1, 5)
        else:
            x_new = position['x'] - randint(1, 5)

        if y_element - position['y'] > 0:
            y_new = position['y'] + randint(1, 5)
        else:
            y_new = position['y'] - randint(1, 5)

        page.mouse.move(x_new, y_new)
