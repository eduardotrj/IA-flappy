import pygame
import neat
import time
import os
import random
import pickle

pygame.font.init()


WIN_WIDTH = 560
WIN_HEIGHT = 900
GEN = 0


"Load images"
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
    """ Build a bird object.
    """

    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5
    
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        
    def jump(self):
        """Move the position up and resent the tick_count
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
        
    def move(self):
        self.tick_count += 1
        
        d = self.vel*self.tick_count + 1.5*self.tick_count**2
        
        if d >= 16:
            d = 16
            
        if d < 0:
            d -= 2
            
        self.y = self.y + d
        
        "track position if is over or under 0"
        if d < 0 or self.y < self.height +50:
            if self.tilt < self.MAX_ROTATION: #Avoid go over max rotation.
                self.tilt = self.MAX_ROTATION
                
        else: #It's means go down → negative rotation.
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
                
                
    def draw(self, win):
        """
        Check the current image show and draw the next one in order 0→1→2→1→0.
        If the rotation is over -80, Reset the image (means is falling not flying)

        Args:
            win (_type_): _description_
        """
        self.img_count += 1  #
        
        
        if self.img_count <self.ANIMATION_TIME:
            self.img = self.IMGS[0]
           
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
            
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
            
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
            
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
            
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
            
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        # Rotate the image using the own image and not the corner of the window.
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)
        
    def get_mask(self):
        """
        adasd
        """
        return pygame.mask.from_surface(self.img)
    
class Pipe:
    GAP = 200
    VEL = 5
    
    def __init__(self, x) -> None:
        self.x = x
        self.height = 0
        self.gap = 100
        
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.passed = False
        self.set_height()
        
    def set_height(self):
        """
        Define the height position where to draw the pipe between a range.
        Adapt it to each pipe type (TOP or BOTTOM)
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
        
    def move(self):
        """ Select the speed move for the pipes in the screen """
        self.x -= self.VEL
        
    def draw(self, win):
        """ Print the elements in the screen """
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        
    def collide(self, bird):
        """Determinate when collide between pipes and bird happens.

        Args:
            bird (_type_): _description_
            win (_type_): _description_
        """
        
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        
        # To find the collide point.
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(bottom_mask, top_offset)
        
        if t_point or b_point:
            return True     #collide happens.
    
        return False
        
        
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    def __init__(self, y) -> None:
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        
    def move(self):
        """ Print 2 images and move one after another to generate infinite aspect.
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
            
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
            
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        
        
        #!dd●●●●●●●●●●●●●●●●●●●●●●●●●
class Background:
    VEL = 1
    WIDTH = BG_IMG.get_width()
    IMG = BG_IMG
    
    def __init__(self, y) -> None:
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        
    def move(self):
        """ Print 2 images and move one after another to generate infinite aspect.
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
            
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
            
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

    
def draw_window(win, background, birds, pipes, base, score, gen):
    """
        Draw the window with the elements.

    Args:
        win (_type_): _description_
        bird (_type_): _description_
    """
    #win.blit(BG_IMG, (0,0))   # It could add a slow speed on the background.
    background.draw(win)
    for pipe in pipes:
        pipe.draw(win)    
        
    base.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
    win.blit(text, (10, 10))
    
    # bird.draw(win)
    
    for bird in birds:
        bird.draw(win)
    
    
    pygame.display.update()
    
    
def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []
    
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)
    
    # bird = Bird(230,350)
    
    background = Background(0)
    base = Base(800)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    clock = pygame.time.Clock()
    
    score = 0
    
    
    
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
                
        else:   # not generations
            run = False
            break
        
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1  # bc the loop runs 30tps.
            
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            
            if output[0] > 0.5:
                bird.jump()
                
        #bird.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
                
            
                
            pipe.move()
            
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))
            
        for r in rem:
            pipes.remove(r)
            
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x) 
            
        # if score > 50:
        #     break
            
            
        background.move()
        base.move()
        draw_window(win, background, birds, pipes, base, score, GEN)
        
    # pygame.quit()
    # quit()
        
# main()

def run(config_path):
    """_summary_

    Args:
        config_path (_type_): _description_
    """
    
    config = neat.config.Config(neat.DefaultGenome, 
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)
    
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner = p.run(main,50)  #It execute main(), 50 times.


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_feedforward.txt")
    run(config_path)