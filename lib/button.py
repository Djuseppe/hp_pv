import RPi.GPIO as GPIO
from relay import Pump as Relay

GPIO.setmode(GPIO.BCM)


# def main():
#     GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#     GPIO.add_event_detect(27, GPIO.RISING)
#     GPIO.add_event_callback(27, lambda: print('pushed'))


def main():
    from time import sleep
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)  # Set's GPIO pins to BCM GPIO numbering
    INPUT_PIN = 27
    GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    light = Relay(13)

    def input_on(channel):
        light.turn_on()
        print('pushed ON')
        sleep(5)
        light.turn_off()

    GPIO.add_event_detect(INPUT_PIN, GPIO.BOTH, callback=input_on, bouncetime=200)

    # Start a loop that never ends
    while True:
        print('still running')
        sleep(1)


if __name__ == '__main__':
    main()
