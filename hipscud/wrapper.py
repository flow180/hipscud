from hipscud.resources import Resources

import sys, subprocess, os, json, tempfile
from urllib import request
from urllib.parse import parse_qs, urlparse, urlsplit

from PyQt4 import QtWebKit, QtGui, QtCore
from PyQt4.Qt import QApplication, QKeySequence, QTimer
from PyQt4.QtCore import QBuffer, QByteArray, QUrl
from PyQt4.QtWebKit import QWebView, QWebPage, QWebSettings
from PyQt4.QtNetwork import QNetworkProxy


class Wrapper(QWebView):

    highlights = 0
    unreads = 0
    id = 0
    icon = None
    name = ''
    hipchatLoaded = QtCore.pyqtSignal()

    def __init__(self, window):
        self.configure_proxy()
        QWebView.__init__(self)
        self.window = window
        with open(Resources.get_path("hipscud.js"), "r") as f:
            self.js = f.read()
        self.setZoomFactor(self.window.zoom)
        self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.urlChanged.connect(self._urlChanged)
        self.loadStarted.connect(self._loadStarted)
        self.loadFinished.connect(self._loadFinished)
        self.linkClicked.connect(self._linkClicked)
        self.page().featurePermissionRequested.connect(self.permissionRequested)
        self.addActions()

    def permissionRequested(self, frame, feature):
        self.page().setFeaturePermission(frame, feature, QWebPage.PermissionGrantedByUser)

    def configure_proxy(self):
        proxy = urlparse(os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY'))
        if proxy.hostname is not None and proxy.port is not None:
            q_network_proxy = QNetworkProxy(QNetworkProxy.HttpProxy, proxy.hostname, proxy.port)
            if proxy.username is not None:
                q_network_proxy.setUser(proxy.username)
            if proxy.password is not None:
                q_network_proxy.setPassword(proxy.password)
            QNetworkProxy.setApplicationProxy(q_network_proxy)

    def addActions(self):
        self.pageAction(QWebPage.Undo).setShortcuts(QKeySequence.Undo)
        self.pageAction(QWebPage.Redo).setShortcuts(QKeySequence.Redo)
        self.pageAction(QWebPage.Cut).setShortcuts(QKeySequence.Cut)
        self.pageAction(QWebPage.Copy).setShortcuts(QKeySequence.Copy)
        self.pageAction(QWebPage.Paste).setShortcuts(QKeySequence.Paste)
        self.pageAction(QWebPage.Back).setShortcuts(QKeySequence.Back)
        self.pageAction(QWebPage.Forward).setShortcuts(QKeySequence.Forward)
        self.pageAction(QWebPage.Reload).setShortcuts(QKeySequence.Refresh)

    def contextMenuEvent(self, event):
        entriesToHide = ['Direction', 'Open in New Window', 'Save Link...']
        menu = QtGui.QMenu(self)
        hit = self.page().currentFrame().hitTestContent(event.pos())
        if self.window.speller.initialized:
            element = hit.element()
            if hit.isContentEditable() and not hit.isContentSelected() and element.attribute("type") != "password":
                self.window.speller.populateContextMenu(menu, element)
        pageMenu = self.page().createStandardContextMenu()
        url = hit.linkUrl()
        if pageMenu is not None:
            for a in pageMenu.actions():
                if 'Open Link' == a.text() and not url.isEmpty():
                    action = QtGui.QAction('Open Link', self)
                    action.triggered.connect(lambda: self.systemOpen(
                        self._urlToString(url)))
                    menu.addAction(action)
                elif a.text() in entriesToHide:
                    continue
                elif 'Copy Link' == a.text() and not url.isEmpty():
                    action = QtGui.QAction('Copy Link', self)
                    action.triggered.connect(lambda: self.decodeAndCopy(
                        self._urlToString(url)))
                    menu.addAction(action)
                elif a.isSeparator():
                    menu.addSeparator()
                elif a.isVisible():
                    menu.addAction(a)
        del pageMenu
        menu.exec_(event.globalPos())

    def decodeAndCopy(self, url):
        QApplication.clipboard().setText(url)

    def call(self, function, arg=None):
        if isinstance(arg, str):
            arg = "'"+arg+"'"
        if arg is None:
            arg = ""
        return self.page().currentFrame().evaluateJavaScript("HipScud."+function+"("+arg+");")

    def _loadStarted(self):
        # Some custom CSS to clean/fix UX
        self.settings().setUserStyleSheetUrl(QUrl.fromLocalFile(Resources.get_path("resources.css")))
        self.page().currentFrame().evaluateJavaScript("window.Notification=function(){};Notification.permission='granted'");

    def _urlChanged(self, qUrl):
        url = self._urlToString(qUrl)
        if Resources.HOMEPAGE_URL_RE.match(url):
            self.load(QUrl("https://"+qUrl.host()+"/chat"))
        if self.window.debug: print("URL Changed: {}".format(url))

    @staticmethod
    def _urlToString(url):
        """Convert QUrl to str preserving encoding of special characters."""
        return bytes(url.toEncoded()).decode('latin1')

    def _loadFinished(self, ok=True):
        # Starting the webkit-JS bridge
        self.page().currentFrame().addToJavaScriptWindowObject("desktop", self)
        # Loading ScudCloud JS client
        self.page().currentFrame().evaluateJavaScript(self.js)
        if Resources.SIGNIN_URL == self._urlToString(self.url()):
            self.page().currentFrame().evaluateJavaScript('addSelfHostedOption();')
        self.window.statusBar().hide()

    def systemOpen(self, url):
        subprocess.call(('xdg-open', url))

    def _linkClicked(self, qUrl):
        url = self._urlToString(qUrl)
        if self.window.debug: print("Link Clicked: {}".format(url))
        if Resources.SIGNIN_URL == url or Resources.HOMEPAGE_URL_RE.match(url) or Resources.CHAT_PAGE_RE.match(url):
            self.window.switchTo(url)
        else:
            self.systemOpen(url)

    def preferences(self):
        self.window.show()
        self.call("preferences")

    def sendTickle(self):
        pass

    def logout(self):
        self.call("logout")

    def helpCenter(self):
        subprocess.call(('xdg-open', "https://confluence.atlassian.com/hipchat/hipchat-documentation-740262341.html"))

    def about(self):
        subprocess.call(('xdg-open', "https://github.com/flow180/hipscud"))

    def listChannels(self):
        return self.call("listChannels")

    def openChannel(self, menuitem, timestamp):
        self.call("open", menuitem.property_get("id"))
        self.window.show()

    @QtCore.pyqtSlot(str, int, bool)
    def count(self, team_id, unread, highlight):
        self.unreads = unread
        if unread == 0:
            self.window.leftPane.stopAlert(team_id)
            self.window.leftPane.stopUnread(self.id)
        else:
            self.window.leftPane.unread(self.id)
            self.window.leftPane.alert(team_id, unread)
        self.window.count()

    @QtCore.pyqtSlot(str)
    def populate(self, serialized):
        data = json.loads(serialized)
        self.window.teams(data['teams'])
        if self.window.current() == self:
            self.window.quicklist(data['channels'])
        self.id = data['teams'][0]['id']
        self.name = data['teams'][0]['team_name']
        # Using team id to avoid invalid icon paths (Fixes #315)
        icon_name = 'hipscud_' + data['teams'][0]['id'] + '.png'
        icon_path = os.path.join(tempfile.gettempdir(), icon_name)
        # Download the file to use in notifications
        file_name, headers = request.urlretrieve(data['icon'], icon_path)
        self.icon = file_name
        self.hipchatLoaded.emit()

    @QtCore.pyqtSlot(bool)
    def enableMenus(self, enabled):
        self.window.enableMenus(enabled)

    @QtCore.pyqtSlot(str, str)
    def sendMessage(self, title, message):
        self.window.notify(title, str(message), self.icon)
