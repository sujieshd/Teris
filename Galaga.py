import random
import tkinter as tk


WIDTH = 600
HEIGHT = 800
PLAYER_SPEED = 8
PLAYER_BULLET_SPEED = -12
ENEMY_BULLET_SPEED = 6
ENEMY_HORIZONTAL_STEP = 12
ENEMY_DROP_STEP = 24
ENEMY_MOVE_INTERVAL = 450
FRAME_MS = 16


class GalagaGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Galaga")
        self.root.configure(bg="#05070a")

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg="#05070a",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        self.info = tk.Label(
            root,
            text="",
            fg="#e0f2ff",
            bg="#05070a",
            font=("Consolas", 12),
            justify="left",
            anchor="w",
        )
        self.info.grid(row=1, column=0, sticky="we", padx=10, pady=(0, 10))

        self.keys_pressed: set[str] = set()
        self.player_bullets: list[dict[str, int]] = []
        self.enemy_bullets: list[dict[str, int]] = []
        self.enemies: list[dict[str, int | bool]] = []

        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 65
        self.player_width = 42
        self.player_height = 26
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.game_over = False
        self.paused = False

        self.enemy_direction = 1
        self.enemy_last_move_at = 0
        self.fire_cooldown = 0

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        self.start_new_wave()
        self.update_info()
        self.game_loop()

    def on_key_press(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        self.keys_pressed.add(key)

        if key == "space":
            self.shoot_player_bullet()
        elif key == "p":
            self.paused = not self.paused
        elif key == "r" and self.game_over:
            self.reset_game()

    def on_key_release(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def reset_game(self) -> None:
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self.enemies.clear()
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.game_over = False
        self.paused = False
        self.player_x = WIDTH // 2
        self.enemy_direction = 1
        self.enemy_last_move_at = 0
        self.start_new_wave()

    def start_new_wave(self) -> None:
        self.enemies.clear()
        rows = min(6, 3 + self.wave)
        cols = 8
        x_start = 90
        y_start = 90
        x_gap = 52
        y_gap = 46

        for row in range(rows):
            for col in range(cols):
                enemy_type = 0 if row < 2 else 1
                self.enemies.append(
                    {
                        "x": x_start + col * x_gap,
                        "y": y_start + row * y_gap,
                        "w": 34,
                        "h": 24,
                        "alive": True,
                        "type": enemy_type,
                    }
                )

    def shoot_player_bullet(self) -> None:
        if self.game_over or self.paused:
            return
        if self.fire_cooldown > 0:
            return
        self.player_bullets.append({"x": self.player_x, "y": self.player_y - 18, "r": 4})
        self.fire_cooldown = 8

    def move_player(self) -> None:
        if "left" in self.keys_pressed or "a" in self.keys_pressed:
            self.player_x -= PLAYER_SPEED
        if "right" in self.keys_pressed or "d" in self.keys_pressed:
            self.player_x += PLAYER_SPEED

        half = self.player_width // 2
        self.player_x = max(half, min(WIDTH - half, self.player_x))

    def move_player_bullets(self) -> None:
        for bullet in self.player_bullets:
            bullet["y"] += PLAYER_BULLET_SPEED
        self.player_bullets = [b for b in self.player_bullets if b["y"] > -20]

    def move_enemy_bullets(self) -> None:
        for bullet in self.enemy_bullets:
            bullet["y"] += ENEMY_BULLET_SPEED
        self.enemy_bullets = [b for b in self.enemy_bullets if b["y"] < HEIGHT + 20]

    def move_enemy_swarm(self) -> None:
        now = self.root.winfo_fpixels("1i")
        _ = now

        if self.enemy_last_move_at <= 0:
            self.enemy_last_move_at = self.root.tk.getint(self.root.tk.call("clock", "milliseconds"))

        current_ms = self.root.tk.getint(self.root.tk.call("clock", "milliseconds"))
        if current_ms - self.enemy_last_move_at < max(80, ENEMY_MOVE_INTERVAL - self.wave * 25):
            return

        self.enemy_last_move_at = current_ms
        alive_enemies = [e for e in self.enemies if e["alive"]]
        if not alive_enemies:
            return

        move_sideways = True
        for enemy in alive_enemies:
            next_x = int(enemy["x"]) + ENEMY_HORIZONTAL_STEP * self.enemy_direction
            if next_x - int(enemy["w"]) // 2 < 10 or next_x + int(enemy["w"]) // 2 > WIDTH - 10:
                move_sideways = False
                break

        if move_sideways:
            for enemy in alive_enemies:
                enemy["x"] = int(enemy["x"]) + ENEMY_HORIZONTAL_STEP * self.enemy_direction
        else:
            self.enemy_direction *= -1
            for enemy in alive_enemies:
                enemy["y"] = int(enemy["y"]) + ENEMY_DROP_STEP

    def enemies_fire(self) -> None:
        alive_enemies = [e for e in self.enemies if e["alive"]]
        if not alive_enemies:
            return

        chance = min(0.06, 0.015 + self.wave * 0.004)
        if random.random() < chance:
            shooter = random.choice(alive_enemies)
            self.enemy_bullets.append(
                {"x": int(shooter["x"]), "y": int(shooter["y"]) + int(shooter["h"]) // 2, "r": 5}
            )

    def rect_hit(self, x: int, y: int, rect_x: int, rect_y: int, w: int, h: int) -> bool:
        return rect_x - w // 2 <= x <= rect_x + w // 2 and rect_y - h // 2 <= y <= rect_y + h // 2

    def handle_collisions(self) -> None:
        for bullet in self.player_bullets[:]:
            bx = int(bullet["x"])
            by = int(bullet["y"])
            hit_enemy = None
            for enemy in self.enemies:
                if enemy["alive"] and self.rect_hit(bx, by, int(enemy["x"]), int(enemy["y"]), int(enemy["w"]), int(enemy["h"])):
                    hit_enemy = enemy
                    break
            if hit_enemy is not None:
                hit_enemy["alive"] = False
                self.score += 150 if int(hit_enemy["type"]) == 0 else 100
                if bullet in self.player_bullets:
                    self.player_bullets.remove(bullet)

        px = self.player_x
        py = self.player_y

        for bullet in self.enemy_bullets[:]:
            if self.rect_hit(int(bullet["x"]), int(bullet["y"]), px, py, self.player_width, self.player_height):
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)
                self.player_hit()

        for enemy in self.enemies:
            if not enemy["alive"]:
                continue
            if int(enemy["y"]) + int(enemy["h"]) // 2 >= self.player_y - self.player_height // 2:
                self.game_over = True
                return
            if self.rect_hit(px, py, int(enemy["x"]), int(enemy["y"]), int(enemy["w"]), int(enemy["h"])):
                self.game_over = True
                return

    def player_hit(self) -> None:
        if self.game_over:
            return
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            return

        self.player_x = WIDTH // 2
        self.player_bullets.clear()
        self.enemy_bullets.clear()

    def maybe_next_wave(self) -> None:
        if any(enemy["alive"] for enemy in self.enemies):
            return
        self.wave += 1
        self.start_new_wave()

    def update_info(self) -> None:
        status = "PAUSED" if self.paused and not self.game_over else ("GAME OVER (R to restart)" if self.game_over else "PLAYING")
        self.info.configure(text=f"Score: {self.score}   Lives: {self.lives}   Wave: {self.wave}   Status: {status}")

    def draw_player(self) -> None:
        x = self.player_x
        y = self.player_y
        w = self.player_width
        h = self.player_height

        self.canvas.create_polygon(
            x,
            y - h // 2,
            x - w // 2,
            y + h // 2,
            x,
            y + h // 4,
            x + w // 2,
            y + h // 2,
            fill="#4fc3f7",
            outline="#90caf9",
            width=2,
        )
        self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill="#e1f5fe", outline="")

    def draw_enemies(self) -> None:
        for enemy in self.enemies:
            if not enemy["alive"]:
                continue
            x = int(enemy["x"])
            y = int(enemy["y"])
            w = int(enemy["w"])
            h = int(enemy["h"])

            body_color = "#ff80ab" if int(enemy["type"]) == 0 else "#ffcc80"
            wing_color = "#f50057" if int(enemy["type"]) == 0 else "#ff9800"

            self.canvas.create_oval(x - w // 2, y - h // 2, x + w // 2, y + h // 2, fill=body_color, outline="#311b92")
            self.canvas.create_polygon(
                x - w // 2,
                y,
                x - w,
                y + h // 2,
                x - w // 3,
                y + h // 3,
                fill=wing_color,
                outline="",
            )
            self.canvas.create_polygon(
                x + w // 2,
                y,
                x + w,
                y + h // 2,
                x + w // 3,
                y + h // 3,
                fill=wing_color,
                outline="",
            )

    def draw_bullets(self) -> None:
        for bullet in self.player_bullets:
            x = int(bullet["x"])
            y = int(bullet["y"])
            r = int(bullet["r"])
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#b3e5fc", outline="")

        for bullet in self.enemy_bullets:
            x = int(bullet["x"])
            y = int(bullet["y"])
            r = int(bullet["r"])
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#ff5252", outline="")

    def draw_overlay(self) -> None:
        if self.paused and not self.game_over:
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2,
                text="PAUSED",
                fill="#e3f2fd",
                font=("Consolas", 36, "bold"),
            )

        if self.game_over:
            self.canvas.create_rectangle(50, HEIGHT // 2 - 90, WIDTH - 50, HEIGHT // 2 + 90, fill="#000000", outline="#e57373", width=2)
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2 - 30,
                text="GAME OVER",
                fill="#ff8a80",
                font=("Consolas", 34, "bold"),
            )
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2 + 20,
                text=f"Final Score: {self.score}",
                fill="#ffe0b2",
                font=("Consolas", 16),
            )
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2 + 50,
                text="Press R to Restart",
                fill="#cfd8dc",
                font=("Consolas", 14),
            )

    def render(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_line(0, self.player_y + 25, WIDTH, self.player_y + 25, fill="#1a237e")
        self.draw_player()
        self.draw_enemies()
        self.draw_bullets()
        self.draw_overlay()

    def game_loop(self) -> None:
        if not self.paused and not self.game_over:
            self.move_player()
            self.move_player_bullets()
            self.move_enemy_bullets()
            self.move_enemy_swarm()
            self.enemies_fire()
            self.handle_collisions()
            self.maybe_next_wave()

            if self.fire_cooldown > 0:
                self.fire_cooldown -= 1

        self.update_info()
        self.render()
        self.root.after(FRAME_MS, self.game_loop)


def main() -> None:
    root = tk.Tk()
    game = GalagaGame(root)
    _ = game
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()
