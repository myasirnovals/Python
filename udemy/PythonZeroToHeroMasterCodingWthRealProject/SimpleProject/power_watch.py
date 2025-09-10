from plyer import notification
from time import sleep
import psutil

while True:
    battery = psutil.sensors_battery()
    if battery is not None:
        life = battery.percent

        if life < 35:
            notification.notify(
                title="Battery low",
                message=" please connect to a power source!",
                timeout=10
            )
        elif life > 98:
            notification.notify(
                title="Battery full",
                message=" please disconnect the power source!",
                timeout=10
            )
    else:
        print("No battery detected on this system. Exiting.")
        break

    sleep(50)
