import pygame
import pygame.freetype

class ScrollText:
    def __init__(self, surface, text, vpos, color=(0,0,0), size=50):
        self.surface = surface
        self.text = text
        self.vpos = vpos
        self.width = surface.get_width()
        self.position = self.width
        self.color = color
        self.size = size
        self.font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), self.size)
        self.text_surface, _ = self.font.render(self.text, self.color)
        self.scroll_speed = 4
              
    def update(self):
        self.surface.blit(self.text_surface, (self.position, self.vpos))
        if self.position+self.text_surface.get_width() > 0:
            self.position -= self.scroll_speed
        else:
            self.position = self.width
            
text_list = ["Hi, would you like some hand sanitizer?",
        "Would you like to see a video on how to do it?",
        "Great, just put your hand under the dispenser, please!",
        "Okay, here's the video",
        "Sorry, I didn't hear you. Would you like some hand sanitizer?",
        "Sorry, I didn't hear you. Would you like to see a video?",
        "Okay, have a nice day!",
        "Sorry, I do not understand. Have a nice day!",
        "It's important to sanitize your hands often",
        "Hey, have you remembered to use hand sanitizer lately?",
        "Remember to rub your hands for 30 seconds",
        "Thanks for caring!"]

text_list_da = ["Hej, kunne du tænke dig noget håndsprit?",
                "Vil du se en video om hvordan man gør?",
                "Så bare put din hånd under automaten",
                "Okay, her er videoen",
                " ",
                " ",
                "Okay, hav en god dag!",
                " ",
                " ",
                " ",
                "Husk at gnide dine hænder i mindst 30 sekunder",
                "Husk at gnide hænderne i 30 sekunder. Du kan følge nedtællingen på skærmen",
                " "]

ozText = ["Hey, there!", "Hello!", "Howdy!", "Hey, do you have a minute?", "Would you like some hand sanitizer?",
          "Did you sanitize your hands recently?", "Do you want to clean your hands?", "Great, just put your hand under the dispenser, please!",
          "Okay, maybe next time", "OK, but it's important to  sanitize your hands often", "But it's important to sanitize your hands often",
          "But your really should sanitize your hands at this point", "Do you want to watch a video on how to properly rub your hands",
          "Remember to rub your hands for at least 30 seconds", "Did you know that hand sanitizer can eliminate many known viruses, including the corona virus?",
          "Did you know that frequent hand sanitization can reduce the spread of the epidemic?",
          "Did you know it's recommended to use hand sanitizer whenever you can't wash your hands?",
          "Remember to keep a distance of at least one meter from other people whenever possible",
          "Have a nice day!", "Have a nice day and remember to keep your hands clean!"]

font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 75)
font_color = (0,0,0)
max_length = 20


def createTextSurface(surface, index, tsh, tsw, woz, lang):
    
    if woz:
        text = ozText[index]
    elif lang == "da-DK":
        text = text_list_da[index]
    else:
        text = text_list[index]
    surf_list = []
    
    while(len(text) > max_length):
        split_index = text.rfind(" ", 0, max_length)
        new_line = text[:split_index]
        text = text[split_index:]
        new_surf, _ = font.render(new_line, font_color)
        surf_list.append(new_surf)
    
    new_surf, _ = font.render(text, font_color)
    surf_list.append(new_surf)

    return surf_list

