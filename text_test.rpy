define e = Character("Eileen")

define title = "My Visual Novel"
define pi = 3.14

default age = 20
default name = "Eileen"

label start:
    menu:
        "What should I do?"
        "Go outside":
            e "I went outside!"
        "Stay inside":
            e "I stayed inside!"
