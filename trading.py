import pygame
import random
import sys

pygame.init()

# Screen
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trading Simulator")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)

# Game variables
def reset_game():
    global price, prices, balance, shares, trend, news_timer, news_text
    price = 100
    prices = [price]
    balance = 10000
    shares = 0
    trend = random.uniform(-0.2, 0.2)
    news_timer = 0
    news_text = ""

reset_game()

# Price update
def update_price():
    global price, trend
    change = random.uniform(-2, 2) + trend
    price = max(1, round(price + change, 2))

# News system
def handle_news():
    global trend, news_timer, news_text

    if news_timer <= 0:
        event = random.choice([
            ("Good Earnings 📈", 1.5),
            ("Bad News 📉", -1.5),
            ("Market Crash 💀", -3),
            ("Big Investment 🚀", 3),
            ("Stable Market 😐", 0)
        ])
        news_text = event[0]
        trend = event[1]
        news_timer = random.randint(100, 200)
    else:
        news_timer -= 1

# Trading
def buy():
    global balance, shares, price
    if balance >= price:
        shares += 1
        balance -= price

def sell():
    global balance, shares, price
    if shares > 0:
        shares -= 1
        balance += price

# Draw chart
def draw_chart():
    if len(prices) < 2:
        return

    max_price = max(prices)
    min_price = min(prices)

    scale = 200 / (max_price - min_price + 0.01)

    for i in range(1, len(prices)):
        x1 = i - 1
        x2 = i
        y1 = 400 - (prices[i-1] - min_price) * scale
        y2 = 400 - (prices[i] - min_price) * scale

        pygame.draw.line(screen, (0, 255, 0), (x1, y1), (x2, y2), 2)

# Draw UI
def draw_ui():
    profit = balance + shares * price - 10000

    texts = [
        f"Price: ₹{price}",
        f"Balance: ₹{round(balance,2)}",
        f"Shares: {shares}",
        f"Net Worth: ₹{round(balance + shares*price,2)}",
        f"Profit: ₹{round(profit,2)}",
        f"News: {news_text}",
        "B = Buy | S = Sell | R = Restart | ESC = Quit"
    ]

    for i, t in enumerate(texts):
        txt = font.render(t, True, (255, 255, 255))
        screen.blit(txt, (20, 20 + i * 25))

# Main loop
running = True
while running:
    screen.fill((10, 10, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                buy()
            if event.key == pygame.K_s:
                sell()
            if event.key == pygame.K_r:
                reset_game()
            if event.key == pygame.K_ESCAPE:
                running = False

    update_price()
    handle_news()

    prices.append(price)
    if len(prices) > WIDTH:
        prices.pop(0)

    draw_chart()
    draw_ui()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()