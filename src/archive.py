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
        self.log_folder = ''
        self.language = language
        self.flag = flag
        self.start()

    def start(self):
        self.mkdir()

        self.archive_bin_file()
        self.archive_proto_file()
        self.archive_script_file()
        self.archive_log_file()
        self.remove_temp_pb_file()

    def mkdir(self):
        if self.flag == 'c':
            self.script_folder = global_config.client_script_folder()
            self.bin_folder = global_config.client_bin_folder()
            self.proto_folder = global_config.client_proto_folder()
            self.log_folder = global_config.client_log_folder()
        elif self.flag == 's':
            self.script_folder = global_config.server_script_folder()
            self.bin_folder = global_config.server_bin_folder()
            self.proto_folder = global_config.server_proto_folder()
            self.log_folder = global_config.server_log_folder()
        else:
            raise
        command.mkdir(self.script_folder)
        command.mkdir(self.bin_folder)
        command.mkdir(self.proto_folder)
        command.mkdir(self.log_folder)

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

    def archive_log_file(self):
        file_list = glob('./' + '*.log')
        for file in file_list:
            self.move_file(file, self.log_folder)

    def archive_script_file(self):
        if self.language == global_config.language_type.php:
            command.mkdir(self.script_folder + '/GPBMetadata')
            file_list = glob('./GPBMetadata/*.php')
            for file in file_list:
                self.move_file(file, self.script_folder + 'GPBMetadata/')
            command.mkdir(self.script_folder + '/Data')
            file_list = glob('./Data/*.php')
            for file in file_list:
                self.move_file(file, self.script_folder + 'Data/')
            os.rmdir('GPBMetadata')
            os.rmdir('Data')
        elif self.language == global_config.language_type.java:
            java_list = global_config.java_package().split('.')
            java_folder = ''
            for name in java_list:
                java_folder += name + '/'
            print(java_folder)
            command.mkdir(self.script_folder + 'com/example/data')
            file_list = glob('./{}*.java'.format(java_folder))
            for file in file_list:
                self.move_file(file, self.script_folder + '/' + java_folder)
            os.rmdir(java_folder)
        elif self.language == global_config.language_type.kotlin:
            command.mkdir(self.script_folder + '/Data')
            file_list = glob('./Data/*.kt')
            for file in file_list:
                self.move_file(file, self.script_folder + 'Data/')
            os.rmdir('Data')
        else:
            if self.language == global_config.language_type.csharp:
                ext = "*.cs"
            elif self.language == global_config.language_type.cplus:
                ext = "*.pb.*"
            elif self.language == global_config.language_type.python:
                ext = "*_pb2.py"
            elif self.language == global_config.language_type.go:
                ext = "*.go"
            elif self.language == global_config.language_type.js:
                ext = "*.js"
            elif self.language == global_config.language_type.objc:
                ext = "*.pbobjc.*"
            else:
                print("Unknown Language Type Archive Failed");
                raise

            file_list = glob('./' + ext)
            for file in file_list:
                self.move_file(file, self.script_folder)

    def archive_bin_file(self):
        if self.flag == 'c':
            ext = global_config.client_file_ext()
        elif self.flag == 's':
            ext = global_config.server_file_ext()

        file_list = glob('./' + '*' + ext)
        for file in file_list:
            self.move_file(file, self.bin_folder)

    def remove_temp_pb_file(self):
        file_list = glob('./' + '*_pb2.py')
        for file in file_list:
            os.remove(file)
