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

### How a course moves

1. **Pipeline:** a GATI head adds the course and says whether the course is already available. If not, course production uploads the course files and the GATI head confirms it or asks for changes (back to course production); if it is, course production is skipped. Every step, file and note is kept in the course log. Once approved, the GATI head confirms the batch, and leadership approves it (or sends it back to the GATI head).
2. **Batches · Upcoming batches:** approved batches wait for their start day. Operations click **Batch started**, upload the student list (required; a template is offered) and enter the actual start date and learners present.
3. **Batches · Running:** shows progress and days left. On the end day operations click **Batch completed** with the final throughput, gender split, labs, and optionally the feedback Excel and group photo.
4. **Throughput** (the completed list): locked. GATI heads can request an edit; the program team unlocks it.

### Who can do what

- **Admin** (ram.viswanath@tataiis.org): everything, and the only one who can delete records.
- **GATI head:** adds and edits pipeline courses for their own sources, confirms uploaded courses, confirms batches. A program team member can also head a source.
- **Course production:** uploads courses for review and adds notes in the pipeline.
- **Leadership:** approves confirmed batches into Upcoming batches, or sends them back to the GATI head.
- **Program team (operations):** starts and completes batches, edits standby/running/completed records, manages people and lists. View only in the pipeline.
- **Viewer:** sees everything, changes nothing.

### Data in Firestore

- `courses/{id}`: one document per course. `stage` is `pipeline`, `standby`, `running`, `actual` or `dropped`; `review` tracks the pipeline review; `log` is the conversation log; `files` lists attached files.
- `files/{id}` and `files/{id}/chunks/{n}`: attached files (up to 5 MB), stored in pieces because the project has no file storage.
- `users/{email}`: one document per person with access. `role` is `program`, `cp`, `lead`, `head` or `viewer`; `gatis` lists the sources they head.
- `config/main`: schools, labs, holidays and the named GATI heads.

## How the numbers are worked out

- **Throughput** is the number of learners, counted once, in the month the course ends.
- **Throughput days** are learners × training days, placed in the month each day falls in.
- **Training days** are Monday to Friday, plus Saturday when a course is marked that way, minus listed holidays. A course can also have its training days set by hand.
- **Online courses** count in throughput but not in throughput days by default.
- **Courses marked as not counting towards throughput** never add to throughput or throughput days. Dashboard and Throughput show only counted courses unless the filter says otherwise.
- **Financial year** runs April to March.

## Making changes

Every change saved to the `main` branch is published automatically by GitHub Actions (`.github/workflows/deploy.yml`): the site and the database rules go live within a couple of minutes. No keys are stored anywhere. Google trusts this repository's `main` branch directly through Workload Identity Federation, and the publishing account `github-deployer@gati-course-tracker.iam.gserviceaccount.com` can only publish the site and rules. To stop automatic publishing, delete the `github` workload identity pool in Google Cloud → IAM → Workload Identity Federation.

To publish by hand instead, install Node.js and the Firebase command-line tool (`npm install -g firebase-tools`), sign in with `firebase login` as an owner of the Firebase project, and run:

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
