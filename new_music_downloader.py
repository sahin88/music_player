import sys
import os
import time

from PyQt5 import QtGui, QtWidgets, QtCore, QtMultimedia
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QListWidget, QMenu, QFrame, QButtonGroup
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, \
    QMessageBox, QApplication, QProgressBar
import youtube_dl
from PyQt5.QtCore import QUrl, QTimer, QThread, pyqtSignal
from pytube import YouTube

BUTTON_COLOR = "#128c7e"
APPLE_MUSIC_RED_COLOR = "#f94c57"
BASE_DIR = f'{os.path.dirname(__file__)}/utils'
RELATIVE_DIR = "" # Please enter your directory mp3 diractory


class DownloadThreadPyTube(QThread):
    progress_update = pyqtSignal(float)

    def __init__(self, video_link, local_path):
        super().__init__()
        self.local_path = local_path
        self.video_link = video_link

    def run(self):
        if self.local_path:
            try:
                yt = YouTube(self.video_link, on_progress_callback=self.on_progress)
                video_stream = yt.streams.filter(only_audio=True).first()
                video_stream.download(output_path=self.local_path, filename=f"{video_stream.title}.mp3")
            except Exception as e:
                print(f"An error occurred: {e}")

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        print(stream, bytes_remaining)
        bytes_downloaded = total_size - bytes_remaining
        progress = int(bytes_downloaded / total_size * 100)
        self.progress_update.emit(progress)


class YouTubeDownloader(QWidget):
    folder_path = RELATIVE_DIR

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Music Downloader")
        top_layout = QHBoxLayout()
        layout_right = QVBoxLayout()
        layout_left = QVBoxLayout()
        self.folder_path = RELATIVE_DIR
        self.url_input = QLineEdit()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet("QProgressBar {border-radius: 10px; padding: 10px;"
                                        "background-color: #e5ded4;"
                                        "border-style: solid;"
                                        "text-align: center;"
                                        "color:  #128c7e;"
                                        "}"
                                        "QProgressBar::chunk {border-radius: 10px;"
                                        "width: 10px;"
                                        "background-color: #f94c57;"
                                        "color: #128c7e;"
                                        "}")

        # Set rounded appearance
        self.url_input.setStyleSheet("QLineEdit { border-radius: 10px; padding: 10px;"
                                     "background-color: #e5ded4;"
                                     "font-family: 'Comic Sans MS', 'Comic Sans', cursive;"
                                     "color: #060b14;}")

        self.url_input.setPlaceholderText("YouTube muzik adresini giriniz")

        self.download_button = QPushButton("Indir")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setStyleSheet("QPushButton { border-radius: 2px; padding: 10px;"
                                           "background-color: #128c7e;"
                                           "color: #e5ded4;"
                                           "font-family: 'Comic Sans MS', 'Comic Sans', cursive;"
                                           "border-radius: 10px;}")

        horizontal_layout = QHBoxLayout()
        self.file_path_input = QLineEdit(self)
        self.file_path_input.setText(RELATIVE_DIR)
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setStyleSheet("QLineEdit { border-radius: 10px; padding: 10px;"
                                           "background-color: #e5ded4;"
                                           "font-family: 'Comic Sans MS', 'Comic Sans', cursive;"
                                           "color: #060b14;}")

        button = QPushButton("Indirme Konumu", self)
        button.setStyleSheet("QPushButton { border-radius: 2px; padding: 10px;"
                             "background-color: #128c7e;"
                             "color: #e5ded4;"
                             "font-family: 'Comic Sans MS', 'Comic Sans', cursive;"
                             "border-radius: 10px;}")
        button.clicked.connect(self.show_folder_dialog)
        horizontal_layout.addWidget(self.file_path_input)
        horizontal_layout.addWidget(button)

        layout_left.addWidget(self.url_input)

        layout_left.addLayout(horizontal_layout)

        layout_left.addWidget(self.download_button)
        layout_left.addWidget(self.progress_bar)
        self.listWidget = QListWidget()
        self.listWidget.setStyleSheet("QListWidget { border-radius: 10px; padding: 10px;"
                                     "background-color:#128c7e;"
                                     "font-family: 'Comic Sans MS', 'Comic Sans', cursive;"
                                     "color: #060b14;}")

        self.playpushButton = QtWidgets.QPushButton()
        self.playpushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.playpushButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(f"{BASE_DIR}/images/Play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.altidokuzpushButton = QtWidgets.QPushButton()
        self.altidokuzpushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.altidokuzpushButton.setText("")
        icon69 = QtGui.QIcon()
        icon69.addPixmap(QtGui.QPixmap(f"{BASE_DIR}/images/Create.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.altidokuzpushButton.setIcon(icon69)

        self.altidokuzpushButton.setIconSize(QtCore.QSize(24, 24))
        self.altidokuzpushButton.setFlat(True)
        self.altidokuzpushButton.setObjectName("Add")

        self.playpushButton.setIcon(icon1)
        self.playpushButton.setIconSize(QtCore.QSize(24, 24))
        self.playpushButton.setFlat(True)
        self.playpushButton.setObjectName("playpushButton")
        self.pausepushButton = QtWidgets.QPushButton()
        self.pausepushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pausepushButton.setText("")

        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(f"{BASE_DIR}/images/Pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pausepushButton.setIcon(icon2)
        self.pausepushButton.setIconSize(QtCore.QSize(24, 24))
        self.pausepushButton.setFlat(True)
        self.pausepushButton.setObjectName("pausepushButton")
        self.stoppushButton = QtWidgets.QPushButton()
        self.stoppushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.stoppushButton.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(f"{BASE_DIR}/images/Stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stoppushButton.setIcon(icon3)
        self.stoppushButton.setIconSize(QtCore.QSize(24, 24))
        self.stoppushButton.setFlat(True)
        self.stoppushButton.setObjectName("stoppushButton")
        # self.horizontalLayout_2.addWidget(self.stoppushButton)
        self.previouspushButton = QtWidgets.QPushButton()
        self.previouspushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.previouspushButton.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(f"{BASE_DIR}/images/Previous.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.previouspushButton.setIcon(icon4)
        self.previouspushButton.setIconSize(QtCore.QSize(24, 24))
        self.previouspushButton.setFlat(True)
        self.previouspushButton.setObjectName("previouspushButton")
        # self.horizontalLayout_2.addWidget(self.previouspushButton)
        self.nextpushButton = QtWidgets.QPushButton()
        self.nextpushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.nextpushButton.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(f"{BASE_DIR}/images/Next.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.nextpushButton.setIcon(icon5)
        self.nextpushButton.setIconSize(QtCore.QSize(24, 24))
        self.nextpushButton.setFlat(True)
        self.nextpushButton.setObjectName("nextpushButton")

        self.altidokuzpushButton = QtWidgets.QPushButton()
        self.altidokuzpushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.altidokuzpushButton.setText("")
        icon69 = QtGui.QIcon()
        icon69.addPixmap(QtGui.QPixmap(f"{BASE_DIR}/images/Create.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.altidokuzpushButton.setIcon(icon69)

        self.altidokuzpushButton.setIconSize(QtCore.QSize(24, 24))
        self.altidokuzpushButton.setFlat(True)
        self.altidokuzpushButton.setObjectName("Add")

        self.volumeSlider = QtWidgets.QSlider()
        self.volumeSlider.setMinimumSize(QtCore.QSize(250, 0))
        self.volumeSlider.setMaximumSize(QtCore.QSize(250, 16777215))
        self.volumeSlider.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setSingleStep(1)
        self.volumeSlider.setProperty("value", 50)
        self.volumeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.volumeSlider.setInvertedAppearance(False)
        self.volumeSlider.setInvertedControls(False)
        self.volumeSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.volumeSlider.setTickInterval(10)
        self.volumeSlider.setObjectName("volumeSlider")

        self.musicSlider = QtWidgets.QSlider()
        self.musicSlider.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.musicSlider.setOrientation(QtCore.Qt.Horizontal)
        self.musicSlider.setObjectName("musicSlider")

        play_main_buttons_h_layout = QHBoxLayout()

        play_buttons_h_layout = QHBoxLayout()
        play_buttons_h_layout.addWidget(self.playpushButton)
        play_buttons_h_layout.addWidget(self.pausepushButton)
        play_buttons_h_layout.addWidget(self.stoppushButton)
        play_buttons_h_layout.addWidget(self.previouspushButton)
        play_buttons_h_layout.addWidget(self.nextpushButton)
        play_buttons_h_layout.addWidget(self.altidokuzpushButton)
        play_slider_h_layout = QHBoxLayout()

        self.end_time_label = QtWidgets.QLabel()
        self.start_time_label = QtWidgets.QLabel()
        self.start_time_label.setObjectName("start_time_label")
        self.end_time_label.setObjectName("end_time_label")
        play_slider_h_layout.addWidget(self.start_time_label)
        play_slider_h_layout.addWidget(self.musicSlider)
        play_slider_h_layout.addWidget(self.end_time_label)
        play_main_buttons_h_layout.addLayout(play_buttons_h_layout)
        layout_right.addWidget(self.listWidget)
        volume_horizontal_layout = QHBoxLayout()
        self.volume_label = QLabel()
        self.volume_label.setText("Ses:")
        self.volume_label.setStyleSheet("QLabel {"
                                        "color: #e5ded4;"
                                        "font-family: 'Comic Sans MS', 'Comic Sans', cursive;"
                                        "border-radius: 10px;}")
        volume_horizontal_layout.addWidget(self.volume_label)
        volume_horizontal_layout.addWidget(self.volumeSlider)
        layout_right.addLayout(volume_horizontal_layout)
        layout_right.addLayout(play_main_buttons_h_layout)
        layout_right.addLayout(play_slider_h_layout)
        top_layout.addLayout(layout_left)
        top_layout.addLayout(layout_right)
        # Inits
        self.current_songs = []
        self.current_volume = 50
        global stopped
        stopped = False
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setVolume(self.current_volume)

        # Slider Timer
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.move_slider)

        # Connections
        self.musicSlider.sliderMoved[int].connect(lambda: self.player.setPosition(self.musicSlider.value()))
        self.volumeSlider.sliderMoved[int].connect(lambda: self.volume_changed())
        self.altidokuzpushButton.clicked.connect(self.add_songs)
        self.playpushButton.clicked.connect(self.play_song)
        self.pausepushButton.clicked.connect(self.pause_and_unpause)
        self.nextpushButton.clicked.connect(self.next_song)
        self.previouspushButton.clicked.connect(self.previous_song)
        self.stoppushButton.clicked.connect(self.stop_song)

        self.setLayout(top_layout)
        self.setFixedSize(800, 600)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f94c57"))  # YouTube red color
        self.download_thread = None
        self.setPalette(palette)

    def move_slider(self):
        if stopped:
            return
        else:
            if self.player.state() == QMediaPlayer.PlayingState:
                self.musicSlider.setMinimum(0)
                self.musicSlider.setMaximum(self.player.duration())
                slider_position = self.player.position()
                self.musicSlider.setValue(slider_position)

                current_time = time.strftime('%H:%M:%S', time.localtime(self.player.position() / 1000))
                song_duration = time.strftime('%H:%M:%S', time.localtime(self.player.duration() / 1000))
                self.start_time_label.setText(f"{current_time}")
                self.end_time_label.setText(f"{song_duration}")

    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, caption='Add Songs',
            directory=RELATIVE_DIR, filter="Supported Files (*.mp3;*.mpeg;*.ogg;*.m4a;*.MP3;*.wma;*.acc;*.amr)"
        )
        if files:
            for file in files:
                self.current_songs.append(file)
                self.listWidget.addItem(os.path.basename(file))

    def play_song(self):
        try:
            global stopped
            stopped = False

            current_selection = self.listWidget.currentRow()
            current_song = self.current_songs[current_selection]

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()
        except Exception as e:
            print(f"Play song error: {e}")

    def pause_and_unpause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def next_song(self):
        try:
            current_selection = self.listWidget.currentRow()
            if current_selection + 1 == len(self.current_songs):
                next_index = 0
            else:
                next_index = current_selection + 1
            current_song = self.current_songs[next_index]
            self.listWidget.setCurrentRow(next_index)
            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()
        except Exception as e:
            print(f"Next song error: {e}")

    def previous_song(self):
        try:
            current_selection = self.listWidget.currentRow()

            if current_selection == 0:
                previous_index = len(self.current_songs) - 1
            else:
                previous_index = current_selection - 1

            current_song = self.current_songs[previous_index]
            self.listWidget.setCurrentRow(previous_index)
            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()
        except Exception as e:
            print(f"Previous song error: {e}")

    def stop_song(self):
        self.player.stop()
        self.musicSlider.setValue(0)
        self.start_time_label.setText(f"00:00:00")
        self.end_time_label.setText(f"00:00:00")

    def volume_changed(self):
        try:
            self.current_volume = self.volumeSlider.value()
            self.player.setVolume(self.current_volume)
            self.volume_label.setText(f"{self.current_volume}")
        except Exception as e:
            print(f"Changing volume error: {e}")

    def remove_one_song(self):
        current_selection = self.listWidget.currentRow()
        self.current_songs.pop(current_selection)
        self.listWidget.takeItem(current_selection)

    def remove_all_songs(self):
        self.stop_song()
        self.listWidget.clear()
        self.current_songs.clear()

    def show_folder_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", options=options)
        print("New file path", self.folder_path)

        if self.folder_path:
            self.file_path_input.setText(self.folder_path)

    def show_success_message(self, err_mesage='', error_=None):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Muzik Indirme Durum")

        if error_:
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText(f"Download failed: {err_mesage}")
        else:
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Indirme Basarili")
            msg_box.setText("Muzik dosyasi basarili bir sekilde indirilmistir.")

        msg_box.exec()

    def download_music(self):
        download_path = self.folder_path

        url = self.url_input.text()
        if url:
            try:
                yt = YouTube(url)
                audio_stream = yt.streams.filter(only_audio=True).first()

                if audio_stream:
                    audio_stream.download(output_path=download_path, filename=f"{audio_stream.title}.mp3")

            except Exception as e:
                _error_message = f"Indirilirken asagidaki hata olustu: {str(e)}"
                self.show_success_message(_error_message, True)
        else:
            _error_message = "Lütfen bir youtube muzik linki giriniz."
            self.show_success_message(_error_message, True)

    def prepLink(self, link, path):
        video_url = link
        video_info = youtube_dl.YoutubeDL().extract_info(
            url=video_url, download=False
        )
        try:
            for singleVideoInfo in video_info['entries']:
                self.download_video(singleVideoInfo, path)
        except KeyError:
            self.download_video(video_info, path)

    def download_video(self, videoInfo, path):
        try:
            filename = f"{path}/{videoInfo['title']}.mp3"
            options = {
                'format': 'bestaudio/best',
                'keepvideo': False,
                'outtmpl': filename,
            }
            print(f"[script] downloading {videoInfo['title']}")

            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([videoInfo['webpage_url']])
        except:
            print("error occured with one video")

    def update_progress(self, progress):
        print("progress:", progress)
        self.progress_bar.setValue(int(progress))
        if progress == 100:
            self.show_success_message(err_mesage='', error_=None)

    def start_download(self):
        local_path = self.folder_path
        video_url = self.url_input.text()
        if not self.download_thread or not self.download_thread.isRunning():
            self.progress_bar.setValue(0)
            self.download_thread = DownloadThreadPyTube(video_url, local_path)
            self.download_thread.progress_update.connect(self.update_progress)
            self.download_thread.start()

def main():
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
