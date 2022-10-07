This data is read into sqlite in :memory: db for testing.

omitted sqlite_sequence data because
`object name reserved for internal use: sqlite_sequence`

To create input.db:
```bash
sqlite3 tests/data/input.db
sqlite> .mode csv
sqlite> .import tests/data/Habits.csv Habits
sqlite> .import tests/data/Repetitions.csv Repetitions
sqlite> .exit
```
