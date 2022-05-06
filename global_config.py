class language_type():
    cplus = 1,
    csharp = 2,
    java = 3,
    go = 4,
    python = 5,
    php = 6,
    js = 7,

global client_language
global server_language
client_language = language_type.cplus
server_language = language_type.cplus

global package_name
package_name = "Data"

# java only
global java_package
java_package = "com.example.data"

# java only
global java_outer_classname
java_outer_classname = "Data"

global java_multiple_files
java_multiple_files = True

# "SPEED" / "CODE_SIZE" / "LITE_RUNTIME"
global optimize_for
optimize_for = "SPEED"

global cc_enable_arenas
cc_enable_arenas = True

# Objective-C only
global objc_class_prefix
objc_class_prefix = "NS"

global client_file_ext
global server_file_ext
client_file_ext = ".bytes"
server_file_ext = ".bin"
