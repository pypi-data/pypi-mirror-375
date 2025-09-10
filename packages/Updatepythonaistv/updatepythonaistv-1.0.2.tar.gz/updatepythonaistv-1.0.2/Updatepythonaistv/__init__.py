"""
Updatepythonaistv
=================

📦 Thư viện hỗ trợ:
- Cập nhật môi trường Python trên Termux.
- Build và upload package lên PyPI.
- Dùng như công cụ CLI hoặc import trực tiếp trong Python.

Tác giả: Trọng Phúc
GitHub: https://github.com/phuctrong1tuv
"""

__version__ = "1.0.0"
__author__ = "Trọng Phúc"
__email__ = "phuctrongytb16@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/phuctrong1tuv/Updatepythonaistv"

# Import các hàm chính từ core (cli.py hoặc tách riêng core.py)
from .cli import run_setup as setup_env
from .cli import system_info as check_env
from .cli import run_upload as upload_package

# API friendly alias (giống phong cách botaistv)
setup = setup_env
check = check_env
upload = upload_package