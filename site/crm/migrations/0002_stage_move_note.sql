-- A stage move is written once per MOVE_STAGE note: the nightly sync
-- (crm_sync.py) may re-send a move, and a Pantheon move writes its own note,
-- so one note is one move. NULL note_id (a move with no note) stays allowed.
CREATE UNIQUE INDEX IF NOT EXISTS stage_moves_note ON stage_moves(note_id);
