## RPG battle

---

Все команды выполняются в терминале из **корневой папки проекта**.

Создать виртуальное окружение:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Для установки зависимостей выполните:

```bash
pip install -r requirements.txt
```

Для очистки локального Git от лишнего кеша:
```bash
git rm -r --cached .idea
```
или
```bash
git rm -r --cached -f .idea
```

Установить pyinstaller:
```bash
pip install pyinstaller
```

Собрать spec файл с помощью pyinstaller можно командой:
```bash
pyi-makespec --onedir --contents-directory "." --name EpicRPG  --windowed --icon="resources/images/icons/icon_pdf_maker_255_size.ico" --paths="src" --add-data="resources;resources" --add-data="src;src" --hidden-import="PyQt6" --hidden-import="rich" --hidden-import="PIL" src/main.py  
```

Собрать exe файл с помощью pyinstaller:
```bash
pyinstaller EpicRPG.spec
```

---
> Задание на Codewars:
>
> https://www.codewars.com/kata/66bdf9f511467a75cf5ff88b

![kitten-is-sleeping](doc/images/readme/kitten-is-sleeping.jpg)