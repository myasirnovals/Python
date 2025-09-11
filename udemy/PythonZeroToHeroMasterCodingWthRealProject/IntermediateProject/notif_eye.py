from plyer import notification

import time

if __name__ == "__main__":
    while True:
        notification.notify(
            title="Hello",
            message="Hello World",
            timeout=10
        )
        time.sleep(3)

