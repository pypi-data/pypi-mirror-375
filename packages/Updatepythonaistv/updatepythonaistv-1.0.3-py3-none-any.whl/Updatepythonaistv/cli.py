import argparse
import subprocess
import sys
import os
import getpass

def run_setup():
    """Cài đặt môi trường Termux với các gói cần thiết"""
    cmds = [
        "pkg update -y && pkg upgrade -y",
        "pkg install python git wget curl nano vim termux-api -y",
        "pip install --upgrade pip",
        "pip install requests beautifulsoup4 numpy pandas matplotlib",
        "pip install setuptools wheel twine build",   # 🔥 thêm thư viện để build & upload PyPI
        "termux-setup-storage"
        
    ]
    for cmd in cmds:
        print(f"👉 Running: {cmd}")
        subprocess.call(cmd, shell=True)

def system_info():
    """Trả về thông tin hệ thống"""
    return f"""
    Python: {sys.version}
    Platform: {sys.platform}
    """

def run_upload():
    """Build + Upload package lên PyPI"""
    print("🚀 Đang build và upload package lên PyPI...")

    token = getpass.getpass("🔑 Nhập PyPI Token của bạn: ").strip()
    if not token:
        print("❌ Bạn chưa nhập token!")
        sys.exit(1)

    try:
        # Xóa bản build cũ
        subprocess.run(["rm", "-rf", "dist", "build", "Updatepythonaistv.egg-info"], check=True)

        # Build mới
        subprocess.run([sys.executable, "setup.py", "sdist", "bdist_wheel"], check=True)

        # Upload bằng token nhập thủ công
        subprocess.run([
            "twine", "upload", "dist/*",
            "-u", "__token__",
            "-p", token
        ], check=True)

        print("✅ Upload thành công lên PyPI!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Updatepythonaistv CLI")
    parser.add_argument("action", choices=["setup", "check", "upload"], help="setup / check / upload")

    args = parser.parse_args()

    if args.action == "setup":
        run_setup()
    elif args.action == "check":
        print(system_info())
    elif args.action == "upload":
        run_upload()