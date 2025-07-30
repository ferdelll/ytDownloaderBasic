import yt_dlp
import os
import re
import subprocess
import platform

class APP:
    commandList = {
        "exit": "Выходит из программы",
        "help": "Выводит справку",
        "download": "Скачивает видео с YouTube по URL",
        "clear": "Очищает консоль",
        "version": "Показывает версию"
    }
    commandArgs = {
        "help": "Принимает название команды для точной справки",
        "download": "Принимает ссылку, путь (опционально) и флаг -f с именем папки (опционально)"
    }
    version = 1.0

    def __init__(self):
        while True:
            command = input("Введите команду или help для помощи: ")
            commandF = command.split()
            
            if not commandF:
                continue
                
            match commandF[0].lower():
                case "exit":
                    break
                case "help":
                    self.callHelpFunc(commandF[1] if len(commandF) > 1 else "default")
                case "clear":
                    self.consoleClear()
                case "download":
                    if len(commandF) > 1:
                        folder_name = "videos"
                        use_folder = True
                        link = None
                        location = os.getcwd()
                        
                        if "-f" in commandF:
                            f_index = commandF.index("-f")
                            if f_index + 1 < len(commandF):
                                folder_name = commandF[f_index + 1]
                                commandF.pop(f_index + 1)
                                commandF.pop(f_index)
                            else:
                                print("Ошибка: Укажите имя папки после флага -f")
                                continue
                        elif "--no-folder" in commandF:
                            use_folder = False
                            commandF.remove("--no-folder")
                        
                        if len(commandF) > 2:
                            link = commandF[1]
                            location = commandF[2]
                        elif len(commandF) > 1:
                            link = commandF[1]
                        else:
                            link = input("Введите ссылку: ")
                        
                        self.download(link, location, folder_name, use_folder)
                    else:
                        tlink = input("Введите ссылку: ")
                        self.download(tlink, os.getcwd(), "videos", True)
                case "version":
                    print(f"Версия приложения: {self.version}")
                case _:
                    print("Ошибка: Неизвестная команда")

    def is_valid_youtube_url(self, url):
        youtube_regex = (
            r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return re.match(youtube_regex, url) is not None

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            print(f"Скачивание: {d['_percent_str']} ({d['_eta_str']} осталось)")
        elif d['status'] == 'finished':
            print("Скачивание завершено, обработка файла...")

    def download(self, link, location=os.getcwd(), folder_name="videos", use_folder=True):
        if not self.is_valid_youtube_url(link):
            print("Ошибка: Неверный YouTube URL")
            return
            
        if not os.path.exists(location):
            print("Ошибка: Указанная директория не существует")
            return
            
        if not os.access(location, os.W_OK):
            print("Ошибка: Нет прав для записи в указанную директорию")
            return
            
        try:
            if use_folder:
                tlocation = os.path.join(location, folder_name)
                if not os.path.exists(tlocation):
                    os.makedirs(tlocation)
            else:
                tlocation = location
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(tlocation, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook]
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            print("Видео успешно скачано!")
            
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", tlocation.replace("/", "\\")])
                elif platform.system() == "Darwin":
                    subprocess.run(["open", tlocation])
                elif platform.system() == "Linux":
                    subprocess.run(["xdg-open", tlocation])
                else:
                    print("Открытие папки не поддерживается на этой ОС")
            except Exception as e:
                print(f"Ошибка при открытии папки: {e}")
                
        except yt_dlp.utils.DownloadError:
            print("Ошибка: Не удалось скачать видео. Проверьте URL или подключение к интернету.")
        except PermissionError:
            print("Ошибка: Нет прав для записи в указанную директорию.")
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")

    def consoleClear(self):
        os.system('cls' if os.name == "nt" else "clear")

    def callHelpFunc(self, arg="default"):
        if arg == "default":
            print("Доступные команды:")
            for cmd, desc in self.commandList.items():
                args = self.requestArgs(cmd)
                print(f"{cmd} - {desc} | {args}")
            print("\nПример использования:")
            print("download https://www.youtube.com/watch?v=example /path/to/save -f my_videos")
            print("download https://www.youtube.com/watch?v=example /path/to/save --no-folder")
        else:
            if arg in self.commandList:
                print(f"{arg} - {self.commandList[arg]} | {self.requestArgs(arg)}")
            else:
                print(f"Ошибка: '{arg}' не является корректной командой")

    def requestArgs(self, val):
        if val in self.commandList:
            return self.commandArgs.get(val, "Для данной команды аргументы не найдены")
        return "Команда не существует"

if __name__ == "__main__":
    APP()