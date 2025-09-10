import time


def sleep_with_countdown(seconds: int) -> None:
    """
    Sleep for a specified number of seconds, displaying a countdown in the console.

    :param seconds:
        Number of seconds to sleep.
    :return:
        None
    """
    for seconds_left in range(seconds, 0, -1):
        print(f"\r{seconds_left}s left ", end="")
        time.sleep(1)
    print("\r ", end="")


def beep_sound_with_pause(
    action_time: int = 1,
    pause_time: int = 0,
    repeat: int = 1,
    action_text=str,
    pause_text=str,
) -> None:
    """
    Play a beep sound with specified action and pause times.
    This function will beep for the specified action time, then pause for the specified pause time,
        repeating this process for the specified number of repeats.

    :param action_time:
        Time in seconds to play the beep sound.
        Default is 1 second.
    :param pause_time:
        Time in seconds to pause between beeps.
        Default is 0 seconds.
    :param repeat:
        Number of times to repeat the beep sound.
        Default is 1.
    :param action_text:
        text to display when the action period starts.
    :param pause_text:
        text to display when the pause period starts.
    :return:
        None
    """
    beep_sound("session started!")

    for i in range(repeat):
        beep_sound(action_text + f" for {action_time}s. {i + 1} of {repeat}.")

        sleep_with_countdown(action_time)

        if pause_time > 0:
            beep_sound(f"{pause_text}. Rest for {pause_time}s.")

            sleep_with_countdown(pause_time)
            beep_sound("+" * 10 + " Rest is over! " + "+" * 10 + "\n" * 3)

    beep_sound("session is over!")


def beep_sound(display_text: str | None = None) -> None:
    """
    Play a beep sound.
    This function prints a bell character to the console, which typically triggers a beep sound on most systems.
    If `display_text` is provided, it can be used to display a message alongside the beep,
        but it does not affect the sound.

    :param display_text:
        Optional text to display when the beep is triggered.
        This can be used for logging or user feedback purposes.
    :return:
        None
    """
    if display_text:
        print(display_text)
    print('\a', end=' ')


if __name__ == '__main__':
    beep_sound()
