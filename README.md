# exam-marking, a tool to make it easy to mark exam questions.

Built for UNSW COMP6[48]41 tutors, because I want to be able to mark in a single window.

```
Usage: exam-marking [OPTIONS] MARKS_PATH

  Reads answers and marks from MARKS_PATH and starts a webserver where you can
  fill in marks. Marks will be saved periodically and when you Ctrl+C the
  process.

Options:
  --import-answers FILENAME       Imports answers from the provided txt file.
                                  Overwrites file at MARKS_PATH. Answers are
                                  expected to be separated by a block of
                                  hashes 20 wide, with the center of the
                                  middle line containing a zID (z[0-9]{7})
                                  with a single space on either side.
  --column <TEXT BOOLEAN INTEGER>...
                                  A set of columns to provide in the marking
                                  interface. Each column should have a name,
                                  either true or false to indicate whether it
                                  is a checkbox or not, and a maximum value
                                  (or the value for true checkboxes).
  --port INTEGER                  Port to use for webserver. Defaults to 8000.
  --help                          Show this message and exit.
```