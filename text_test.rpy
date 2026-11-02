define e = Character("Eileen")

define title = "My Visual Novel"
define num = 10
define stay = "stay"

default age = 20
default name = "Eileen"

label start:
    menu:
        "What should I do?"

        "Go outside":
            e "I went outside!"

        "Stay inside":
            jump inside

        "Stay put":
            jump expression stay
    return

label inside:
    e "I stayed inside!"
    return

label stay:
    e "I stayed put!"
    return
