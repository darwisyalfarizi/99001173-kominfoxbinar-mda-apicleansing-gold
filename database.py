import sqlite3

def init_db():
    conn = sqlite3.connect('database/clean_text.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS submissions (
                        id_submission INTEGER PRIMARY KEY AUTOINCREMENT,
                        tweet TEXT NOT NULL,
                        hs INTEGER NOT NULL,
                        abusive INTEGER NOT NULL,
                        hs_individual INTEGER NOT NULL,
                        hs_group INTEGER NOT NULL,
                        hs_religion INTEGER NOT NULL,
                        hs_race INTEGER NOT NULL,
                        hs_physical INTEGER NOT NULL,
                        hs_gender INTEGER NOT NULL,
                        hs_other INTEGER NOT NULL,
                        hs_weak INTEGER NOT NULL,
                        hs_moderate INTEGER NOT NULL,
                        hs_strong INTEGER NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS text_outputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        submission_id INTEGER,
                        tweet TEXT NOT NULL,
                        hs INTEGER NOT NULL,
                        abusive INTEGER NOT NULL,
                        hs_individual INTEGER NOT NULL,
                        hs_group INTEGER NOT NULL,
                        hs_religion INTEGER NOT NULL,
                        hs_race INTEGER NOT NULL,
                        hs_physical INTEGER NOT NULL,
                        hs_gender INTEGER NOT NULL,
                        hs_other INTEGER NOT NULL,
                        hs_weak INTEGER NOT NULL,
                        hs_moderate INTEGER NOT NULL,
                        hs_strong INTEGER NOT NULL,
                        FOREIGN KEY(submission_id) REFERENCES submission(id_submission))''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
