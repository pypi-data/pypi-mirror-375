from random import choices

weatherComponent1 = [
    "Sunny", "Rainy", "Snowy", "Hurricane", "Storm", "Rainfall"
]
weatherComponent2 = [
    "precipitation", "excessive flooding of rivers and lakes", "mysterious Fog", "volcanic ash cloud", "unexplained tremors", "alien invasion warning"
]
weatherComponent3 = [
    "bananas", "gummy bears", "used teabags", "half-eaten sandwiches", "tiny plastic ducks", "rubber chickens", "spoons", "the sound of dial-up internet"
]

def check():
    rComponent1_l = choices(weatherComponent1, k=1)
    rComponent2_l = choices(weatherComponent2, k=1)
    rComponent3_l = choices(weatherComponent3, k=1)

    rComponent1 = rComponent1_l[0]
    rComponent2 = rComponent2_l[0]
    rComponent3 = rComponent3_l[0]


    return print(f"{rComponent1} with {rComponent2} in the form of {rComponent3}. Have a nice day!")