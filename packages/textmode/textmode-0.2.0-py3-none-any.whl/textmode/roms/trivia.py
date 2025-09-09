from textmode import TextmodeConsole, register_rom


@register_rom("trivia")
class TriviaGame:
    async def run(self, console: TextmodeConsole) -> None:
        # Simple trivia using only dialogue(), choices(), and addScore()
        await console.dialogue(
            "Welcome to Trivia! Answer a few questions. +1 point for each correct answer."
        )

        questions = [
            (
                "What is the capital of France?",
                ["Paris", "Rome", "Berlin", "Madrid"],
                "Paris",
            ),
            (
                "2 + 2 = ?",
                ["3", "4", "5"],
                "4",
            ),
            (
                "Which planet is known as the Red Planet?",
                ["Venus", "Mars", "Jupiter"],
                "Mars",
            ),
        ]

        for prompt, options, correct in questions:
            await console.dialogue(prompt)
            choice = await console.choices(options)
            if choice == correct:
                await console.dialogue("Correct!")
                console.addScore(1)
            else:
                await console.dialogue(f"Not quite. The answer was {correct}.")

        await console.dialogue("That's all! Thanks for playing.")
