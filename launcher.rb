# -*- coding: sjis -*-

# require "win32ole"
# wsh = WIN32OLE.new("Wscript.Shell")

# この起動スクリプトのパスが基底となる
BASE_ABSOLUTE_PATH = File.dirname(File.expand_path('.', __FILE__))

Dir.chdir("#{BASE_ABSOLUTE_PATH}/scripts") do

  # cd 先での処理を書く
  system("#{BASE_ABSOLUTE_PATH}/venv/pythonw.exe ./BAT.py")
end

exit
