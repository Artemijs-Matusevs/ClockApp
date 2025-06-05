

## 1. Overview  PROOF OF CONCEPT
Python Flask web application to **clock in/out** using a badge reader and track accessed documents in the records room.

Main entry point for this is `index.py`, this contains all of the back-end code. The front-end was built with Jinja templating language, and all of the templates used can be found in the `templates` folder.

As the app is still in production, it runs on the local host of the machine, on port 5000. localhost:5000

Github repo: https://github.com/Artemijs-Matusevs/ClockApp

Note, for testing purposes the secret key is hard coded, this should be replaced by env variables.



---

## 2. Database Schema  
The SQLite database (`database.db`) has 3 tables:  

### **Tables**  
| Table       | Fields                                                             | Purpose                                                       |
| ----------- | ------------------------------------------------------------------ | ------------------------------------------------------------- |
| `users`     | `id`, `full_name`, `hashed_badge` (UNIQUE), `department`           | Table to store users names, hashed badge numbers, department. |
| `documents` | `id`, `document_name`, `department_name`                           | Table to store all documents/departments                      |
| `checkins`  | `id`, `user_id`, `name`, `intime`, `outtime`, `documents_accessed` | Logs check-ins and what documents were accessed.              |

---

## 3. Usage

#### Existing User:
1) Scanned badge gets sent to the back-end, where it's hash is checked to see if the user exists `checkUser(badge_id)`0
2) If user exists, check to see if they are currently clocked in, `is_clocked_in(user_id)`. This function will check to see if a record for that user already exists in the "checkins" table, and if it exists, it will check to see if there's any records with the same user ID and the "outtime" column being"null" (meaning they've already clocked in, and haven't clocked out yet) -> Clock Out.
3) Else: Redirect to document selection.


#### New User  
1) Scanned badge gets sent to the back-end, where it's hash is checked to see if the user exists `checkUser(badge_id)`.
2. Register:  
   - Enter name and department.  
   - Badge number is hashed (using `bcrypt`) and saved in the users table.  
3) Redirect to document selection.

#### Exporting Data  
1) Export checkin table to CSV `/export/<table>`,data is filtered by date range sent from the form on the front-end index template. 1 day is taken away to make the start_date inclusive.

---

## 4. Key Functions  

### Authentication  
- `checkUser(badge_id)` → Compares badge hash to stored values.  
- `new_user()` → Hashes badge ID and saves user name and department to users table.  

### Time Tracking  
- `clock_user_in()` → Logs clock-in time and documents.  
- `clock_user_out()` → Updates `outtime` in database.  
- `is_clocked_in()` → Checks if user is already clocked in.  

### Data Export  
- `/export/<table>` → Exports a table with specific date range to an CSV.

---

## 5. Setup Instructions  

### Dependencies
- Libraries: `flask`, `flask-bcrypt`, `flask-session`, `sqlite3`  

### Set up
1. Clone the repository.  
2. Create a python virtual environment `python -m venv venv`
3. Activate the env `source venv/Scripts/activate`
4. Download/Install dependencies `pip i flask flask-bcrypt flask-session`
5. Create the database `python createDatabase.py`
6. Run the app: `flask --app index run`: Now you can see the app run on http://localhost:5000




