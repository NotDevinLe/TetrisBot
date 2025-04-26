import numpy as np
from collections import deque
import random
import pygame

pygame.init()

COLORS = {
    0: (255, 255, 255),
    1: (208, 151, 54),
    2: (39, 101, 195),
    3: (232, 211, 81),
    4: (67, 161, 201),
    5: (132, 46, 166),
    6: (95, 200, 79),
    7: (219, 60, 34),
}

SPEED = 20
BOARD_HEIGHT = 20
BOARD_WIDTH = 10
BLOCK_SIZE = 30
BOARD_Y, BOARD_X = 1, 11

BLOCKS = {
    1: [[0,0,1],
        [1,1,1],
        [0,0,0],],
    2: [[1,0,0],
        [1,1,1],
        [0,0,0]],
    3: [[0,0,0,0],
        [0,1,1,0],
        [0,1,1,0],
        [0,0,0,0]],
    4: [[0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0]],
    5: [[0,1,0],
        [1,1,1],
        [0,0,0]],
    6: [[0,1,1],
        [1,1,0],
        [0,0,0]],
    7: [[1,1,0],
        [0,1,1],
        [0,0,0]]
}

class Tetris:
    def __init__(self):
        self.w = (22 + BOARD_WIDTH) * BLOCK_SIZE
        self.h = (2 + BOARD_HEIGHT) * BLOCK_SIZE

        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()

        self.last_fall_time = pygame.time.get_ticks()
        self.fall_interval = 300
    
        self.score = 0
        self.board = np.zeros((20,10), dtype=int)
        self.hold = None
        self.next_pieces = deque()

        for i in range(5):
            self.next_pieces.append(random.randint(1,7))

        id = random.randint(1,7)
        self.curr = [BLOCKS[id], id]
        self.currPos = [5, 0]
        self.hold = None
        self.canHold = True

        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.lock_start_time = None
        self.linesClearedCurrRound = 0
        self.done = False
    
    def check_collision_left(self):
        shape = self.curr[0]
        for r in range(len(shape)):
            for c in range(len(shape[0])):
                if shape[r][c] == 1:
                    board_r = self.currPos[1] + r
                    board_c = self.currPos[0] + c

                    # Check left wall
                    if board_c - 1 < 0:
                        return False

                    # Check for block to the left
                    if self.board[board_r][board_c - 1] != 0:
                        return False
        return True
                    
    def check_collision_right(self):
        shape = self.curr[0]
        for r in range(len(shape)):
            for c in range(len(shape[0])):
                if shape[r][c] == 1:
                    board_r = self.currPos[1] + r
                    board_c = self.currPos[0] + c

                    # Check right wall
                    if board_c + 1 > 9:
                        return False

                    # Check for block to the right
                    if self.board[board_r][board_c + 1] != 0:
                        return False
        return True

    def check_collision_bottom(self):
        shape = self.curr[0]
        for r in range(len(shape)):
            for c in range(len(shape[0])):
                if shape[r][c] != 1:
                    continue

                board_r = self.currPos[1] + r
                board_c = self.currPos[0] + c

                if board_r + 1 >= BOARD_HEIGHT:
                    return True

                if self.board[board_r + 1][board_c] != 0:
                    return True

        return False

    def set_piece(self):
        shape = self.curr[0]
        for r in range(len(shape)):
            for c in range(len(shape[0])):
                if shape[r][c] == 1:
                    board_r = self.currPos[1] + r
                    board_c = self.currPos[0] + c
                    self.board[board_r][board_c] = self.curr[1]
        self.clear_lines()
        self.canHold = True

    def clear_lines(self):
        lines = 0
        for r in range(len(self.board)):
            count = 0
            for c in range(len(self.board[0])):
                if self.board[r][c] != 0:
                    count += 1
            if count == 10:
                lines += 1
                for i in range(r, -1, -1):
                    self.board[i] = self.board[i - 1]
                self.board[0] = np.zeros(10)
        self.score += lines ** 2
        self.linesClearedCurrRound = lines

    def spawn_new_piece(self):
        id = self.next_pieces.popleft()
        self.curr = [BLOCKS[id], id]
        self.next_pieces.append(random.randint(1, 7))
        self.currPos = [5, 0]
        if self.check_collision_bottom():
            self.done = True
    
    def hold_piece(self):
        if self.hold == None:
            self.hold = self.curr[1]
            self.spawn_new_piece()
        else:
            temp = self.hold
            self.hold = self.curr[1]
            self.curr = [BLOCKS[temp], temp]
            self.currPos = [5,0]

            if self.check_collision_bottom():
                self.done = True


    def rotate(self):
        rotated = np.rot90(self.curr[0], -1)  # clockwise
        for r in range(len(rotated)):
            for c in range(len(rotated[0])):
                if rotated[r][c] != 1:
                    continue

                board_r = self.currPos[1] + r
                board_c = self.currPos[0] + c

                # Check bounds
                if board_r < 0 or board_r >= BOARD_HEIGHT or board_c < 0 or board_c >= BOARD_WIDTH:
                    return  # cancel rotation

                # Check collision
                if self.board[board_r][board_c] != 0:
                    return  # cancel rotation

        # If no collision, apply rotation
        self.curr[0] = rotated
        if self.check_collision_bottom():
            self.lock_start_time = pygame.time.get_ticks()

    def play_step(self, action):
        holesBefore = self.getHoles()
        holesAfter = self.getHoles()
        if action == 1:
            if self.check_collision_left():
                self.currPos = [self.currPos[0] - 1, self.currPos[1]]
                if self.check_collision_bottom():
                    self.lock_start_time = pygame.time.get_ticks()
        elif action == 2:
            if self.check_collision_right():
                self.currPos = [self.currPos[0] + 1, self.currPos[1]]
                if self.check_collision_bottom():
                    self.lock_start_time = pygame.time.get_ticks()
        elif action == 3:
            if self.check_collision_bottom():
                self.set_piece()
                holesAfter = self.getHoles()
                self.spawn_new_piece()
            else:
                self.currPos[1] += 1
        elif action == 4:
            self.rotate()
        elif action == 5:
            if self.canHold:
                self.hold_piece()
                self.canHold = False
        elif action == 6:
            while not self.check_collision_bottom():
                self.currPos[1] += 1
            self.set_piece()
            holesAfter = self.getHoles()
            
            self.spawn_new_piece()
            self.canHold = True

        current_time = pygame.time.get_ticks()
        if not self.done:
            if current_time - self.last_fall_time > self.fall_interval:
                if self.check_collision_bottom():
                    if self.lock_start_time is None:
                        self.lock_start_time = pygame.time.get_ticks()
                    elif pygame.time.get_ticks() - self.lock_start_time >= 500:
                        self.set_piece()
                        holesAfter = self.getHoles()
                        self.spawn_new_piece()
                        self.lock_start_time = None
                else:
                    self.currPos[1] += 1
                    self.lock_start_time = None
                self.last_fall_time = current_time

            self.update_ui(self.curr, self.currPos)
            pygame.display.flip()

        return self.getState(), self.getReward(holesBefore, holesAfter), self.done

    def getReward(self, holesBefore, holesAfter):
        reward = self.linesClearedCurrRound ** 2
        self.linesClearedCurrRound = 0
        reward -= 0.02 * (holesAfter - holesBefore)
        reward -= 0.02 * self.getheightSD()
        reward -= 1 if self.done else 0
        reward -= 10 * self.getMaxHeight()

        return reward

    def getHoles(self):
        holes = 0
        for c in range(len(self.board[0])):
            found = False
            for r in range(len(self.board)):
                if self.board[r][c] != 0:
                    found = True
                elif self.board[r][c] == 0 and found:
                    holes += 1
        
        return holes

    def getheightSD(self):
        heights = []
        rows, cols = len(self.board), len(self.board[0])

        for c in range(cols):
            for r in range(rows):
                if self.board[r][c] != 0:
                    heights.append(r)
                    break
        
        for i in range(10 - len(heights)):
            heights.append(20)
        
        return np.std(heights) if heights else 0

    def getMaxHeight(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                if self.board[r][c] != 0:
                    return 10 - r
        return 0

    def update_ui(self, currPiece, currPos):
        self.display.fill((242, 242, 242))

        # Draw board
        for r in range(1, 21):
            for c in range(11, 21):
                pygame.draw.rect(self.display, (255, 255, 255), pygame.Rect(c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(self.display, (205,205,205), pygame.Rect(c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), width=1)

        # Draw current piece
        for r in range(len(currPiece[0])):
            for c in range(len(currPiece[0])):
                if currPiece[0][r][c] == 1:
                    block_coords = [BOARD_Y + r + currPos[1], BOARD_X + c + currPos[0]]
                    pygame.draw.rect(self.display, COLORS[currPiece[1]], pygame.Rect(block_coords[1] * BLOCK_SIZE, block_coords[0] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.display, (0,0,0), pygame.Rect(block_coords[1] * BLOCK_SIZE, block_coords[0] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), width=2)
        
        # Draw all pieces on board
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                if self.board[r][c] != 0:
                    block_coords = [BOARD_Y + r, BOARD_X + c]
                    pygame.draw.rect(self.display, COLORS[self.board[r][c]], pygame.Rect(block_coords[1] * BLOCK_SIZE, block_coords[0] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.display, (0,0,0), pygame.Rect(block_coords[1] * BLOCK_SIZE, block_coords[0] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), width=2)
        
        # Draw board outline
        pygame.draw.rect(self.display, (0,0,0), pygame.Rect(11 * BLOCK_SIZE, 1 * BLOCK_SIZE, BLOCK_SIZE * 10, BLOCK_SIZE * 20), width=3)
        
        # Hold Piece
        pygame.draw.rect(self.display, (0,0,0), pygame.Rect(3 * BLOCK_SIZE, 1 * BLOCK_SIZE, BLOCK_SIZE * 4, BLOCK_SIZE * 4), width=3)
        if self.hold:
            xMargin, yMargin = 0, 0
            if self.hold == 1 or self.hold == 2 or self.hold == 5 or self.hold == 6 or self.hold == 7:
                xMargin, yMargin = 0.5, 1
            holdShape = BLOCKS[self.hold]
            for c in range(3, 3 + len(holdShape)):
                for r in range(1, 1 + len(holdShape)):
                    if holdShape[r - 1][c - 3] != 0:
                        pygame.draw.rect(self.display, COLORS[self.hold], pygame.Rect((c + xMargin) * BLOCK_SIZE, (r + yMargin) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(self.display, (0,0,0), pygame.Rect((c + xMargin) * BLOCK_SIZE, (r + yMargin) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), width=1)
            
        # Next Piece
        pygame.draw.rect(self.display, (0,0,0), pygame.Rect(24 * BLOCK_SIZE, 1 * BLOCK_SIZE, BLOCK_SIZE * 4, BLOCK_SIZE * 4), width=3)
        xMargin, yMargin = 0, 0
        if self.next_pieces[0] != 4 and self.next_pieces[0] != 3:
            xMargin, yMargin = 0.5, 1
        nextShape = BLOCKS[self.next_pieces[0]]
        for c in range(24, 24 + len(nextShape)):
            for r in range(1, 1 + len(nextShape)):
                if nextShape[r - 1][c - 24] != 0:
                    pygame.draw.rect(self.display, COLORS[self.next_pieces[0]], pygame.Rect((c + xMargin) * BLOCK_SIZE, (r + yMargin) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.display, (0,0,0), pygame.Rect((c + xMargin) * BLOCK_SIZE, (r + yMargin) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), width=1)
        
        # show score
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.display.blit(score_text, (3 * BLOCK_SIZE, 7 * BLOCK_SIZE))
    
    def reset(self):
        self.__init__()
        return self.getState()
    
    def getState(self):
        # One-hot encode the curr piece
        currPiece = np.zeros(7)
        currPiece[self.curr[1] - 1] = 1

        # Normalize the position of the curr piece
        currPos = [self.currPos[0] / 10, self.currPos[1] / 20]

        # One hot encode the next three pieces
        nextPieces = np.zeros(21)
        for i in range(3):
            nextPieces[self.next_pieces[i] - 1 + i * 7] = 1
        
        board = self.board.flatten()

        state = np.concatenate([
            currPiece,
            currPos,
            nextPieces,
            board
        ])

        # Return final state
        return state 