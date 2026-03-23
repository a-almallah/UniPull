## Prerequisites

1. **Python 3.x** installed on your system.
2. The `requests` library. You can instal
## Setup & Authentication

Because the portal is protected by strict ASP.NET Core session cookies and CSRF (Cross-Site Request Forgery) tokens, you must provide your active browser session data to the script. 

You need to create **two files** in the exact same folder as `main.py`: one named `cookies` and one named `csrf-token`.

### Step 1: Open Developer Tools
1. Log into the Syllabus portal in your web browser (Chrome/Edge/Firefox).
2. Navigate to the page where the courses are listed.
3. Press **F12** (or right-click anywhere and select **Inspect**) to open the Developer Tools.
4. Click on the **Network** tab at the top of the Developer Tools panel.
5. In the Network tab's filter box, type `List` (or just change the semester dropdown on the page to trigger a new data load).

### Step 2: Get your `cookies`
1. Under the "Name" column in the Network tab, click on the request named **`List`**.
2. A side panel will open. Scroll down to the **Request Headers** section.
3. Find the line labeled **`Cookie:`**.
4. Right-click the massive string of text next to it and select **Copy value**.
5. Create a new text file in the same folder as the script, name it exactly **`cookies`** (no `.txt` extension needed, but fine if it has one as long as you paste the data inside).
6. Paste the copied string into the file and save it. **Make sure there are no extra spaces or blank lines at the beginning or end.**

### Step 3: Get your `csrf-token`
1. Look at the exact same **Request Headers** section from Step 2.
2. Find the line labeled **`RequestVerificationToken:`**.
3. Right-click the string next to it and select **Copy value**.
4. Create another new text file in the same folder, name it exactly **`csrf-token`**.
5. Paste the copied string into the file and save it. 

*Your folder should now look like this:*
```text
📁 Folder/
 ├── main.py
 ├── cookies
 └── csrf-token
```

## How to Run

Open your terminal or command prompt, navigate to the folder containing the script, and run the following command:

```bash
python main.py --term-id 318
```

### Command Line Arguments

* `--term-id` **(Required)**: The ID of the semester you want to scrape. (e.g., `318` for the active term).
* `--output` *(Optional)*: The name of the output CSV file. Defaults to `offered_courses.csv`. 
  * *Example:* `python main.py --term-id 318 --output fall_2024_courses.csv`

## Output

The script will fetch 100 courses at a time, displaying its progress in the terminal. Once finished, it will generate a CSV file containing the following columns:

* SyllabusCode
* TermCode
* CollegeCode
* DepartmentCode
* CourseCode
* Course (Full Name)
* CourseSection
* CRN
* Faculty
* Status

## Troubleshooting

* **"The server rejected the request and redirected us"**: Your session has expired, or the data in your `cookies` / `csrf-token` files was copied incorrectly. Log out, log back in, and grab fresh values from the Network tab.
* **"Expecting value: line 1 column 1 (char 0)"**: The files might have accidental blank lines at the top. Ensure the text in `cookies` and `csrf-token` starts on the very first line of the file.
