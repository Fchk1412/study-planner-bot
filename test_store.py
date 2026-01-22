from bot.store import ExamStore

store = ExamStore()
store.init_db()

uid = 111  # pretend user id
new_id = store.add_exam(uid, "OS", "2026-01-19")
print("Inserted exam id:", new_id)

exams = store.list_exams(uid)
print("Exams:", exams)
