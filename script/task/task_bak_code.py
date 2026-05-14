import os
import sys

i=0
script_dir = os.path.abspath(__file__)
while i<4:
    i=i+1
    script_dir = os.path.dirname(script_dir)
    sys.path.append(script_dir)
from 运维管理.Manage.CodeBak2Remote import CodeBak2Remote

CodeBak2Remote('运维管理_代码备份').run()


