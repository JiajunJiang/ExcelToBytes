import os
import shutil
from glob import glob

import global_config
from command import command


class archive:
    def __init__(self, language, flag):
        self.bin_folder = ''
        self.proto_folder = ''
        self.script_folder = ''
        self.language = language
        self.flag = flag
        self.start()

    def start(self):
        self.mkdir()

        self.archive_bin_file()
        self.archive_proto_file()
        self.archive_script_file()
        self.remove_temp_pb_file()

    def mkdir(self):
        if self.flag == 'c':
            folder_name = "Client"
        elif self.flag == 's':
            folder_name = "Server"
        else:
            raise

        command.mkdir(folder_name)
        self.script_folder = folder_name + "/script/"
        command.mkdir(self.script_folder)
        self.bin_folder = folder_name + "/bin/"
        command.mkdir(self.bin_folder)
        self.proto_folder = folder_name + "/proto/"
        command.mkdir(self.proto_folder)

    def move_file(self, file, destination):
        file_path, file_name = os.path.split(file)
        if not os.path.exists(destination):
            os.makedirs(destination)
        shutil.move(file, destination + file_name)
        print("move %s -> %s" % (file, destination + file_name))

    def archive_proto_file(self):
        file_list = glob('./' + '*.proto')
        for file in file_list:
            self.move_file(file, self.proto_folder)

    def archive_script_file(self):
        if self.language == global_config.language_type.php:
            command.mkdir(self.script_folder + '/GPBMetadata')
            file_list = glob('./GPBMetadata/*.php')
            for file in file_list:
                self.move_file(file, self.script_folder + '/GPBMetadata')
            command.mkdir(self.script_folder + '/Data')
            file_list = glob('./Data/*.php')
            for file in file_list:
                self.move_file(file, self.script_folder + '/Data')
            os.rmdir('GPBMetadata')
            os.rmdir('Data')
        else:
            if self.language == global_config.language_type.java:
                ext = "*.java"
            elif self.language == global_config.language_type.csharp:
                ext = "*.cs"
            elif self.language == global_config.language_type.cplus:
                ext = "*.pb.*"
            elif self.language == global_config.language_type.python:
                ext = "*_pb2.py"
            elif self.language == global_config.language_type.go:
                ext = "*.go"
            file_list = glob('./' + ext)
            for file in file_list:
                self.move_file(file, self.script_folder)

    def archive_bin_file(self):
        if self.flag == 'c':
            ext = global_config.client_file_ext
        elif self.flag == 's':
            ext = global_config.server_file_ext

        file_list = glob('./' + '*' + ext)
        for file in file_list:
            self.move_file(file, self.bin_folder)

    def remove_temp_pb_file(self):
        file_list = glob('./' + '*_pb2.py')
        for file in file_list:
            os.remove(file)
