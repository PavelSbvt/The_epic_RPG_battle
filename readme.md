## Отдельная ветка для сервера

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