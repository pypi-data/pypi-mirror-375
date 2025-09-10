from argparse import ArgumentParser

from beepr.beep import beep_sound_with_pause


def get_parser() -> ArgumentParser:
    """
    Parse command line arguments for the beep sound script.

    :return: ArgumentParser object
    """
    parser = ArgumentParser(description="Play a beep sound.")
    parser.add_argument(
        "action_time",
        nargs="?",
        type=int,
        default=0,
        help="Action time in seconds."
    )
    parser.add_argument(
        "pause_time",
        nargs="?",
        type=int,
        default=0,
        help="Pause time in seconds."
    )
    parser.add_argument(
        "repeat",
        nargs="?",
        type=int,
        default=1,
        help="Number of times to repeat the beep sound."
    )
    parser.add_argument(
        "action_message",
        nargs="?",
        type=str,
        default="💻 Work",
        help="Action message to display."
    )
    parser.add_argument(
        "pause_message",
        nargs="?",
        type=str,
        default="🌴 Pause",
        help="Pause message to display."
    )
    return parser


def main() -> None:
    """
    Main function to execute the beep sound.
    """
    args = get_parser().parse_args()

    print(
        "beepr is running with the following parameters: \n"
        f"Action: {args.action_time} \n"
        f"Pause: {args.pause_time} \n"
        f"Repeat: {args.repeat} \n"
        f"Action Message: {args.action_message} \n"
        f"Pause Message: {args.pause_message} \n"
    )

    beep_sound_with_pause(
        action_time=args.action_time,
        pause_time=args.pause_time,
        repeat=args.repeat,
        action_text=args.action_message,
        pause_text=args.pause_message,
    )


if __name__ == "__main__":
    main()
