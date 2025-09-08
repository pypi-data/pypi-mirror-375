# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-08-24 17:08
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME



class MangoLabel(QLabel):
    def __init__(self, text=None, parent=None, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.kwargs = kwargs
        self.set_style()
        self.setText(str(text) if text is not None else '')

        # 启用右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def set_style(self, style="background-color: transparent; color: black;"):
        style = self.kwargs.get('style', style)
        self.setStyleSheet(style)

    def show_context_menu(self, position):
        """显示右键上下文菜单"""
        context_menu = QMenu(self)
        context_menu.setFixedSize(40, 30)
        context_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {THEME.bg_100}; 
                border-radius: 3px;
                padding: 0px;
                margin: 0px;
                border: none; /* 移除默认边框 */
                /* 重要：设置背景只绘制在圆角区域内 */
                background-clip: border;
            }}
            QMenu::item {{
                width: 40px;
                height: 30px;
                padding: 0px;
                margin: 0px;
                text-align: center;
                background-color: transparent;
                padding-left: 0px;
                padding-right: 0px;
                margin-left: 0px;
                margin-right: 0px;
            }}
        """)

        # 设置窗口标志，避免系统默认的菜单样式
        context_menu.setWindowFlags(context_menu.windowFlags() | Qt.FramelessWindowHint)
        context_menu.setAttribute(Qt.WA_TranslucentBackground)

        # 创建复制动作
        copy_action = QAction("  复制", self)
        copy_action.triggered.connect(self.copy_text)
        context_menu.addAction(copy_action)

        context_menu.exec_(self.mapToGlobal(position))
    def copy_text(self):
        """复制文本到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text())
        from mangoui.components import success_message
        success_message(self.parent or self, '复制成功')



class MangoLabelWidget(QWidget):

    def __init__(self, text=None, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.kwargs['style'] = f"""
                   QLabel {{
                       color: {THEME.text_100};  /* 文字颜色 */
                       background-color: {kwargs.get('background_color', THEME.group.info)};  /* 背景颜色 */
                       padding: 6px 12px;  /* 内边距 */
                       border: none;  /* 无边框 */
                       border-radius: 5px;  /* 圆角 */
                       font-size: {THEME.font.text_size};  /* 字体大小 */
                       font-weight: {THEME.font.weight};  /* 字体加粗 */
                   }}
               """

        self.setMaximumHeight(25)
        self.mango_label = MangoLabel(text=text, parent=self, **self.kwargs)
        self.mango_label.setAlignment(Qt.AlignCenter)  # type: ignore

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)  # type: ignore
        layout.addWidget(self.mango_label, alignment=Qt.AlignCenter)  # type: ignore
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
