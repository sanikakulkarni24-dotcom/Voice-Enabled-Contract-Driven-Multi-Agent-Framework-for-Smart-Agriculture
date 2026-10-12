from difflib import SequenceMatcher


COMMANDS = {

    "harvest": {
        "task": "Harvest the crop",
        "agent": "Harvesting Agent",
        "machine": "Combine harvester"
    },

    "irrigate": {
        "task": "Irrigate the field",
        "agent": "Irrigation Agent",
        "machine": "Irrigation pump/system"
    },

    "fertilizer": {
        "task": "Apply fertilizer",
        "agent": "Fertilizer Application Agent",
        "machine": "Tractor with fertilizer spreader"
    }
}


ALIASES = {

    "harvest": [
        "harvest",
        "harvesting",
        "harvester",
        "harvested"
    ],

    "irrigate": [
        "irrigate",
        "irrigation",
        "irrigating",
        "water",
        "watering"
    ],

    "fertilizer": [
        "fertilizer",
        "fertilize",
        "fertilizing",
        "fertiliser",
        "fertilise",
        "fertilising"
    ]
}


def similarity(a, b):

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


def find_command(processed_tokens):

    best_command = None
    best_score = 0

    for word in processed_tokens:

        for command, aliases in ALIASES.items():

            for alias in aliases:

                score = similarity(
                    word,
                    alias
                )

                if score > best_score:

                    best_score = score
                    best_command = command

    return best_command, best_score


def show_command(command):

    info = COMMANDS[command]

    print(f"\n   {info['task']}")
    print(f"   Agent: {info['agent']}")
    print(f"   Machine: {info['machine']}")


def confirm_command(
    recognized_text,
    processed_tokens
):

    command, score = find_command(
        processed_tokens
    )

    # ------------------------------------------------
    # HIGH CONFIDENCE
    # ------------------------------------------------

    if command is not None and score >= 0.90:

        print(
            "\nCommand identified successfully."
        )

        show_command(command)

        return {
            "confirmed": True,
            "suggested_command": command,
            "score": score,
            "command_text": recognized_text
        }

    # ------------------------------------------------
    # MEDIUM CONFIDENCE
    # ------------------------------------------------
    # Instead of asking Yes/No for one suggestion,
    # show all available agricultural operations.

    if command is not None and score >= 0.55:

        print(
            "\nI could not confidently identify "
            "the agricultural task."
        )

        print(
            "\nPlease select the intended task:"
        )

        print("\n1. Harvest the crop")
        print("   Agent: Harvesting Agent")
        print("   Machine: Combine harvester")

        print("\n2. Irrigate the field")
        print("   Agent: Irrigation Agent")
        print("   Machine: Irrigation pump/system")

        print("\n3. Apply fertilizer")
        print("   Agent: Fertilizer Application Agent")
        print("   Machine: Tractor with fertilizer spreader")

        print("\n4. Speak the command again")

        choice = input(
            "\nSelect option: "
        ).strip()

        if choice == "1":

            return {
                "confirmed": True,
                "suggested_command": "harvest",
                "score": score,
                "command_text": recognized_text
            }

        if choice == "2":

            return {
                "confirmed": True,
                "suggested_command": "irrigate",
                "score": score,
                "command_text": recognized_text
            }

        if choice == "3":

            return {
                "confirmed": True,
                "suggested_command": "fertilizer",
                "score": score,
                "command_text": recognized_text
            }

        return {
            "confirmed": False,
            "suggested_command": None,
            "score": score,
            "command_text": recognized_text
        }

    # ------------------------------------------------
    # ACTION NOT CLEAR
    # ------------------------------------------------

    print(
        "\nI could not confidently identify "
        "the agricultural task."
    )

    print(
        "\nPlease select the intended task:"
    )

    print("\n1. Harvest the crop")
    print("   Agent: Harvesting Agent")
    print("   Machine: Combine harvester")

    print("\n2. Irrigate the field")
    print("   Agent: Irrigation Agent")
    print("   Machine: Irrigation pump/system")

    print("\n3. Apply fertilizer")
    print("   Agent: Fertilizer Application Agent")
    print("   Machine: Tractor with fertilizer spreader")

    print("\n4. Speak the command again")

    choice = input(
        "\nSelect option: "
    ).strip()

    if choice == "1":

        return {
            "confirmed": True,
            "suggested_command": "harvest",
            "score": 0,
            "command_text": recognized_text
        }

    if choice == "2":

        return {
            "confirmed": True,
            "suggested_command": "irrigate",
            "score": 0,
            "command_text": recognized_text
        }

    if choice == "3":

        return {
            "confirmed": True,
            "suggested_command": "fertilizer",
            "score": 0,
            "command_text": recognized_text
        }

    return {
        "confirmed": False,
        "suggested_command": None,
        "score": 0,
        "command_text": recognized_text
    }