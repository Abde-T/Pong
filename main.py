from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')
Config.set('graphics', 'resizable', False)
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.audio import SoundLoader


WINNING_SCORE = 5

class MenuWidget(RelativeLayout):
        def on_touch_down(self, touch):
            if self.opacity == 0:
                return False
            return super(RelativeLayout, self).on_touch_down(touch)
        
class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    menu_title = StringProperty('P  O  N  G')
    menu_button_title = StringProperty('START')
    state_game_has_started = False
    state_game_over = False
    sound_hit = SoundLoader.load("RESOURCES/audio/hit.wav")
    sound_loss = SoundLoader.load("RESOURCES/audio/loss.wav")
    sound_won = SoundLoader.load("RESOURCES/audio/won.wav")
    sound_play = SoundLoader.load("RESOURCES/audio/play.wav")

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self.reset_game()


    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        if not self.state_game_over:

            self.ball.move()

            # player2 Ai
            if self.ball.x > self.width / 2:
                if self.ball.center_y > self.player2.center_y + self.player2.height / 2:
                    self.player2.move_up()
                elif self.ball.center_y < self.player2.center_y - self.player2.height / 2:
                    self.player2.move_down()

            # Bounce off paddles
            self.player1.bounce_ball(self.ball)
            self.player2.bounce_ball(self.ball)

            # Bounce ball off bottom or top
            if (self.ball.y < self.y) or (self.ball.top > self.top):
                self.ball.velocity_y *= -1

            # Went off to a side to score a point?
            if self.ball.x < self.x:
                self.player2.score += 1
                self.serve_ball(vel=(4, 0))
                self.player1.center_y = self.center_y
                self.player2.center_y = self.center_y
            if self.ball.right > self.width:
                self.player1.center_y = self.center_y
                self.player2.center_y = self.center_y
                self.player1.score += 1
                self.serve_ball(vel=(-4, 0))

            # Check for game over
            if self.player1.score == WINNING_SCORE:
                self.end_game('YOU WON', self.sound_won)
            elif self.player2.score == WINNING_SCORE:
                self.end_game('YOU LOST', self.sound_loss)

    def end_game(self, title, sound):
        self.state_game_over = True
        self.menu_title = f'GAME OVER {title}'
        sound.play()
        self.menu_button_title = 'RESTART'
        self.menu_widget.opacity = 1
        self.ball.center = self.center
        print(title.lower())

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.move_down() if touch.y < self.player1.center_y else self.player1.move_up()
       
    def on_menu_button_pressed(self):
        self.reset_game()
        self.serve_ball()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        self.sound_play.play()

    def reset_game(self):
        self.state_game_over = False
        self.player1.score = 0
        self.player2.score = 0
        self.player1.center_y = self.center_y
        self.player2.center_y = self.center_y


    class PongPaddle(Widget):
        score = NumericProperty(0)
        sound_hit = SoundLoader.load("RESOURCES/audio/hit.wav")
        sound_hit.volume = .5

        def bounce_ball(self, ball):
            if self.collide_widget(ball):
                vx, vy = ball.velocity
                offset = (ball.center_y - self.center_y) / (self.height / 2)
                bounced = Vector(-1 * vx, vy)
                vel = bounced * 1.1
                ball.velocity = vel.x, vel.y + offset
                self.sound_hit.play()

        def move_up(self):
            new_y = self.y + 10  # Adjust the movement step as needed
            if new_y + self.height <= self.parent.height:
                self.y = new_y

        def move_down(self):
            new_y = self.y - 10  # Adjust the movement step as needed
            if new_y >= 0:
                self.y = new_y

    class PongBall(Widget):
        velocity_x = NumericProperty(0)
        velocity_y = NumericProperty(0)
        velocity = ReferenceListProperty(velocity_x, velocity_y)

        def move(self):
            self.pos = Vector(*self.velocity) + self.pos


class PongApp(App):
    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    PongApp().run()



    