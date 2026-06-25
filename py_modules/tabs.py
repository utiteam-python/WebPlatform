from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout
from .web_view import WebView

class TabsManager(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

        # Aggiunge la prima tab di default
        self.add_new_tab()

    def add_new_tab(self, url=None):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0,0,0,0)

        web_view = WebView()
        if url:
            web_view.load(url)
        layout.addWidget(web_view)

        index = self.addTab(tab, "Nuova scheda")
        self.setCurrentIndex(index)
        return web_view

    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)