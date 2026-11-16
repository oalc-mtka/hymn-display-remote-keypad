# Remote Keypad keeps its own Display Timeout

The Remote Keypad draws the Top Display itself and runs its own 7-minute Display Timeout, rather than only imitating key presses and letting the Bottom Display's firmware decide. Nobody remembers why it was built this way, and we're keeping it: it works, and the wiring needed to do otherwise isn't documented yet.

It is safe only because of an operating rule: the Remote Access Switch is off whenever a Song Leader is on the Song Leaders' Bench. Without that rule, a remote Send followed by a Song Number entered on the bench would be blanked early when the Remote Keypad's timer fires. Don't "fix" the duplicate timer without first finding out from the engineers whether the bench firmware has its own Display Timeout.
