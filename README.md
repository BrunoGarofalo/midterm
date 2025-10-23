New calculation

REPL: performs 2 + 2
→ Originator updates state
→ Create new Memento
→ Caretaker saves memento (undo stack)
→ Subject.notify("save", message)
→ LoggingObserver / AutosaveObserver append the calculation


Undo

REPL: user triggers undo
→ Caretaker pops last memento
→ Originator restores previous state
→ Subject.notify("undo", previous_message)
→ Observers remove last entry from TXT/CSV


Redo

REPL: user triggers redo
→ Caretaker pops from redo stack
→ Originator restores that state
→ Subject.notify("redo", message)
→ Observers re-add the calculation to TXT/CSV