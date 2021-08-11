# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from pykiwoom.kiwoom import *

kiwoom = Kiwoom()
kiwoom.CommConnect(block = True)
print(kiwoom.GetLoginInfo("USER_ID")  )
kosdaq = kiwoom.GetCodeListByMarket('10')
for i in kosdaq:
    name = kiwoom.GetMasterCodeName(i)
    print(i, ":", name)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
