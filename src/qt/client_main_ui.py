import sys
import os
from pathlib import Path

from PyQt6 import QtWidgets, QtCore, QtGui

from src.modules.file_io import save_urls, load_urls
from src.qt.main_window import Ui_MainWindow
from src.modules.requester import Requester
import src.qt.resources

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
        self.get_stats_timer.timeout.connect(self.get_stats_while_playing)
        self.horizontalSliderPlayBack.sliderReleased.connect(self.seek_to_pos)
    
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

    def toggle_repeat(self) -> None:
        res = self.requester.repeat().json()

    def toggle_mute(self) -> None:
        res = self.requester.mute()

    def get_remote_file_list(self) -> None:
        res = self.requester.list()
        self.listWidgetRemoteFiles.clear()
        res_dict = res.json()
        res_files = res_dict.get('files')
        if len(res_files) > 0:
            for file in res_files:
                self.listWidgetRemoteFiles.addItem(QtWidgets.QListWidgetItem(file))

    def toggle_pause(self) -> None:
        res = self.requester.pause()
        if not self.actionPause.isChecked():
            self.get_stats_timer.start()

    def upload_file(self) -> None:
        selected_file = Path(self.file_chooser.getOpenFileName(self.mw, filter=self.media_filter)[0])
        if Path(selected_file).is_file():
            res = self.requester.upload(selected_file).json()

    def exit_program(self) -> None:
        self.stop_playing()
        sys.exit(0)


    def toggle_fullscreen(self) -> None:
        res = self.requester.fullscreen().json()

    def stop_playing(self) -> None:
        res = self.requester.stop().json()

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
        res = self.play_single(curr_url, replace=True, local=False).json()

    def play_item_from_file_list(self) -> None:
        curr_file = self.listWidgetRemoteFiles.currentItem().text()
        res = self.play_single(curr_file, local=True, replace=True)

    def choose_file_and_stream(self) -> None:
        selected_file = Path(self.file_chooser.getOpenFileName(self.mw, filter=self.media_filter)[0])
        if Path(selected_file).is_file():
            res = self.requester.stream(selected_file, replace=True).json()
            self.get_stats_timer.start()
            self.actionPause.setChecked(False)

    def play_single(self, uri: str, replace: bool, local: bool):
        res = self.requester.play(uri, local=local, replace=replace).json()
        self.get_stats_timer.start()
        self.actionPause.setChecked(False)
        self.horizontalSliderPlayBack.setEnabled(True)
        return res

    def get_stats_while_playing(self) -> None:
        res = self.requester.status().json()
        if res.get('filename') is None:
            self.get_stats_timer.stop()
            self.horizontalSliderPlayBack.setEnabled(False)
            self.horizontalSliderPlayBack.setSliderPosition(0)
        elif res.get('pause'):
            self.get_stats_timer.stop()
        else:
            if not self.horizontalSliderPlayBack.isSliderDown():
                self.horizontalSliderPlayBack.setSliderPosition(int(res.get('percent-pos')))
            print(res)
    
    def seek_to_pos(self) -> None:
        slider_position = float(self.horizontalSliderPlayBack.sliderPosition())
        res = self.requester.seek(slider_position).json()


if __name__ == '__main__':
    pass