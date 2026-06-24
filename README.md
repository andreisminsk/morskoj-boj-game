# Морской Бой — Morskoj Boj (Sea Battle)

A retro 2D arcade game inspired by the classic Soviet periscope slot machine. Built with Pygame — all graphics and audio are generated procedurally, no external assets needed.

---

## 🇬🇧 English

### How to Play

You command a submarine periscope. Enemy ships cross the horizon — aim, lead your shots, and sink them!

| Control | Action |
|---|---|
| **Mouse** or **← / →** | Rotate periscope (scroll view left/right) |
| **Space**, **Enter**, or **Left Click** | Fire torpedo |
| **R** | Restart (after game over) |
| **Esc** | Quit |

### Rules

- You start with **10 torpedoes**.
- Ships move horizontally across the horizon at different speeds and sizes.
- Torpedoes travel **straight up** — you must **aim ahead** of the ship (lead your target) to score a hit.
- **3 ship types** with different point values:
  - **Destroyer** (green) — fast, small, 1 point
  - **Cruiser** (cyan) — medium, 2 points
  - **Battleship** (red) — slow, large, 3 points
- Score **10 hits** to activate a **Bonus Round** with 10 extra torpedoes.
- The game ends when you run out of torpedoes.

### Installation & Running

```bash
pip install pygame
python morskoj_boj.py
```

---

## 🇷🇺 Русский

### Как играть

Вы управляете перископом подводной лодки. Вражеские корабли пересекают линию горизонта — цельтесь с упреждением и топите их!

| Управление | Действие |
|---|---|
| **Мышь** или **← / →** | Вращать перископ (сдвигать вид влево/вправо) |
| **Пробел**, **Enter** или **Левый клик** | Выстрел торпедой |
| **R** | Перезапуск (после конца игры) |
| **Esc** | Выход |

### Правила

- В начале у вас **10 торпед**.
- Корабли движутся по горизонту с разной скоростью и размером.
- Торпеды летят **прямо вверх** — нужно **стрелять с упреждением** (целиться вперёд по ходу корабля).
- **3 типа кораблей** с разной стоимостью очков:
  - **Эсминец** (зелёный) — быстрый, маленький, 1 очко
  - **Крейсер** (голубой) — средний, 2 очка
  - **Линкор** (красный) — медленный, большой, 3 очка
- Наберите **10 попаданий** для **бонусного раунда** с 10 дополнительными торпедами.
- Игра заканчивается, когда торпеды закончились.

### Установка и запуск

```bash
pip install pygame
python morskoj_boj.py
