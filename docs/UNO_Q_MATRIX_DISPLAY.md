# UNO Q matrix display guide

The UNO Q's blue LED matrix gives you a quick view of Buddy's state while the full scene plays in your browser. The examples below show the small display animations. For the robot, game pieces, console connection, and detailed messages, open Mission or Setup using the links printed by the UNO Q installer.

## Starting and waiting

When R.O.B. Vision starts or reconnects, an hourglass moves across the matrix. Once the controller is ready, Buddy's eyes appear. They glance around and blink while he waits for a game.

![Three hourglass frames shown while R.O.B. Vision starts](images/matrix-startup.png)

![Buddy's ready eyes, glance, and blink](images/matrix-idle.png)

## Playing a game

Starting Gyromite briefly shows `GY`; starting Stack-Up briefly shows `SU`. Buddy's eyes then return, with a small accent for the selected game. When he accepts a movement command, his eyes react briefly to the action.

![Gyromite and Stack-Up title cues](images/matrix-game-titles.png)

![Gyromite and Stack-Up eye animations](images/matrix-game-eyes.png)

## Test and pairing

| You see | Meaning | What to do |
| --- | --- | --- |
| Moving hourglass | R.O.B. Vision is starting or reconnecting. | Wait for Buddy's eyes. If the hourglass stays, check that the App Lab app is running. |
| Buddy's eyes | The controller is ready. | Open Mission for the selected game and console link. |
| `GY` or `SU` | Gyromite or Stack-Up was selected. | Watch Mission for the virtual game table and **GAME FRAMES LINKED**. |
| Pulsing `T` | The game-frame link recognizes a game's Test signal. | Continue the game's Test check on Setup. A brief steady `T` can also follow a ready-light command. |
| Pulsing `P` | Console pairing is in progress. | Enter the code and fingerprint printed by the console installer on the browser Setup page. |

![The `T` display for a game's Test signal and ready-light command](images/matrix-test.png)

The matrix returns to the game eyes after a Test or ready signal ends. Its small game accents are decoration; use Mission and the game screen to check piece positions and gate responses.
