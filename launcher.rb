# -*- coding: sjis -*-

# require "win32ole"
# wsh = WIN32OLE.new("Wscript.Shell")

# ���̋N���X�N���v�g�̃p�X�����ƂȂ�
BASE_ABSOLUTE_PATH = File.dirname(File.expand_path('.', __FILE__))

system("#{BASE_ABSOLUTE_PATH}/venv/pythonw.exe #{BASE_ABSOLUTE_PATH}/scripts/BAT.py")

exit
