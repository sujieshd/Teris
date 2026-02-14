import random
import tkinter as tk


BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
TICK_MS = 450
FAST_TICK_MS = 50


PIECES = {
	"I": [[(0, 1), (1, 1), (2, 1), (3, 1)], [(2, 0), (2, 1), (2, 2), (2, 3)]],
	"O": [[(1, 0), (2, 0), (1, 1), (2, 1)]],
	"T": [
		[(1, 0), (0, 1), (1, 1), (2, 1)],
		[(1, 0), (1, 1), (2, 1), (1, 2)],
		[(0, 1), (1, 1), (2, 1), (1, 2)],
		[(1, 0), (0, 1), (1, 1), (1, 2)],
	],
	"S": [[(1, 0), (2, 0), (0, 1), (1, 1)], [(1, 0), (1, 1), (2, 1), (2, 2)]],
	"Z": [[(0, 0), (1, 0), (1, 1), (2, 1)], [(2, 0), (1, 1), (2, 1), (1, 2)]],
	"J": [
		[(0, 0), (0, 1), (1, 1), (2, 1)],
		[(1, 0), (2, 0), (1, 1), (1, 2)],
		[(0, 1), (1, 1), (2, 1), (2, 2)],
		[(1, 0), (1, 1), (0, 2), (1, 2)],
	],
	"L": [
		[(2, 0), (0, 1), (1, 1), (2, 1)],
		[(1, 0), (1, 1), (1, 2), (2, 2)],
		[(0, 1), (1, 1), (2, 1), (0, 2)],
		[(0, 0), (1, 0), (1, 1), (1, 2)],
	],
}


COLORS = {
	"I": "#00BCD4",
	"O": "#FFEB3B",
	"T": "#9C27B0",
	"S": "#4CAF50",
	"Z": "#F44336",
	"J": "#3F51B5",
	"L": "#FF9800",
	"grid": "#1f1f1f",
	"empty": "#111111",
}


class Tetris:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title("Tetris")
		self.root.configure(bg="#0f0f0f")

		self.canvas = tk.Canvas(
			root,
			width=BOARD_WIDTH * CELL_SIZE,
			height=BOARD_HEIGHT * CELL_SIZE,
			bg="#111111",
			highlightthickness=0,
		)
		self.canvas.grid(row=0, column=0, rowspan=6, padx=(10, 6), pady=10)

		self.info = tk.Label(
			root,
			text="",
			fg="#f0f0f0",
			bg="#0f0f0f",
			justify="left",
			font=("Consolas", 12),
		)
		self.info.grid(row=0, column=1, sticky="nw", padx=(6, 12), pady=(10, 0))

		self.hint = tk.Label(
			root,
			text=(
				"Controls\n"
				"←/→: Move\n"
				"↑: Rotate\n"
				"↓: Soft drop\n"
				"Space: Hard drop\n"
				"P: Pause\n"
				"R: Restart"
			),
			fg="#bbbbbb",
			bg="#0f0f0f",
			justify="left",
			font=("Consolas", 10),
		)
		self.hint.grid(row=1, column=1, sticky="nw", padx=(6, 12), pady=(16, 0))

		self.root.bind("<Left>", lambda _event: self.try_move(-1, 0))
		self.root.bind("<Right>", lambda _event: self.try_move(1, 0))
		self.root.bind("<Down>", lambda _event: self.soft_drop())
		self.root.bind("<Up>", lambda _event: self.rotate())
		self.root.bind("<space>", lambda _event: self.hard_drop())
		self.root.bind("p", lambda _event: self.toggle_pause())
		self.root.bind("P", lambda _event: self.toggle_pause())
		self.root.bind("r", lambda _event: self.reset())
		self.root.bind("R", lambda _event: self.reset())

		self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
		self.current_piece = None
		self.current_rotation = 0
		self.current_x = 3
		self.current_y = 0
		self.score = 0
		self.lines = 0
		self.level = 1
		self.is_game_over = False
		self.is_paused = False
		self.tick_job = None

		self.reset()

	def reset(self) -> None:
		if self.tick_job is not None:
			self.root.after_cancel(self.tick_job)
			self.tick_job = None
		self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
		self.score = 0
		self.lines = 0
		self.level = 1
		self.is_game_over = False
		self.is_paused = False
		self.spawn_piece()
		self.update_info()
		self.draw()
		self.schedule_tick()

	def spawn_piece(self) -> None:
		self.current_piece = random.choice(list(PIECES.keys()))
		self.current_rotation = 0
		self.current_x = 3
		self.current_y = 0
		if not self.is_valid(self.current_x, self.current_y, self.current_rotation):
			self.is_game_over = True

	def get_blocks(self, piece: str, rotation: int):
		rotations = PIECES[piece]
		return rotations[rotation % len(rotations)]

	def is_valid(self, x: int, y: int, rotation: int) -> bool:
		for bx, by in self.get_blocks(self.current_piece, rotation):
			px = x + bx
			py = y + by
			if px < 0 or px >= BOARD_WIDTH or py < 0 or py >= BOARD_HEIGHT:
				return False
			if self.board[py][px] is not None:
				return False
		return True

	def try_move(self, dx: int, dy: int) -> bool:
		if self.is_game_over or self.is_paused:
			return False
		nx = self.current_x + dx
		ny = self.current_y + dy
		if self.is_valid(nx, ny, self.current_rotation):
			self.current_x = nx
			self.current_y = ny
			self.draw()
			return True
		return False

	def rotate(self) -> None:
		if self.is_game_over or self.is_paused:
			return
		nr = self.current_rotation + 1
		if self.is_valid(self.current_x, self.current_y, nr):
			self.current_rotation = nr
		elif self.is_valid(self.current_x - 1, self.current_y, nr):
			self.current_x -= 1
			self.current_rotation = nr
		elif self.is_valid(self.current_x + 1, self.current_y, nr):
			self.current_x += 1
			self.current_rotation = nr
		self.draw()

	def soft_drop(self) -> None:
		if self.is_game_over or self.is_paused:
			return
		if self.try_move(0, 1):
			self.score += 1
			self.update_info()
		else:
			self.lock_piece()

	def hard_drop(self) -> None:
		if self.is_game_over or self.is_paused:
			return
		dropped = 0
		while self.try_move(0, 1):
			dropped += 1
		self.score += dropped * 2
		self.lock_piece()

	def lock_piece(self) -> None:
		for bx, by in self.get_blocks(self.current_piece, self.current_rotation):
			px = self.current_x + bx
			py = self.current_y + by
			self.board[py][px] = self.current_piece
		self.clear_lines()
		self.spawn_piece()
		self.update_info()
		self.draw()

	def clear_lines(self) -> None:
		new_board = [row for row in self.board if any(cell is None for cell in row)]
		cleared = BOARD_HEIGHT - len(new_board)
		while len(new_board) < BOARD_HEIGHT:
			new_board.insert(0, [None for _ in range(BOARD_WIDTH)])
		self.board = new_board

		if cleared > 0:
			self.lines += cleared
			self.level = max(1, self.lines // 10 + 1)
			points = {1: 100, 2: 300, 3: 500, 4: 800}
			self.score += points.get(cleared, 0) * self.level

	def tick(self) -> None:
		self.tick_job = None
		if self.is_game_over:
			self.update_info()
			self.draw()
			return
		if not self.is_paused:
			if not self.try_move(0, 1):
				self.lock_piece()
		self.update_info()
		self.draw()
		self.schedule_tick()

	def schedule_tick(self) -> None:
		speed = max(100, TICK_MS - (self.level - 1) * 35)
		if self.is_paused:
			speed = FAST_TICK_MS
		self.tick_job = self.root.after(speed, self.tick)

	def toggle_pause(self) -> None:
		if self.is_game_over:
			return
		self.is_paused = not self.is_paused
		self.update_info()
		self.draw()

	def update_info(self) -> None:
		status = "GAME OVER" if self.is_game_over else ("PAUSED" if self.is_paused else "Playing")
		self.info.configure(
			text=(
				f"Status: {status}\n"
				f"Score : {self.score}\n"
				f"Lines : {self.lines}\n"
				f"Level : {self.level}"
			)
		)

	def draw_cell(self, x: int, y: int, color: str) -> None:
		x1 = x * CELL_SIZE
		y1 = y * CELL_SIZE
		x2 = x1 + CELL_SIZE
		y2 = y1 + CELL_SIZE
		self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=COLORS["grid"])

	def draw(self) -> None:
		self.canvas.delete("all")
		for y in range(BOARD_HEIGHT):
			for x in range(BOARD_WIDTH):
				cell = self.board[y][x]
				color = COLORS["empty"] if cell is None else COLORS[cell]
				self.draw_cell(x, y, color)

		if not self.is_game_over:
			for bx, by in self.get_blocks(self.current_piece, self.current_rotation):
				px = self.current_x + bx
				py = self.current_y + by
				if 0 <= px < BOARD_WIDTH and 0 <= py < BOARD_HEIGHT:
					self.draw_cell(px, py, COLORS[self.current_piece])


def main() -> None:
	root = tk.Tk()
	Tetris(root)
	root.resizable(False, False)
	root.mainloop()


if __name__ == "__main__":
	main()