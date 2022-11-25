import sys
import os
from pathlib import Path

from PyQt6 import QtWidgets, QtCore, QtGui

from modules.file_io import save_urls, load_urls
from modules.requester import Requester
from qt.main_window import Ui_MainWindow
import qt.resources

# to compile .ui modules into python
# pyuic6 -x -o ..\main_window.py .\mainwindow.ui

class ClientMain(Ui_MainWindow):
    def __init__(self, main_window: QtWidgets.QMainWindow, requester: Requester):
        self.mw = main_window
        self.mw.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(":/icons/assets/icons/mpv_logo.svg")))
        self.mw.setWindowTitle('pympvclient')
        self.media_filter = 'Media (*.mkv *.mp4 *.mpeg *.vob *.mpeg2 *.mp3 *.opus *.flac *.mp2 *.ac3 *.eac3 *.dts *.mov *.webm *.mka *.wav *.avi *.mpeg4 *.vorbis)'
        self.requester = requester
        self.get_stats_timer = QtCore.QTimer()
        self.get_stats_timer.setInterval(1000)
        self.setupUi(self.mw)
        self.tabWidget.setCurrentIndex(0)
        self.init_status_bar()
        self.load_urls_and_populate()
        self.connect_events()
        self.get_remote_file_list()
        self.get_initial_player_state()
        self.init_file_chooser()

    def connect_events(self) -> None:
        self.commandLinkButtonAppendURL.clicked.connect(self.add_url_list)
        self.listWidgetURL.itemDoubleClicked.connect(self.play_item_from_url_list)
        self.listWidgetRemoteFiles.itemDoubleClicked.connect(self.play_item_from_file_list)
        self.commandLinkButtonRemoveURL.clicked.connect(self.remove_selected_urls)
        self.actionRefreshFiles.triggered.connect(self.get_remote_file_list)
        self.actionStop.triggered.connect(self.stop_playing)
        self.actionExit.triggered.connect(self.exit_program)
        self.actionUpload.triggered.connect(self.upload_file)
        self.actionPause.triggered.connect(self.toggle_pause)
        self.actionStream.triggered.connect(self.choose_file_and_stream)
        self.actionMute.triggered.connect(self.toggle_mute)
        self.actionFullscreen.triggered.connect(self.toggle_fullscreen)
        self.actionRepeat.triggered.connect(self.toggle_repeat)
        self.get_stats_timer.timeout.connect(self.get_stats_callback)
        self.horizontalSliderPlayBack.sliderReleased.connect(self.seek_to_pos)
        self.actionClear.triggered.connect(self.clear_playlist)
        self.actionAppend.triggered.connect(self.append_to_playlist)
        self.actionPlayPlaylist.triggered.connect(self.play_playlist)
        self.actionRemove.triggered.connect(self.remove_selected_from_playlist)
        self.listWidgetPlaylist.itemDoubleClicked.connect(self.play_current_playlist_item)
        self.actionNext.triggered.connect(self.play_next_item)
        self.actionPrevious.triggered.connect(self.play_previous_item)
    
    def init_file_chooser(self) -> None:
        self.file_chooser = QtWidgets.QFileDialog(self.mw)
        self.file_chooser.setDirectory(os.path.expanduser('~'))
        self.file_chooser.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)
        self.file_chooser.setViewMode(QtWidgets.QFileDialog.ViewMode.List)

    def get_initial_player_state(self) -> None:
        res = self.requester.status().json()
        print(res)
        if res.get('mute'):
            self.actionMute.setChecked(True)
        if res.get('fullscreen'):
            self.actionFullscreen.setChecked(True)
        if res.get('repeat'):
            self.actionRepeat.setChecked(True)
        if res.get('filename') is None:
            self.horizontalSliderPlayBack.setEnabled(False)
        if len(res.get('playlist-names')) > 0:
            self.rebuild_playlist(res.get('playlist-names'))
        else:
            self.actionNext.setEnabled(False)
            self.actionPrevious.setEnabled(False)
        self.labelPermStatusBar.setText('Idle')
        self.horizontalSliderVolume.setSliderPosition(int(res.get('volume')))
        self.statusbar.showMessage('successfully connected to server')

    def init_status_bar(self) -> None:
        self.labelPermStatusBar = QtWidgets.QLabel()
        self.labelPermStatusBar.setObjectName('labelPermStatusBar')
        self.horizontalSliderVolume = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSliderVolume.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSliderVolume.setObjectName('horizontalSliderVolume')
        self.horizontalSliderVolume.setToolTip('Volume')
        self.horizontalSliderVolume.setFixedWidth(100)
        self.horizontalSliderVolume.setRange(0, 100)
        self.statusbarSpacer = QtWidgets.QLabel()
        self.statusbarSpacer.setFixedWidth(1)
        self.statusbar.addPermanentWidget(self.labelPermStatusBar)
        self.statusbar.addPermanentWidget(self.statusbarSpacer)
        self.statusbar.addPermanentWidget(self.horizontalSliderVolume)
        self.horizontalSliderVolume.sliderReleased.connect(self.change_volume)
        
    def toggle_repeat(self) -> None:
        res = self.requester.repeat().json()
        self.temp_status_message(res)

    def toggle_mute(self) -> None:
        res = self.requester.mute().json()
        self.temp_status_message(res)

    def get_remote_file_list(self) -> None:
        res_full = self.requester.flist()
        if res_full.status_code == 200:
            res = res_full.json()
            self.listWidgetRemoteFiles.clear()
            res_files = res.get('files')
            if len(res_files) > 0:
                for file in res_files:
                    self.listWidgetRemoteFiles.addItem(QtWidgets.QListWidgetItem(file))
                self.temp_status_message(res)

    def toggle_pause(self) -> None:
        res = self.requester.pause().json()
        if not self.actionPause.isChecked():
            self.get_stats_timer.start()
        self.temp_status_message(res)

    def upload_file(self) -> None:
        selected_file = Path(self.file_chooser.getOpenFileName(self.mw, filter=self.media_filter)[0])
        if Path(selected_file).is_file():
            res = self.requester.upload(selected_file).json()
            self.temp_status_message(res)

    def exit_program(self) -> None:
        self.stop_playing()
        sys.exit(0)

    def temp_status_message(self, res: dict) -> None:
        self.statusbar.showMessage(str(res.get('message')))

    def toggle_fullscreen(self) -> None:
        res = self.requester.fullscreen().json()
        self.temp_status_message(res)

    def stop_playing(self) -> None:
        res = self.requester.stop().json()
        self.actionNext.setEnabled(False)
        self.actionPrevious.setEnabled(False)
        self.actionPause.setChecked(False)
        self.temp_status_message(res)

    def add_url_list(self) -> None:
        urls = self.plainTextEditURL.toPlainText().splitlines()
        if len(urls) > 0:
            self.plainTextEditURL.setPlainText('')
            for url in urls:
                self.listWidgetURL.addItem(QtWidgets.QListWidgetItem(url))
            self.get_urls_and_save()
    
    def get_urls_and_save(self) -> None:
        curr_urls = [self.listWidgetURL.item(x).text() for x in range(self.listWidgetURL.count())]
        save_urls(curr_urls)

    def load_urls_and_populate(self) -> None:
        urls = load_urls()
        if len(urls) > 0:
            for url in urls:
                self.listWidgetURL.addItem(QtWidgets.QListWidgetItem(url))

    def remove_selected_urls(self) -> None:
        if len(self.listWidgetURL.selectedItems()) > 0:
            for item in self.listWidgetURL.selectedItems():
                self.listWidgetURL.takeItem(self.listWidgetURL.row(item))
            self.get_urls_and_save()

    def play_item_from_url_list(self) -> None:
        curr_url = self.listWidgetURL.currentItem().text()
        res = self.play_single(curr_url, replace=True, local=False)
        self.temp_status_message(res)

    def play_item_from_file_list(self) -> None:
        curr_file = self.listWidgetRemoteFiles.currentItem().text()
        res = self.play_single(curr_file, local=True, replace=True)
        self.temp_status_message(res)

    def choose_file_and_stream(self) -> None:
        selected_file = Path(self.file_chooser.getOpenFileName(self.mw, filter=self.media_filter)[0])
        if Path(selected_file).is_file():
            res = self.requester.stream(selected_file, replace=True).json()
            self.get_stats_timer.start()
            self.actionPause.setChecked(False)
            self.temp_status_message(res)

    def play_single(self, uri: str, replace: bool, local: bool):
        res = self.requester.play(uri, local=local, replace=replace).json()
        if not self.get_stats_timer.isActive():
            self.get_stats_timer.start()
        self.actionPause.setChecked(False)
        self.horizontalSliderPlayBack.setEnabled(True)
        return res

    def get_stats_callback(self) -> None:
        res = self.requester.status().json()
        if res.get('filename') is None:
            self.get_stats_timer.stop()
            self.horizontalSliderPlayBack.setEnabled(False)
            self.horizontalSliderPlayBack.setSliderPosition(0)
        elif res.get('pause'):
            self.get_stats_timer.stop()
        else:
            if not self.horizontalSliderPlayBack.isSliderDown() and res.get('percent-pos') is not None:
                self.horizontalSliderPlayBack.setSliderPosition(int(res.get('percent-pos')))
        plist_length = len(res.get('playlist-names'))
        plist_pos = res.get('playlist-pos')
        if plist_length > 1 and res.get('filename') is not None:
            self.listWidgetPlaylist.item(plist_pos).setSelected(True)
            if plist_pos < plist_length:
                self.actionNext.setEnabled(True)
            else:
                self.actionNext.setEnabled(False)
            if plist_pos > 0:
                self.actionPrevious.setEnabled(True)
            else:
                self.actionPrevious.setEnabled(False)
        if res.get('filename') is None:
            self.actionNext.setEnabled(False)
            self.actionPrevious.setEnabled(False)
        print(res)
    
    def seek_to_pos(self) -> None:
        slider_position = float(self.horizontalSliderPlayBack.sliderPosition())
        res = self.requester.seek(slider_position).json()
        self.temp_status_message(res)
    
    def change_volume(self) -> None:
        slider_position = int(self.horizontalSliderVolume.sliderPosition())
        res = self.requester.volume(slider_position).json()
        self.temp_status_message(res)

    def rebuild_playlist(self, playlist: list[str]) -> None:
        self.listWidgetPlaylist.clear()
        for item in playlist:
            self.listWidgetPlaylist.addItem(QtWidgets.QListWidgetItem(item))
    
    def clear_playlist(self) -> None:
        self.listWidgetPlaylist.clear()
        res = self.requester.status().json()
        if res.get('filename') is not None:
            self.stop_playing()
    
    def append_to_playlist(self) -> None:
        items = []
        if self.tabWidget.currentIndex() == 0:
            items = [x.text() for x in self.listWidgetRemoteFiles.selectedItems()]
        elif self.tabWidget.currentIndex() == 1:
            items = [x.text() for x in self.listWidgetURL.selectedItems()]
        if len(items) > 0:
            for item in items:
                self.listWidgetPlaylist.addItem(QtWidgets.QListWidgetItem(item))
    
    def play_playlist(self) -> None:
        plist = [self.listWidgetPlaylist.item(x).text() for x in range(self.listWidgetPlaylist.count())]
        res = self.requester.playlist(plist, new=True, index=0).json()
        if not self.get_stats_timer.isActive():
            self.get_stats_timer.start()
        self.temp_status_message(res)
        if len(plist) > 1:
            self.actionNext.setEnabled(True)
        self.actionPause.setChecked(False)
        self.horizontalSliderPlayBack.setEnabled(True)

    def update_remote_playlist(self) -> None:
        plist = [self.listWidgetPlaylist.item(x).text() for x in range(self.listWidgetPlaylist.count())]
        res = self.requester.playlist(plist, new=False, index=0).json()
        self.temp_status_message(res)

    def remove_selected_from_playlist(self) -> None:
        if len(self.listWidgetPlaylist.selectedItems()) > 0:
            for item in self.listWidgetPlaylist.selectedItems():
                self.listWidgetPlaylist.takeItem(self.listWidgetPlaylist.row(item))
    
    def play_next_item(self) -> None:
        res = self.requester.next().json()
        self.temp_status_message(res)
    
    def play_previous_item(self) -> None:
        res = self.requester.previous().json()
        self.temp_status_message(res)

    def play_current_playlist_item(self) -> None:
        plist = [self.listWidgetPlaylist.item(x).text() for x in range(self.listWidgetPlaylist.count())]
        curr_index = self.listWidgetPlaylist.selectedIndexes()[0].row()
        res = self.requester.playlist(plist, new=True, index=curr_index).json()
        self.temp_status_message(res)
        if curr_index > 1:
            self.actionPrevious.setEnabled(True)
        if curr_index < len(plist):
            self.actionNext.setEnabled(True)
        if not self.get_stats_timer.isActive():
            self.get_stats_timer.start()
        self.actionPause.setChecked(False)
        self.horizontalSliderPlayBack.setEnabled(True)

if __name__ == '__main__':
    pass