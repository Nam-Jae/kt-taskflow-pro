import sys
import os

# backend/ 를 sys.path에 추가해 절대 임포트가 동작하도록 한다
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
