# GATI Course Tracker

Tracks the courses brought in by the four GATI sources (Government, Academics, Technology partners, Industries) plus NST, for the Indian Institute of Skills: what is in the pipeline, what has actually run, and the throughput and throughput days by month, quarter, campus, school and lab.

**Live site:** https://gati-course-tracker.web.app

## How it is put together

| Part | Where it lives | What it does |
|---|---|---|
| The web page | `public/index.html`, hosted by Firebase Hosting | Everything people see: dashboard, pipeline, actuals, setup |
| The data | Cloud Firestore in the Firebase project `gati-course-tracker` (Mumbai region) | Courses, people and their access, lists of schools, labs and holidays |
| Sign-in | Firebase Authentication, email and password | Only `@tataiis.org` addresses that the program team has added can see data |
| Access rules | `firestore.rules` | Enforced by Firebase itself, not by the page |

### Who can do what

- **Program team:** everything, including adding people, unlocking actuals and adding actuals directly.
- **GATI head:** adds and edits courses for their own sources, moves them to actuals, requests edits on locked actuals.
- **Viewer:** sees everything, changes nothing.

### Data in Firestore

- `courses/{id}`: one document per course. `stage` is `pipeline`, `actual` or `dropped`.
- `users/{email}`: one document per person with access. `role` is `program`, `head` or `viewer`; `gatis` lists a head's sources.
- `config/main`: schools, labs, holidays and the named GATI heads.

## How the numbers are worked out

- **Throughput** is the number of learners, counted once, in the month the course ends.
- **Throughput days** are learners × training days, placed in the month each day falls in.
- **Training days** are Monday to Friday, plus Saturday when a course is marked that way, minus listed holidays. A course can also have its training days set by hand.
- **Online courses** count in throughput but not in throughput days by default.
- **Financial year** runs April to March.

## Making changes

You need Node.js and the Firebase command-line tool (`npm install -g firebase-tools`), and to be signed in with `firebase login` as an owner of the Firebase project.

```bash
firebase deploy --only hosting,firestore:rules
```

To try changes locally against test servers instead of the real data:

```bash
firebase emulators:start --only auth,firestore
```

Then serve the `public` folder and open it with `?emu` added to the address, for example `http://localhost:5055/?emu`.

## Other files

- `tools/import_to_firestore.py`: the one-time script that copied the data from the earlier version into Firestore.
- `claude-version/tracker.html`: the earlier version that ran as a Claude page, kept for reference.

Course data is never stored in this repository. Use **Export to Excel** in the app for a copy of the data.
