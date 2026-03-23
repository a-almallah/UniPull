import argparse
import requests
import csv
import sys
import time

def scrape_courses(args):
    # The endpoint identified from syllabus.js
    endpoint_url = f"{args.base_url.rstrip('/')}/Syllabus/List"
    # endpoint_url = ""
    
    # Headers required to bypass authentication and CSRF protection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": args.cookie,
        "RequestVerificationToken": args.csrf_token,
        "X-Requested-With": "XMLHttpRequest"
    }

    # CSV setup
    fieldnames = [
        "SyllabusCode", "TermCode", "TermName", "CollegeCode", "College", 
        "DepartmentCode", "DepartmentName", "CourseCode", "Course", 
        "CourseSection", "CRN", "Faculty", "StatusText"
    ]
    
    all_records = []
    start = 0
    length = 100 # Batch size
    draw = 1
    total_records = None

    print(f"[*] Starting scrape for Term: {args.term_id}...")

    while True:
        # Construct the payload mimicking the DataTables POST request from syllabus.js
        payload = {
            "draw": draw,
            "start": start,
            "length": length,
            "termId": args.term_id,
            "collegeId": args.college_id,
            "courseId": args.course_id,
            "keyword": args.keyword,
            "status": args.status,
            "myRecordsOnly": "false" # Force false to get all organization records, not just the user's
        }

        try:
            response = requests.post(endpoint_url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"[!] Request failed: {e}")
            sys.exit(1)
        except ValueError:
            print("[!] Failed to parse JSON. Your session cookie or CSRF token might be invalid/expired.")
            sys.exit(1)

        records = data.get("data", [])
        if not records:
            break # No more records returned

        if total_records is None:
            total_records = data.get("recordsFiltered", data.get("recordsTotal", "Unknown"))
            print(f"[*] Found approximately {total_records} total records. Fetching...")

        for row in records:
            # Flatten the nested values for the CSV
            all_records.append({
                "SyllabusCode": row.get("SyllabusCode", ""),
                "TermCode": row.get("TermCode", ""),
                "TermName": row.get("TermName", ""),
                "CollegeCode": row.get("CollegeCode", ""),
                "College": row.get("College", ""),
                "DepartmentCode": row.get("DepartmentCode", ""),
                "DepartmentName": row.get("DepartmentName", ""),
                "CourseCode": row.get("CourseCode", ""),
                "Course": row.get("Course", ""),
                "CourseSection": row.get("CourseSection", ""),
                "CRN": row.get("CRN", ""),
                "Faculty": row.get("Faculty", ""),
                "StatusText": row.get("StatusText", "")
            })

        print(f"    -> Fetched records {start + 1} to {start + len(records)}...")
        
        start += length
        draw += 1
        time.sleep(0.5) # Gentle polite delay between pagination requests

        if len(records) < length:
            break # Reached the last page

    # Save to CSV
    if all_records:
        with open(args.output, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_records)
        print(f"[*] Successfully saved {len(all_records)} courses to '{args.output}'.")
    else:
        print("[*] No courses found matching your criteria.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape offered courses for a given semester from the portal.")
    
    # Required parameters based on server security
    parser.add_argument("--base-url", required=True, help="Base URL of the application (e.g., https://portal.sharjah.ac.ae)")
    parser.add_argument("--cookie", required=True, help="Your active session cookie string (from browser dev tools)")
    parser.add_argument("--csrf-token", required=True, help="The __RequestVerificationToken value (from browser dev tools or page source)")
    
    # Filtering parameters from LoadSyllabusList in syllabus.js
    parser.add_argument("--term-id", required=True, help="Target Semester/Term ID (e.g., 202410)")
    parser.add_argument("--college-id", default="", help="Optional: Filter by College ID")
    parser.add_argument("--course-id", default="", help="Optional: Filter by Course ID")
    parser.add_argument("--status", default="", help="Optional: Filter by Syllabus Status ID (e.g., approved, draft)")
    parser.add_argument("--keyword", default="", help="Optional: Search keyword")
    
    # Output parameter
    parser.add_argument("--output", default="offered_courses.csv", help="Output CSV filename (default: offered_courses.csv)")

    args = parser.parse_args()
    scrape_courses(args)