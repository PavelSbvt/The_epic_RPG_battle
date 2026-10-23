from gui.utils.windows_functions import background_window_by_time_of_day
from utils.output_rich import Rich


def update_progress_bar_animation(self):
    """
    Функция для обновления прогресса прогресс-бара для имитации индикации
    вымышленного процесса

    :return: None
    """

    if self.progress_bar.value() < 100:
        self.progress_bar.setValue(self.progress_bar.value() + 1)
    else:
        self.progress_bar.setValue(100)

def loading_window_img_click(self) -> None:
    """
    Функция для смены фонового изображения загрузочного окна по кнопке (изображение
    является кнопкой). Ещё раз запускает функцию выбора случайного изображения на
    фон загрузочного окна и обновляет главные цвета изображения, которые передадутся
    функции обновления градиента.

    :return: None
    """

    Rich.print_spacer()
    Rich.debug_log("нажата кнопка изменения фонового изображения загрузочного окна")

    self.current_r, self.current_g, self.current_b, self.bg_path_check \
        = background_window_by_time_of_day(self.lb_hi_prog,
            self.loading_window, self.bg_path_check)

    Rich.debug_log("Фоновое изображение загрузочного окна изменено, "
        "цвета фонового градиента изменены.")


def update_animation_gradient(self) -> None:
    """
    Функция для создания анимации виджету с градиентом на фоне 
    (виджет находится поверх основного фона окна) - плавное смещение градиента
     и уменьшение его прозрачности.

    :return: None
    """""

    r, g, b = self.current_r, self.current_g, self.current_b

    self.base_position_gradient += self.speed * self.direction_animation

    if self.base_position_gradient >= 0.5:
        self.base_position_gradient = 0.5
        self.direction_animation = -1

    elif self.base_position_gradient <= 0.0:
        self.flag_finish_animation = True
        self.base_position_gradient = 0.0

    pos = self.base_position_gradient

    self.change_color += 0.5 * self.change_color_direction

    if self.change_color >= 40:
        self.change_color = 40
        self.change_color_direction = -1
    elif self.change_color <= 1:
        self.change_color = 1
        self.change_color_direction = 1

    index_changed_color = int(self.change_color * 0.5)

    change_red = min(255, r + index_changed_color)
    change_green = min(255, g + index_changed_color)
    change_blue = min(255, b + index_changed_color)

    if not self.flag_finish_animation:
        self.widget_gradient.setStyleSheet(f"""
                #widget_gradient{{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0.5,
                    stop: 0 rgba({r}, {g}, {b}, 0.0),
                    stop: {self.gradient_1_pos + pos * 0.3} rgba({r}, {g}, {b}, 
                    {self.opacity_animation:.2f}),
                    stop: {self.gradient_2_pos + pos * 0.3} rgba({change_red * 0.5:.0f}, 
                    {change_green * 0.5:.0f}, {change_blue * 0.5:.0f}, 
                    {self.opacity_animation * 1:.2f}),
                    stop: 1 rgba({change_red}, {change_green}, {change_blue}, 
                    {self.opacity_animation * 4:.2f})
                );
                border-radius: 10px;}}
            """)
    else:
        self.widget_gradient.setStyleSheet(f"""
                #widget_gradient{{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0.5,
                    stop: 0 rgba({r}, {g}, {b}, 0.0),
                    stop: {self.gradient_1_pos + pos * 0.3} rgba({r}, {g}, {b}, 
                    {self.opacity_animation * 1:.2f}),
                    stop: {self.gradient_2_pos + pos * 0.3} rgba({change_red * 0.5:.0f}, 
                    {change_green * 0.5:.0f}, {change_blue * 0.5:.0f}, 
                    {self.opacity_animation * 1:.2f}),
                    stop: 1 rgba({change_red}, {change_green}, {change_blue}, 
                    {self.opacity_animation * 4:.2f})
                );
                border-radius: 10px;}}
            """)
        if self.opacity_animation <= 0.1:
            self.opacity_animation += 0.0005

        if (self.gradient_1_pos + pos * 0.6) >= 0.1:
            self.gradient_1_pos -= 0.005
            self.gradient_2_pos -= 0.005
        else:
            return
