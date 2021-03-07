from price import PriceCalculator
import pygame
import pygame.freetype

class Display():
  def run(self):
    assets = []
    assets.append(PriceCalculator(.2, 0.3, 1/365, 30))
    assets.append(PriceCalculator(.2, 0.6, 1/365, 45))
    assets.append(PriceCalculator(.2, 0.45, 1/365, 90))
    pygame.init()
    font = pygame.font.Font(None, 40)

    display = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Stock Ticker")
    clock = pygame.time.Clock()
    
    self.tickers = ["CMP", "BTM", "LSC"]

    crashed = False
    while not crashed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
        self.prices = list(map(lambda x : x.current_asset_price, assets))
        self.prices = list(map(lambda x : int(max(x, 1.0)), self.prices))
        display.fill((0, 0, 0))
        text_surface = font.render(str("CMP"), False, (255, 255, 255))
        display.blit(text_surface, (100, 300))
        text_surface = font.render(str("BTM"), False, (255, 255, 255))
        display.blit(text_surface, (300, 300))
        text_surface = font.render(str("LSC"), False, (255, 255, 255))
        display.blit(text_surface, (500, 300))
        text_surface = font.render(str(self.prices[0]), False, (255, 255, 255))
        display.blit(text_surface, (100, 400))
        text_surface = font.render(str(self.prices[1]), False, (255, 255, 255))
        display.blit(text_surface, (300, 400))
        text_surface = font.render(str(self.prices[2]), False, (255, 255, 255))
        display.blit(text_surface, (500, 400))
        pygame.display.update()
        clock.tick(10)
        list(map(lambda x : x.time_step(), assets))