from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QToolBar,
    QLineEdit, QCheckBox, QDialog, QDialogButtonBox,
    QFormLayout, QFileDialog, QMenu
)

from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from py_modules.web_view import WebView
from .flags_manager import load_flags, save_flags
from .tabs import TabsManager
from .pla_pages import render_special_page
from pathlib import Path

AVAILABLE_FLAGS = [
    "ad_block",
    "dark_mode",
    "experimental_js",
]

class FlagsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ferdor Flags")
        self._flags = load_flags()

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.checkboxes = {}

        for flag in AVAILABLE_FLAGS:
            cb = QCheckBox(flag)
            cb.setChecked(flag in self._flags)
            self.checkboxes[flag] = cb
            form.addRow(cb)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                   Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_flags(self) -> set[str]:
        return {f for f, cb in self.checkboxes.items() if cb.isChecked()}


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ferdor Browser")
        self.resize(1200, 800)

        # Tabs manager
        self.tabs = TabsManager(self)
        self._create_ui()

    def _create_ui(self):
        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Toolbar
        self.toolbar = QToolBar("Navigazione", self)
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Back
        back_action = QAction("←", self)
        back_action.triggered.connect(lambda: self._safe_call("back"))
        self.toolbar.addAction(back_action)

        # Forward
        forward_action = QAction("→", self)
        forward_action.triggered.connect(lambda: self._safe_call("forward"))
        self.toolbar.addAction(forward_action)

        # Reload
        reload_action = QAction("⟳", self)
        reload_action.triggered.connect(lambda: self._safe_call("reload"))
        self.toolbar.addAction(reload_action)

        # New tab
        new_tab_action = QAction("🗋", self)
        new_tab_action.setToolTip("Nuova scheda")
        new_tab_action.triggered.connect(self.add_new_tab)
        self.toolbar.addAction(new_tab_action)

        # URL bar
        self.url_bar = QLineEdit(self)
        self.url_bar.returnPressed.connect(self._on_url_entered)
        self.toolbar.addWidget(self.url_bar)

        # Flags
        flags_action = QAction("Flags", self)
        flags_action.triggered.connect(self._open_flags_dialog)
        self.toolbar.addAction(flags_action)

        # Pages menu
        self._add_pages_menu()

        layout.addWidget(self.tabs)
        self.setCentralWidget(central)

        # Connetti cambi tab
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self._connect_current_webview()

        # Apro prima tab
        self.add_new_tab("pla://home")

    # ---------- Sicure chiamate ----------
    def _safe_call(self, method_name):
        webview = self.current_webview()
        if webview:
            getattr(webview, method_name)()

    # ---------- Tabs ----------
    def current_webview(self):
        """Ritorna il WebView della tab corrente o None se speciale"""
        tab = self.tabs.currentWidget()
        if tab and tab.layout().count() > 0:
            w = tab.layout().itemAt(0).widget()
            return w if isinstance(w, WebView) else None
        return None

    def add_new_tab(self, url=None):
        webview = self.tabs.add_new_tab(url)
        webview.urlChanged.connect(self._on_url_changed)
        webview.page().profile().downloadRequested.connect(self._on_download_requested)
        self.url_bar.setText(webview.url().toString())

    def _connect_current_webview(self):
        webview = self.current_webview()
        if webview:
            webview.urlChanged.connect(self._on_url_changed)
            webview.page().profile().downloadRequested.connect(self._on_download_requested)
            self.url_bar.setText(webview.url().toString())

    def _on_tab_changed(self, index):
        self._connect_current_webview()

    # ---------- URL Navigation ----------
    def _on_url_entered(self):
        text = self.url_bar.text().strip()
        tab = self.tabs.currentWidget()
        webview = self.current_webview()

        if text.startswith("pla://"):
            # Renderizza pagina speciale
            special_widget = render_special_page(QUrl(text))
            if webview:
                tab.layout().removeWidget(webview)
                webview.deleteLater()
            tab.layout().addWidget(special_widget)
            self.url_bar.setText(text)

        elif webview:
            if "." in text or text.startswith("http"):
                if not text.startswith("http"):
                    text = "https://" + text
                webview.load(QUrl(text))
            else:
                query = text.replace(" ", "+")
                google_url = f"https://www.google.com/search?q={query}"
                webview.load(QUrl(google_url))

    def _on_url_changed(self, qurl):
        self.url_bar.setText(qurl.toString())

    # ---------- Download ----------
    def _on_download_requested(self, download):
        downloads_dir = Path.home() / "Downloads"

        filename = download.downloadFileName()

        save_path, _ = QFileDialog.getSaveFileName(
        self,
        "Salva file",
        str(downloads_dir / filename)
    )

        if save_path:
            path_obj = Path(save_path)
            download.setDownloadFileName(path_obj.name)
            download.setDownloadDirectory(str(path_obj.parent))
            download.accept()
            
    # ---------- Flags ----------
    def _open_flags_dialog(self):
        dlg = FlagsDialog(self)
        if dlg.exec():
            flags = dlg.selected_flags()
            save_flags(flags)


    # ---------- Menu Ferdor Pages ----------
    def _add_pages_menu(self):
        menu_action = QAction("⋯", self)
        menu = QMenu()

        # Pagine interne
        menu.addAction("Home", lambda: self.load_fe_page("pla://home"))
        menu.addAction("Config", lambda: self.load_fe_page("pla://config"))
        menu.addAction("Settings", lambda: self.load_fe_page("pla://settings"))

        menu.addSeparator()
        menu.addAction("Esci", lambda: self.close())

        menu_action.setMenu(menu)
        self.toolbar.addAction(menu_action)

    def load_fe_page(self, url_str):
        tab = self.tabs.currentWidget()
        webview = self.current_webview()
        if url_str.startswith("pla://"):
            special_widget = render_special_page(QUrl(url_str))
            if webview:
                tab.layout().removeWidget(webview)
                webview.deleteLater()
            tab.layout().addWidget(special_widget)
            self.url_bar.setText(url_str)

    def load(self, url_str):
        """Carica un link esterno nella scheda corrente o nuova scheda"""
        webview = self.current_webview()
        if webview:
            if url_str.startswith("fe://"):
                self.load_fe_page(url_str)
            else:
                webview.load(QUrl(url_str))
        else:
            # fallback: nuova tab
            self.add_new_tab(url_str)