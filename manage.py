#!/usr/bin/env python
import os
import sys
import threading
import subprocess

def run_bot():
    # Botni alohida jarayon sifatida yurgizamiz
    subprocess.call([sys.executable, 'manage.py', 'run_bot'])

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Agar komanda 'runserver' bo'lsa va bu asosiy jarayon bo'lsa (reloader emas)
    if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django topilmadi...") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()