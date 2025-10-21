import os
import sys
import subprocess
import time

def check_execv_support():
    try:
        python = sys.executable
        os.execv(python, [python, "-c", "print('test')"])
        return True
    except Exception as e:
        print("os.execv ishlamayapti:", e)
        return False

def check_subprocess_support():
    """
    subprocess ishlashini sinaydi.both
    """
    try:
        p = subprocess.Popen([sys.executable, "-c", "print('otaboyev_sardorbek')"])
        p.wait(timeout=5)
        return p.returncode == 0
    except Exception as e:
        print("subprocess ishlamayapti:", e)
        return False

def restart_with_execv():
    print("os.execv yordamida qayta ishga tushirilmoqda...")
    python = sys.executable
    os.execv(python, [python] + sys.argv)

def restart_with_subprocess():
    print("subprocess yordamida yangi jarayon ishga tushirilmoqda...")
    subprocess.Popen([sys.executable] + sys.argv)
    print("Joriy jarayon tugatilmoqda...")
    sys.exit()

def select_restart_method():
    """
    Qaysi usul ishlashini aniqlaydi va qaytaradi.
    """
    # Diqqat: os.execv haqiqiy test qilish qiyin, chunki u jarayonni almashtiradi
    # Bu erda biz faqat subprocess test qilamiz, execv esa har doim bor deb hisoblaymiz
    # yoki siz serverda shaxsiy test o'tkazishingiz mumkin.
    subprocess_ok = check_subprocess_support()
    
    # Bu yerda oddiy holatda execv mavjud deb taxmin qilamiz
    # Lekin kerak bo'lsa, execv sinovini o'zgartiring yoki olib tashlang.
    execv_ok = True
    
    if execv_ok and subprocess_ok:
        # Ikki usul ham ishlaydi
        print("Ikki usul ham ishlaydi.")
        return "both"
    elif execv_ok:
        print("Faqat os.execv ishlaydi.")
        return "execv"
    elif subprocess_ok:
        print("Faqat subprocess ishlaydi.")
        return "subprocess"
    else:
        print("Hech qanday usul ishlamayapti!")
        return None

def main():
    print("Dastur ishga tushdi (pid:", os.getpid(), ")")
    print("Ishlash metodini tekshiramiz...")
    
    method = select_restart_method()
    
    if method is None:
        print("Qayta ishga tushirish imkoniyati yo'q. Dastur tugaydi.")
        sys.exit(1)

    # Admin tanlovi (buni tashqi fayldan yoki sozlamadan o'qish mumkin)
    # Bu yerda hozir oddiy misol uchun har doim execv ni tanlaymiz,
    # ammo siz admin paneldan tanlab, shu o'zgaruvchiga qiymat berishingiz mumkin
    admin_choice = None
    admin_choice=str(input("Qayta ishga tushirish usulini tanlang (execv/subprocess/both): ")).strip().lower()

    if method == "both":
        # Adminga tanlash uchun: 'execv' yoki 'subprocess'
        # Misol uchun:
        admin_choice = "execv"  # yoki "subprocess"
    else:
        admin_choice = method

    print(f"Bot {admin_choice} usuli bilan qayta ishga tushadi.")

    # Ishni boshlaymiz
    print("Bot ishlamoqda...")
    time.sleep(5)  # Simulyatsiya uchun

    # Qayta ishga tushirish:
    if admin_choice == "execv":
        restart_with_execv()
    elif admin_choice == "subprocess":
        restart_with_subprocess()
    else:
        print("Noto'g'ri qayta ishga tushirish usuli.")
        sys.exit(1)

if __name__ == "__main__":
    main()
