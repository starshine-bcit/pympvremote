import sys
import os
from pathlib import Path

from PyQt6 import QtWidgets, QtCore, QtGui

from modules.file_io import save_urls, load_urls
from modules.requester import Requester
from qt.main_window import Ui_MainWindow
from qt.upload_worker import UploadWorker
import qt.resources

# to compile .ui modules into python
# pyuic6 -o ..\main_window.py .\mainwindow.ui


class ClientMain(Ui_MainWindow):
    def __init__(self, main_window: QtWidgets.QMainWindow, requester: Requester) -> None:
        """Main Ui window widget, inherits from auto-generated Ui_MainWindow class

        Args:
            main_window (QtWidgets.QMainWindow): Parent main window to this widget
            requester (Requester): The requester instance used to make api calls. All current responses have a status_code property and json() method which returns a dict with key 'message'
        """
        self.mw = main_window
        self.mw.setWindowIcon(QtGui.QIcon(
            QtGui.QPixmap(":/icons/assets/icons/mpv_logo.svg")))
        self.mw.setWindowTitle('pympvclient')
        self.media_filter = 'Media (*.mkv *.mp4 *.mpeg *.vob *.mpeg2 *.mp3 *.opus *.flac *.mp2 *.ac3 *.eac3 *.dts *.mov *.webm *.mka *.wav *.avi *.mpeg4 *.vorbis)'
        self.requester = requester
        self.get_stats_timer = QtCore.QTimer()
        self.get_stats_timer.setInterval(1000)
        self.setupUi(self.mw)
        self.thread_pool = QtCore.QThreadPool()
        self.tabWidget.setCurrentIndex(0)
        self.init_status_bar()
        self.load_urls_and_populate()
        self.connect_events()
        self.get_remote_file_list()
        self.get_initial_player_state()
        self.init_file_chooser()

    def connect_events(self) -> None:
        """Connect all ui needed elements to self methods
        """        
        self.commandLinkButtonAppendURL.clicked.connect(self.add_url_list)
        self.listWidgetURL.itemDoubleClicked.connect(
            self.play_item_from_url_list)
        self.listWidgetRemoteFiles.itemDoubleClicked.connect(
            self.play_item_from_file_list)
        self.commandLinkButtonRemoveURL.clicked.connect(
            self.remove_selected_urls)
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
        self.listWidgetPlaylist.itemDoubleClicked.connect(
            self.play_current_playlist_item)
        self.actionNext.triggered.connect(self.play_next_item)
        self.actionPrevious.triggered.connect(self.play_previous_item)

    def init_file_chooser(self) -> None:
        """Initializes the file chooser widget
        """        
        self.file_chooser = QtWidgets.QFileDialog(self.mw)
        self.file_chooser.setDirectory(os.path.expanduser('~'))
        self.file_chooser.setFileMode(
            QtWidgets.QFileDialog.FileMode.ExistingFiles)
        self.file_chooser.setViewMode(QtWidgets.QFileDialog.ViewMode.List)

    def get_initial_player_state(self) -> None:
        """Gets player state and sets UI element properties, runs
            only on initial load
        """        
        res = self.requester.status().json()
        if res.get('mute'):
            self.actionMute.setChecked(True)
        if res.get('fullscreen'):
            self.actionFullscreen.setChecked(True)
        if res.get('repeat'):
            self.actionRepeat.setChecked(True)
        if res.get('filename') is None:
            self.horizontalSliderPlayBack.setEnabled(False)
        if len(res.get('playlist_names')) > 0:
            self.rebuild_playlist(res.get('playlist_names'))
        else:
            self.actionNext.setEnabled(False)
            self.actionPrevious.setEnabled(False)
        self.actionPause.setEnabled(False)
        self.labelPermStatusBar.setText('Volume')
        self.horizontalSliderVolume.setSliderPosition(int(res.get('volume')))
        self.statusbar.showMessage('successfully connected to server')

    def init_status_bar(self) -> None:
        """Initializes status bar widgets, since Qt Creator doesn't allow
            this
        """        
        self.labelPermStatusBar = QtWidgets.QLabel()
        self.labelPermStatusBar.setObjectName('labelPermStatusBar')
        self.horizontalSliderVolume = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSliderVolume.setOrientation(
            QtCore.Qt.Orientation.Horizontal)
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
        """Toggles repeat on the player
        """        
        res = self.requester.repeat().json()
        self.temp_status_message(res)

    def toggle_mute(self) -> None:
        """Toggles mute on the player
        """        
        res = self.requester.mute().json()
        self.temp_status_message(res)

    def toggle_pause(self) -> None:
        """Toggles pause on player
        """        
        res_full = self.requester.pause()
        if res_full.status_code == 200:
            res = res_full.json()
            if not self.actionPause.isChecked():
                self.get_stats_timer.start()
            self.temp_status_message(res)

    def get_remote_file_list(self) -> None:
        """Gets list of all files in media directory on server and displays
            them in in a listWidgetRemoteFiles
        """        
        res_full = self.requester.flist()
        if res_full.status_code == 200:
            res = res_full.json()
            self.listWidgetRemoteFiles.clear()
            res_files = res.get('files')
            if len(res_files) > 0:
                for file in res_files:
                    self.listWidgetRemoteFiles.addItem(
                        QtWidgets.QListWidgetItem(file))
                self.temp_status_message(res)

    def upload_callback(self, res) -> None:
        """Called by upload worker once upload is complete, shows response 
            message to user
        Args:
            res (Requests.response): The response object returned by the api
        """        
        res = res.json()
        self.temp_status_message(res)

    def upload_file(self) -> None:
        """Allows user to select a single file, then immediately starts
            a worker thread to upload that file
        """        
        selected_file = Path(self.file_chooser.getOpenFileName(
            self.mw, filter=self.media_filter)[0])
        if Path(selected_file).is_file():
            worker = UploadWorker(self.requester.upload, selected_file)
            worker.signals.result.connect(self.upload_callback)
            self.thread_pool.start(worker)

    def exit_program(self) -> None:
        """Safely exists the program, ensuring nothing is playing at the time
        """        
        self.stop_playing()
        sys.exit(0)

    def temp_status_message(self, res: dict) -> None:
        """Displays status message indicating return from api in the status
            bar. Overwritten each time it is called

        Args:
            res (dict): dict returned from a res.json() method, contains 'message' key
        """        
        self.statusbar.showMessage(str(res.get('message')))

    def toggle_fullscreen(self) -> None:
        """Toggles fullscreen on the player
        """        
        res = self.requester.fullscreen().json()
        self.temp_status_message(res)

    def stop_playing(self) -> None:
        """Stops playing the current file/playlist, if any
        """        
        res = self.requester.stop().json()
        self.actionNext.setEnabled(False)
        self.actionPrevious.setEnabled(False)
        self.actionPause.setChecked(False)
        self.temp_status_message(res)

    def add_url_list(self) -> None:
        """Splits user-entered URLs from plainTextEditURL, add the entries to
            listWidgetURL and then calls get_urls_and_save() to persist them
        """        
        urls = self.plainTextEditURL.toPlainText().splitlines()
        if len(urls) > 0:
            self.plainTextEditURL.setPlainText('')
            for url in urls:
                self.listWidgetURL.addItem(QtWidgets.QListWidgetItem(url))
            self.get_urls_and_save()

    def get_urls_and_save(self) -> None:
        """Gets all URLs from listWidgetURLs and calls save_urls() to save
            them into a plain text file.
        """        
        curr_urls = [self.listWidgetURL.item(
            x).text() for x in range(self.listWidgetURL.count())]
        save_urls(curr_urls)

    def load_urls_and_populate(self) -> None:
        """Calls load_urls() to get previously stored URLs and load them into 
            listWidgetURL
        """        
        urls = load_urls()
        if len(urls) > 0:
            for url in urls:
                self.listWidgetURL.addItem(QtWidgets.QListWidgetItem(url))

    def remove_selected_urls(self) -> None:
        """Removes selected URLs from listWidgetURL and save changes to disk
        """        
        if len(self.listWidgetURL.selectedItems()) > 0:
            for item in self.listWidgetURL.selectedItems():
                self.listWidgetURL.takeItem(self.listWidgetURL.row(item))
            self.get_urls_and_save()

    def play_item_from_url_list(self) -> None:
        """Gets double-clicked item from listWidgetURL and calls requester 
            method to play it
        """        
        curr_url = self.listWidgetURL.currentItem().text()
        res = self.play_single(curr_url, replace=True, local=False)
        self.temp_status_message(res)

    def play_item_from_file_list(self) -> None:
        """Gets double-clicked item from listWidgetRemoteFiles and 
            calls request method to play it
        """        
        curr_file = self.listWidgetRemoteFiles.currentItem().text()
        res = self.play_single(curr_file, local=True, replace=True)
        self.temp_status_message(res)

    def stream_callback(self, res) -> None:
        """Called by upload worker once complete, updates ui elements to 
            reflect that an item is playing

        Args:
            res (Requests.response): response returned from api upload method
        """        
        res = res.json()
        self.temp_status_message(res)
        self.get_stats_timer.start()
        self.actionPause.setChecked(False)
        self.temp_status_message(res)

    def choose_file_and_stream(self) -> None:
        """Allows user to choose single file, immediately calls upload worker 
            to put it in the remote temp directory and play it.
        """        
        selected_file = Path(self.file_chooser.getOpenFileName(
            self.mw, filter=self.media_filter)[0])
        if Path(selected_file).is_file():
            worker = UploadWorker(self.requester.stream, selected_file)
            worker.signals.result.connect(self.stream_callback)
            self.thread_pool.start(worker)

    def play_single(self, uri: str, replace: bool, local: bool):
        """Play a single item selected by user

        Args:
            uri (str): Local or remote uri to play
            replace (bool): Controls clobber, if replace is true then the selected file will replace currently playing one, if any
            local (bool): Whether this is a local or remote uri

        Returns:
            Requests.response: returns the api response back to parent method
        """        
        res = self.requester.play(uri, local=local, replace=replace).json()
        if not self.get_stats_timer.isActive():
            self.get_stats_timer.start()
        self.actionPause.setChecked(False)
        self.horizontalSliderPlayBack.setEnabled(True)
        return res

    def get_stats_callback(self) -> None:
        """Called by status timer to update UI elements to reflect current 
            player status
        """        
        res = self.requester.status().json()
        if res.get('filename') is None:
            self.get_stats_timer.stop()
            self.horizontalSliderPlayBack.setEnabled(False)
            self.horizontalSliderPlayBack.setSliderPosition(0)
            self.actionPause.setEnabled(False)
            self.actionPause.setChecked(False)
        elif res.get('pause'):
            self.get_stats_timer.stop()
        else:
            if not self.horizontalSliderPlayBack.isSliderDown() and res.get('percent_pos') is not None:
                self.horizontalSliderPlayBack.setSliderPosition(
                    int(res.get('percent_pos')))
            self.actionPause.setEnabled(True)
        plist_length = len(res.get('playlist_names'))
        plist_pos = res.get('playlist_pos')
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

    def seek_to_pos(self) -> None:
        """Seeks to position that user has dragged horizontalSliderPlayback 
            to
        """        
        slider_position = float(self.horizontalSliderPlayBack.sliderPosition())
        res = self.requester.seek(slider_position).json()
        self.temp_status_message(res)

    def change_volume(self) -> None:
        """Changes volume to position that user has dragged 
            horizontalSliderVolume to
        """        
        slider_position = int(self.horizontalSliderVolume.sliderPosition())
        res = self.requester.volume(slider_position).json()
        self.temp_status_message(res)

    def rebuild_playlist(self, playlist: list[str]) -> None:
        """Attempts to rebuild playlist if GUI is exited, but server is kept 
            running

        Args:
            playlist (list[str]): items to add to listWidgetPlaylist
        """        
        self.listWidgetPlaylist.clear()
        for item in playlist:
            self.listWidgetPlaylist.addItem(QtWidgets.QListWidgetItem(item))

    def clear_playlist(self) -> None:
        """Clears all items from playlist and stops playing, is possible
        """        
        self.listWidgetPlaylist.clear()
        res = self.requester.status().json()
        if res.get('filename') is not None:
            self.stop_playing()

    def append_to_playlist(self) -> None:
        """Append one or more items to playlist from either 
            listWidgetRemoteFiles or listWidgetURL, whichever is selected
        """        
        items = []
        if self.tabWidget.currentIndex() == 0:
            items = [x.text()
                     for x in self.listWidgetRemoteFiles.selectedItems()]
        elif self.tabWidget.currentIndex() == 1:
            items = [x.text() for x in self.listWidgetURL.selectedItems()]
        if len(items) > 0:
            for item in items:
                self.listWidgetPlaylist.addItem(
                    QtWidgets.QListWidgetItem(item))

    def play_playlist(self) -> None:
        """Gets playlist items from listWidgetPlaylist and plays starting 
            from index 0
        """        
        plist = [self.listWidgetPlaylist.item(
            x).text() for x in range(self.listWidgetPlaylist.count())]
        res = self.requester.playlist(plist, new=True, index=0).json()
        if not self.get_stats_timer.isActive():
            self.get_stats_timer.start()
        self.temp_status_message(res)
        if len(plist) > 1:
            self.actionNext.setEnabled(True)
        self.actionPause.setChecked(False)
        self.horizontalSliderPlayBack.setEnabled(True)

    def remove_selected_from_playlist(self) -> None:
        """Removes currently selected items from listWidgetPlaylist
        """        
        if len(self.listWidgetPlaylist.selectedItems()) > 0:
            for item in self.listWidgetPlaylist.selectedItems():
                self.listWidgetPlaylist.takeItem(
                    self.listWidgetPlaylist.row(item))

    def play_next_item(self) -> None:
        """Plays next playlist item, if possible
        """        
        res = self.requester.next().json()
        self.temp_status_message(res)

    def play_previous_item(self) -> None:
        """Plays previous playlist item, if possible
        """        
        res = self.requester.previous().json()
        self.temp_status_message(res)

    def play_current_playlist_item(self) -> None:
        """Gets items from listWidgetPlaylist and plays starting on 
            whichever item the user double-clicked
        """        
        plist = [self.listWidgetPlaylist.item(
            x).text() for x in range(self.listWidgetPlaylist.count())]
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
