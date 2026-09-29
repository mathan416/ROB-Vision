# UNO Q matrix display guide

The UNO Q's blue LED matrix gives you a quick view of Buddy's state while the full scene plays in your browser. The examples below show the small display animations. For the robot, game pieces, console connection, and detailed messages, open Mission or Setup using the links printed by the UNO Q installer.

## Starting and waiting

After boot, the display shows Router’s neutral animation. Start a registered Gyromite or Stack-Up game and it changes to Buddy’s cues automatically. An hourglass means he is loading or reconnecting; during play his eyes glance and blink. When the game ends, the display returns to neutral.

![Three hourglass frames shown while R.O.B. Vision starts](images/matrix-startup.png)

![Buddy's ready eyes, glance, and blink](images/matrix-idle.png)

## Playing a game

Starting Gyromite briefly shows `GY`; starting Stack-Up briefly shows `SU`. Buddy's eyes then return, with a small accent for the selected game. When he accepts a movement command, his eyes react briefly to the action.

![Gyromite and Stack-Up title cues](images/matrix-game-titles.png)

![Gyromite and Stack-Up eye animations](images/matrix-game-eyes.png)

## Test and pairing

| You see | Meaning | What to do |
| --- | --- | --- |
| Moving hourglass | R.O.B. Vision is starting or reconnecting. | Wait for Buddy's eyes. If the hourglass stays, open the UNO Q’s Apps page and check whether R.O.B. Vision is ready. |
| Router’s neutral animation | No product has an active display request. | Open the UNO Q address to choose an app, or start a registered game. |
| Buddy's eyes | R.O.B. Vision is displaying its game cue. | Open Mission for the selected game and console link. |
| `GY` or `SU` | Gyromite or Stack-Up was selected. | Watch Mission for the virtual game table and **GAME FRAMES LINKED**. |
| Pulsing `T` | The game-frame link recognizes a game's Test signal. | Continue the game's Test check on Setup. A brief steady `T` can also follow a ready-light command. |
| `ID`, certificate characters, `PN`, and digits | Controller Router is confirming device pairing. | Compare the certificate identity, then enter the six-digit Matrix PIN in Router’s secure Pair console page. |

![The `T` display for a game's Test signal and ready-light command](images/matrix-test.png)

The matrix returns to the game eyes after a Test or ready signal ends. Its small game accents are decoration; use Mission and the game screen to check piece positions and gate responses.

During pairing, read the seven-character ID in groups of three, three, and one. After **PN**, join the two groups of three digits, including leading zeroes. The sequence repeats until confirmation or expiry. The page reports whether the connection succeeded.
