__name__ = "QtCodePenDisplay"
__version__ = "1.0.0"

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl, Qt, QEvent
from PyQt6.QtGui import QColor, QMouseEvent

class QCodePenDisplay(QWebEngineView):
    @staticmethod
    def _free_port():
        import socket
        with socket.socket() as sock:
            sock.bind(('', 200))
            return sock.getsockname()[1]
    
    def __init__(self, codepen_id, codepen_author, is_dragable = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._codepen_id = codepen_id
        self._codepen_author = codepen_author
        self._is_dragable = is_dragable

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setUrl(QUrl(f"https://cdpn.io/{self._codepen_author}/fullembedgrid/{self._codepen_id}?animations=run&type=embed"))

        self.setAutoFillBackground(True)
        self.setStyleSheet("background:transparent")
        self.page().setBackgroundColor(QColor(0,0,0,0))

        self.focusProxy().installEventFilter(self)

        self.draging = False
        self.current_pos = None

        webEngineScript = QWebEngineScript()
        webEngineScript.setSourceCode("""document.querySelector(".referer-warning").remove()""")
        webEngineScript.setRunsOnSubFrames(True)
        webEngineScript.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)

        self.page().scripts().insert(webEngineScript)

        self.show()

    def eventFilter(self, obj, event: QMouseEvent):
        if not self._is_dragable:
            return
        if self.focusProxy() is obj:
            match (event.type()):
                case QEvent.Type.MouseButtonPress:
                    self.draging = True
                    self.current_pos = event.pos()
                case QEvent.Type.MouseButtonRelease:
                    self.draging = False
                    self.current_pos = None
                case QEvent.Type.MouseMove:
                    if self.current_pos != None:
                        self.move(event.globalPosition().toPoint() - self.current_pos)
        return super().eventFilter(obj, event)


    @classmethod
    def start(cls, *args, **kwargs):
        app = QApplication([__file__])
        _window = cls(*args, **kwargs)
        app.exec()