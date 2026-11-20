# Tata IIS Course Tracker

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

1. **Pipeline:** a GATI head adds the course and answers "Do we have course outline?". With **Request from course production**, course production uploads the course files with the lab utilisation, and the GATI head confirms it or asks for changes (back to course production). With **Already have course outline**, the GATI head fills in the lab utilisation and course production is skipped. Every step, file and message is kept in the course log, and each list page has a **Recent changes** panel that gathers every course's log and edits on that page, marking what is new since you last looked. Anyone involved can add a message at any stage and mention a person, who then sees it under their profile picture. The log's **Uploaded files** button lists every file on the course with its category. Once approved, the GATI head confirms the batch with the student list, and leadership approves it (or sends it back to the GATI head).
2. **Batches · Upcoming batches:** approved batches wait for their start day. The program team can also add a confirmed batch here directly. Operations click **Batch started** and enter the actual start date and learners present; the student list can be uploaded now or later.
3. **Batches · Running:** shows progress and days left, and flags a missing student list. On the end day operations click **Batch completed** with the final throughput and gender split, the final student list (a new file, a typed or pasted sheet, or the one already added once they tick that it is correct and final; its number of learners must equal the final throughput), and Yes or No for placement eligibility. Feedback and the group photo are optional and can be added from the log at any time, even after completion.
4. **Throughput** (the completed list): locked. GATI heads can request an edit; the program team unlocks it. **Batch details** shows the batch, its learners and, when placement eligible, their placements, read-only; the program team edits through its Edit buttons.
5. **Placements:** when operations complete a batch they choose Yes or No for placement eligibility. Eligible batches also appear on the Placements tab, where the program team fills a sheet per batch (student, status, company, sector, role, location, region, package and bracket, joining date) by typing, pasting from Excel or uploading the template. The sheet starts from the batch's student list.

Learner lists carry a registration number for each learner; it is required when a batch is completed. A GATI head can confirm a batch without the list by ticking "Not available right now"; the batch is then flagged until the list is added. Setup and **Give feedback** (with screenshots) are in the profile menu at the top right; only the admin sees the feedback, in Setup.

### Who can do what

- **Admin** (ram.viswanath@tataiis.org): everything, and the only one who can add people, change their access, add completed courses directly and delete records.
- **GATI head:** adds and edits pipeline courses for their own sources, confirms uploaded courses, confirms batches, and can drop a course from the pipeline at any step. A program team member can also head a source.
- **Course production:** uploads courses for review and adds notes in the pipeline.
- **Leadership:** approves confirmed batches into Upcoming batches, or sends them back to the GATI head.
- **Program team (operations):** adds upcoming batches, starts and completes batches, edits upcoming/running/completed records, manages schools, labs and holidays. A member can be limited to one campus (`campuses` on their profile). View only in the pipeline.
- **Viewer:** sees everything, changes nothing.

### Data in Firestore

- `courses/{id}`: one document per course. `stage` is `pipeline`, `standby`, `running`, `actual` or `dropped`; `review` tracks the pipeline review; `log` is the conversation log; `files` lists attached files.
- `files/{id}` and `files/{id}/chunks/{n}`: attached files (up to 5 MB), stored in pieces because the project has no file storage.
- `users/{email}`: one document per person with access. `roles` lists any of `program`, `cp` and `lead` (a person can have several); `gatis` lists the sources they head; nothing listed means view only. Older entries have a single `role`.
- `feedback/{id}`: feedback sent from the profile menu, with any screenshots.
- `placements/{courseId}`: the placement sheet of a completed batch (`rows`, one per student).
- `config/main`: schools, labs, holidays and the named GATI heads.

## How the numbers are worked out

- **Throughput** is the number of learners, counted once, in the month the course ends.
- **Throughput days** are learners × training days, placed in the month each day falls in.
- **Training days** are Monday to Friday, plus Saturday and/or Sunday when a course includes them, minus listed holidays. A course can also have its training days set by hand.
- **Online courses** count in throughput but not in throughput days by default.
- **Courses marked non-eligible for throughput** never add to throughput or throughput days. Dashboard and Throughput show only eligible courses unless the filter says otherwise.
- **Dashboard categories:** every chart, total and table can show any of Throughput (completed), Running batches, Upcoming batches and Pipeline. Pipeline confidence (green, yellow, red) is shown only on the Pipeline tab.
- **Programme types** are grouped as Fresh Skilling (FS), Academic Skilling (AS) and Professional Skilling (PS); `ptCat` and `ptCode` hold the choice and `programType` the label shown.
- **Lab utilisation** is entered in the pipeline (up to three labs plus the classroom, adding up to 100% for on-campus and hybrid courses).
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
