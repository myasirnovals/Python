height = float(input("Enter your height in cm: "))
weight = float(input("Enter your weight in kg: "))

height /= 100
BMI = weight / (height * height)

if BMI > 0:
    if BMI < 18.5:
        print("Underweight")
    elif BMI < 25:
        print("Normal")
    elif BMI < 30:
        print("Overweight")
    else:
        print("Obese")
else:
    ("enter a valid details!")
