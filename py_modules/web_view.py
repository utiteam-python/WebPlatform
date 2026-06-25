from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

class WebView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        

        self.load(QUrl("https://www.google.com"))

        
