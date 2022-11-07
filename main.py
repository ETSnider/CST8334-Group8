import arcade
import random

# screen parameters
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Click and Drag"

# test
# card parameters
# Scaling component of card sizes
CARD_SCALE = 0.6

# ratio component of card sizes
CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

# how big is each mat (spot to put a card on)
MAT_PERCENT_OVERSIZE = 1.25
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT_OVERSIZE)
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT_OVERSIZE)

# how far apart are mats as a percentage of mat size?
VERTICAL_MARGIN_PERCENT = 0.10
HORIZONTAL_MARGIN_PERCENT = 0.10

# how far up should the stockpile and talon be?
BOTTOM_Y = MAT_HEIGHT / 2 + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# How far from the left should the first stack be?
START_X = MAT_WIDTH/2 + MAT_WIDTH*HORIZONTAL_MARGIN_PERCENT

# enums for card values and suits
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]

# face down image
FACE_DOWN_IMAGE = "venv/Lib/site-packages/arcade/resources/images/cards/cardBack_red2.png"
# FACE_DOWN_IMAGE = ":resources:images/cards/cardBack_red2.png"

# how far from the top should the foundations be?
TOP_Y = SCREEN_HEIGHT - MAT_HEIGHT/2 - MAT_HEIGHT*VERTICAL_MARGIN_PERCENT

# how far from the top should the tableau be?
MIDDLE_Y = TOP_Y - MAT_HEIGHT - MAT_HEIGHT*VERTICAL_MARGIN_PERCENT

# how far apart should each mat be?
X_SPACING = MAT_WIDTH + MAT_WIDTH*HORIZONTAL_MARGIN_PERCENT

# How far apart should stacked tableau cards be?
CARD_VERTICAL_OFFSET = CARD_HEIGHT * CARD_SCALE * 0.3

# pile indexes
PILE_COUNT = 13
STOCK = 0
TALON = 1
TABLEAU_1 = 2
TABLEAU_2 = 3
TABLEAU_3 = 4
TABLEAU_4 = 5
TABLEAU_5 = 6
TABLEAU_6 = 7
TABLEAU_7 = 8
FOUNDATION_1 = 9
FOUNDATION_2 = 10
FOUNDATION_3 = 11
FOUNDATION_4 = 12

# standard(3) or Vegas(1)
GAME_RULE = 3

# keep track of vegas score between games
VEGAS_SCORE = 0

class Card(arcade.Sprite):
    def __init__(self, value, suit, scale):
        self.suit = suit
        self.value = value

        self.image_file_name = f"venv/Lib/site-packages/arcade/resources/images/cards/card{self.suit}{self.value}.png"
        # self.image_file_name = f":resources:images/cards/card{self.suit}{self.value}.png"
        self.is_face_up = False

        super().__init__(FACE_DOWN_IMAGE, scale, hit_box_algorithm="None")

    def face_down(self):
        self.is_face_up = False
        self.texture = arcade.load_texture(FACE_DOWN_IMAGE)

    def face_up(self):
        self.is_face_up = True
        self.texture = arcade.load_texture(self.image_file_name)

    def is_face_down(self):
        return not self.is_face_up


class Game(arcade.Window):
    def __init__(self):
        # add startup stuff here
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.AQUAMARINE)  # can change background color here
        # timer stuff here
        self.total_time = 0.0
        self.timer_text = arcade.Text(
            text="00:00",
            start_x=SCREEN_WIDTH * 3 // 4,
            start_y=TOP_Y,
            color=arcade.color.BLACK,
            font_size=70,
            anchor_x="center",
        )
        self.score = 0
        self.score_text = arcade.Text(
            text="0",
            start_x=SCREEN_WIDTH * 3 // 4,
            start_y=BOTTOM_Y,
            color=arcade.color.BLACK,
            font_size=50,
            anchor_x="center",
        )
        self.win = 0
        self.win_text = arcade.Text(
            text="0",
            start_x=SCREEN_WIDTH * 2 // 4,
            start_y=BOTTOM_Y,
            color=arcade.color.BLACK,
            font_size=50,
            anchor_x="center",
        )
        # sprite list of all cards
        self.card_list = None
        # sprite list of mats
        self.pile_mat_list = None
        # list of piles, each being a list of cards
        self.piles = None

        # list of cards being dragged
        self.held_cards = None
        # and where they were taken from (in case they have to revert)
        self.held_cards_original_position = None

    # DONE: Display winning screen
    def winner(self):
        # set up the win screen
        minutes = int(self.total_time) // 60
        seconds = int(self.total_time) % 60
        # check if standard rule
        if GAME_RULE == 3:
            self.score += 700000 / ((minutes * 60) + seconds)
        self.win = "YOU WIN!"

    def setup(self):
        # set up initial game, or restart game
        # reset timer

        self.win = ""
        self.total_time = 0.0
        # reset score for standard rules
        if GAME_RULE == 3:
            self.score = 0

        # vegas rules starts at -52
        if GAME_RULE == 1:
            self.score = VEGAS_SCORE

        # declare foundations, tableau, stock and talon
        self.pile_mat_list = arcade.SpriteList()
        self.piles = [arcade.SpriteList() for _ in range(PILE_COUNT)]
        # stock
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.BLUE)
        pile.position = START_X, BOTTOM_Y
        self.pile_mat_list.append(pile)
        # talon
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.BLUE)
        pile.position = START_X + X_SPACING, BOTTOM_Y
        self.pile_mat_list.append(pile)
        # tableau
        for i in range(7):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.BLUE)
            pile.position = START_X + i * X_SPACING, MIDDLE_Y
            self.pile_mat_list.append(pile)
        # foundations
        for i in range(4):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.BLUE)
            pile.position = START_X + i * X_SPACING, TOP_Y
            self.pile_mat_list.append(pile)

        # declare and populate card list
        self.card_list = arcade.SpriteList()
        for suit in CARD_SUITS:
            for value in CARD_VALUES:
                card = Card(value, suit, CARD_SCALE)
                card.position = START_X, BOTTOM_Y  # put all cards at bottom left for now
                self.card_list.append(card)

        # shuffle cards
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list.swap(pos1, pos2)

        # declare cards on mouse
        self.held_cards = []
        self.held_cards_original_position = []

        # place cards into stock to start
        for card in self.card_list:
            self.piles[STOCK].append(card)

        # pull from stock to deal
        for pile_no in range(TABLEAU_1, TABLEAU_7 + 1):
            for j in range(pile_no - TABLEAU_1 + 1):
                card = self.piles[STOCK].pop()
                self.piles[pile_no].append(card)
                # spread out cards
                if j == 0:
                    card.position = self.pile_mat_list[pile_no].position
                else:
                    top_card = self.piles[pile_no][-2]
                    card.position = top_card.center_x, top_card.center_y - CARD_VERTICAL_OFFSET
                self.pull_to_top(card)

        # flip top cards of tableau face up
        for pile_no in range(TABLEAU_1, TABLEAU_7 + 1):
            self.piles[pile_no][-1].face_up()

    def on_draw(self):
        # overrides the on_draw from arcade to render the screen
        # clear the screen
        self.clear()
        # draw the mats
        self.pile_mat_list.draw()
        # draw the cards
        self.card_list.draw()
        # draw the timer text
        self.timer_text.draw()
        # draw the score text
        self.score_text.draw()
        # draw the win text
        self.win_text.draw()

    def on_update(self, delta_time):
        # accumulate time
        if self.win != "YOU WIN!":
            self.total_time += delta_time
            # alter the timer text
            minutes = int(self.total_time) // 60
            seconds = int(self.total_time) % 60

            # is this standard rules?
            if GAME_RULE == 3:
                if seconds % 10 == 0 and seconds != 0:
                    self.score -= (2/60)

            self.timer_text.text = f"{minutes:02d}:{seconds:02d}"
        self.score_text.text = f"{round(self.score)}"
        self.win_text.text = f"{self.win}"

        # DONE: check if victory
        if len(self.piles[9]) != 0 and len(self.piles[10]) != 0 and len(self.piles[11]) != 0 and len(self.piles[12]) != 0:
            if self.piles[9][-1].value == "K" and self.piles[10][-1].value == "K" and self.piles[11][-1].value == "K" and self.piles[12][-1].value == "K":
                if self.win != "YOU WIN!":
                    self.winner()

    def on_mouse_press(self, x, y, button, key_modifiers):
        # get list of cards at point where we clicked
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        # check if there were any
        if len(cards) > 0:

            # get top card of stack
            primary_card = cards[-1]
            pile_index = self.get_pile_for_card(primary_card)

            # DONE: add checking for right-click, and try to find a spot for that card in foundation, tableau
            if pile_index != STOCK and button == arcade.MOUSE_BUTTON_RIGHT:
                self.move_card(primary_card)
                return

            if pile_index == STOCK:
                for i in range(GAME_RULE):
                    if len(self.piles[STOCK]) == 0:
                        break
                    card = self.piles[STOCK][-1]
                    card.face_up()
                    card.position = self.pile_mat_list[TALON].position
                    self.piles[STOCK].remove(card)
                    self.piles[TALON].append(card)
                    self.pull_to_top(card)
                return
            # flip if face down
            elif primary_card.is_face_down() and primary_card == self.piles[pile_index][-1]:
                primary_card.face_up()
            # add primary card to hand
            self.held_cards = [primary_card]
            # save its position
            self.held_cards_original_position = [self.held_cards[0].position]
            # and pull it to the top of the rendering order
            self.pull_to_top(self.held_cards[0])

            # is it a stack?
            card_index = self.piles[pile_index].index(primary_card)
            for i in range(card_index+1, len(self.piles[pile_index])):
                card = self.piles[pile_index][i]
                self.held_cards.append(card)
                self.held_cards_original_position.append(card.position)
                self.pull_to_top(card)

        else:
            # clicked on a mat?
            mats = arcade.get_sprites_at_point((x, y), self.pile_mat_list)
            if len(mats) > 0:
                mat = mats[0]
                mat_index = self.pile_mat_list.index(mat)
                # if it is an empty stock mat and standard rules
                if GAME_RULE == 3:
                    if mat_index == STOCK and len(self.piles[STOCK]) == 0:
                        self.score -= 20
                        temp_list = []
                        for card in self.piles[TALON]:
                            temp_list.append(card)
                        for card in reversed(temp_list):
                            card.face_down()
                            self.piles[TALON].remove(card)
                            self.piles[STOCK].append(card)
                            card.position = self.pile_mat_list[STOCK].position

    def move_card(self, card):
        global VEGAS_SCORE

        # get card's current pile
        curr_pile = self.get_pile_for_card(card)
        # check if card is not on top
        if self.piles[curr_pile][-1] != card:
            return
        # check if face down and flip if it is
        if not card.is_face_up:
            card.face_up()
            # check if standard rule
            if GAME_RULE == 3:
                self.score += 5
            return
        for i in range(FOUNDATION_4, TABLEAU_1 - 1, -1):
            # checking foundation
            if i > 8:
                # if ace
                if card.value == "A":
                    if len(self.piles[i]) == 0:
                        card.set_position(self.pile_mat_list[i].center_x, self.pile_mat_list[i].center_y)
                        self.pull_to_top(card)
                        self.piles[i].append(card)
                        self.piles[curr_pile].remove(card)
                        # check if standard rule
                        if GAME_RULE == 3:
                            self.score += 10
                        # check if vegas rules
                        if GAME_RULE == 1:
                            self.score += 3
                            VEGAS_SCORE += 3
                            return VEGAS_SCORE
                        return
                    else:
                        continue
                if len(self.piles[i]) == 0:
                    continue
                # what are the values of the pile and held cards?
                for valueIndex, value in enumerate(CARD_VALUES):
                    if value == card.value:
                        card_value = valueIndex
                    if value == self.piles[i][len(self.piles[i])-1].value:
                        top_value = valueIndex
                # if not ace
                if top_value == card_value - 1 and self.piles[i][-1].suit == card.suit:
                    card.set_position(self.piles[i][0].center_x, self.piles[i][0].center_y)
                    self.pull_to_top(card)
                    self.piles[i].append(card)
                    self.piles[curr_pile].remove(card)
                    # check if standard rule
                    if GAME_RULE == 3:
                        self.score += 10
                    # check if vegas rules
                    if GAME_RULE == 1:
                        self.score += 3
                        VEGAS_SCORE += 3
                        return VEGAS_SCORE
                    return
            # checking tableau
            else:
                # if king
                if card.value == "K":
                    if len(self.piles[i]) == 0:
                        card.set_position(self.pile_mat_list[i].center_x, self.pile_mat_list[i].center_y)
                        self.pull_to_top(card)
                        self.piles[i].append(card)
                        self.piles[curr_pile].remove(card)
                        # check if standard rule
                        if GAME_RULE == 3:
                            self.score += 5
                        return
                    else:
                        continue
                if len(self.piles[i]) == 0:
                    continue
                # what are the values of the pile and held cards?
                for valueIndex, value in enumerate(CARD_VALUES):
                    if value == card.value:
                        card_value = valueIndex
                    if value == self.piles[i][len(self.piles[i])-1].value:
                        top_value = valueIndex
                # are the cards black or red?
                if card.suit == "Spades" or card.suit == "Clubs":
                    card_color = "Black"
                else:
                    card_color = "Red"
                # is the pile card black or red?
                if self.piles[i][len(self.piles[i]) - 1].suit == "Spades" or self.piles[i][len(self.piles[i])-1].suit == "Clubs":
                    top_color = "Black"
                else:
                    top_color = "Red"
                # if not king
                if card_value == top_value - 1 and card_color != top_color:
                    card.set_position(self.piles[i][0].center_x, self.piles[i][0].center_y - (len(self.piles[i]))*CARD_VERTICAL_OFFSET)
                    self.pull_to_top(card)
                    self.piles[i].append(card)
                    self.piles[curr_pile].remove(card)
                    # check if standard rule
                    if GAME_RULE == 3:
                        self.score += 5
                    return

    def on_mouse_release(self, x, y, button, key_modifiers):

        # if no cards held, do nothing
        if len(self.held_cards) == 0:
            return

        # find the closest card to held card, and its pile
        # DONE: alter to drop to pile by dropping on stack as well (currently only drops on mat)
        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_position = True

        # check for collision
        if len(arcade.check_for_collision_with_lists(self.held_cards[0], (self.card_list, self.pile_mat_list))) > 0:
            # which pile?
            pile_index = self.pile_mat_list.index(pile)
            # is it its old pile?
            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                # just return it to its old position
                pass

            # is it on a tableau pile?
            elif TABLEAU_1 <= pile_index <= TABLEAU_7:
                # are there other cards there?
                if len(self.piles[pile_index]) > 0:
                    # DONE: add validity checking here for tableau stacking
                    # what is the top card of the pile?
                    top_card = self.piles[pile_index][len(self.piles[pile_index])-1]
                    held_value = 0
                    top_value = 0

                    # what are the values of the pile and held cards?
                    for valueIndex, value in enumerate(CARD_VALUES):
                        if value == self.held_cards[0].value:
                            held_value = valueIndex
                        if value == top_card.value:
                            top_value = valueIndex

                    # is the held card black or red?
                    if self.held_cards[0].suit == "Spades" or self.held_cards[0].suit == "Clubs":
                        held_color = "Black"
                    else:
                        held_color = "Red"
                    # is the pile card black or red?
                    if top_card.suit == "Spades" or top_card.suit == "Clubs":
                        top_color = "Black"
                    else:
                        top_color = "Red"

                    # is the pile card one value higher than the held card?
                    if top_value - 1 == held_value:
                        # is the pile card a different color than the held card?
                        if held_color != top_color:

                            # move card to proper position
                            for i, dropped_card in enumerate(self.held_cards):
                                dropped_card.position = top_card.center_x, top_card.center_y - CARD_VERTICAL_OFFSET * (1+i)
                                reset_position = False
                            for card in self.held_cards:
                                self.move_card_to_pile(card, pile_index)
                                # check if standard rule
                                if GAME_RULE == 3:
                                    self.score += 5 / len(self.held_cards)

                else:
                    # is the held card a king?
                    # DONE: add checking for kings
                    if self.held_cards[0].value == 'K':
                        for i, dropped_card in enumerate(self.held_cards):
                            dropped_card.position = pile.center_x, pile.center_y - CARD_VERTICAL_OFFSET * i
                            reset_position = False
                        for card in self.held_cards:
                            self.move_card_to_pile(card, pile_index)
                            # check if standard rule
                            if GAME_RULE == 3:
                                self.score += 5 / len(self.held_cards)

            # is it on a foundation pile, and is it only 1 card?
            elif FOUNDATION_1 <= pile_index <= FOUNDATION_4 and len(self.held_cards) == 1:

                # are there other cards there?
                if len(self.piles[pile_index]) > 0:

                    # what is the top card of the pile?
                    top_card = self.piles[pile_index][len(self.piles[pile_index]) - 1]
                    held_value = 0
                    top_value = 0

                    # what are the values of the pile and held cards?
                    for valueIndex, value in enumerate(CARD_VALUES):
                        if value == self.held_cards[0].value:
                            held_value = valueIndex
                        if value == top_card.value:
                            top_value = valueIndex

                    # is the pile card one value lower than the held card?
                    if top_value + 1 == held_value:
                        # is the pile card the same suit as the held card?
                        if self.held_cards[0].suit == top_card.suit:
                            self.held_cards[0].position = pile.position
                            self.move_card_to_pile(self.held_cards[0], pile_index)
                            # check if standard rule
                            if GAME_RULE == 3:
                                self.score += 10
                            reset_position = False
                else:
                    # is the held card an A?
                    # DONE: add validity checking here for foundation (Ace and stacking)
                    if self.held_cards[0].value == 'A':
                        self.held_cards[0].position = pile.position
                        self.move_card_to_pile(self.held_cards[0], pile_index)
                        # check if standard rule
                        if GAME_RULE == 3:
                            self.score += 10
                        reset_position = False

        # for invalid drops
        if reset_position:
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # cards are no longer in hand
        self.held_cards = []

    def on_mouse_motion(self, x, y, dx, dy):
        # if holding a card, move card with mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

    def pull_to_top(self, card: arcade.Sprite):
        # make selected card render at top
        self.card_list.remove(card)
        self.card_list.append(card)

    def get_pile_for_card(self, card):
        # get which pile the given card is in
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index

    def remove_card_from_pile(self, card):
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def move_card_to_pile(self, card, pile_index):
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)

    def on_key_press(self, symbol: int, modifiers: int):
        global GAME_RULE
        global VEGAS_SCORE
        # let player reset with r
        if symbol == arcade.key.R:
            GAME_RULE = 3
            VEGAS_SCORE = 0
            self.setup()
            return GAME_RULE, VEGAS_SCORE
        # DONE: let the player play vegas rules with v
        if symbol == arcade.key.V:
            GAME_RULE = 1
            VEGAS_SCORE -= 52
            self.setup()
            return GAME_RULE, VEGAS_SCORE


def main():
    window = Game()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
