import argparse
import requests
import csv
import sys
import time
import os

def read_secret_file(filename):
    if not os.path.exists(filename):
        print(f"[!] Error: The file '{filename}' was not found.")
        sys.exit(1)
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().strip()

def scrape_courses(args):
    cookie_data = read_secret_file("cookies")
    csrf_token_data = read_secret_file("csrf-token")

    endpoint_url = "https://syllabus.sharjah.ac.ae/Syllabus/List"
    
    # Matching the exact headers from your cURL command
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": cookie_data,
        "DNT": "1",
        "Origin": "https://syllabus.sharjah.ac.ae",
        "Referer": "https://syllabus.sharjah.ac.ae/Syllabus",
        "RequestVerificationToken": csrf_token_data,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    # CSV headers
    fieldnames = [
        "SyllabusCode", "TermCode", "CollegeCode", "DepartmentCode", 
        "CourseCode", "Course", "CourseSection", "CRN", "Faculty", "Status"
    ]
    
    all_records = []
    start = 0
    length = 100 # Batch size (changed from 5 to 100 to speed up scraping)
    draw = 1
    total_records = None

    print(f"[*] Starting scrape for Term ID: {args.term_id}...")

    while True:
        # Base payload
        payload = {
            "draw": str(draw),
            "start": str(start),
            "length": str(length),
            "search[value]": "",
            "search[regex]": "false",
            "order[0][column]": "4",
            "order[0][dir]": "asc",
            "termId": args.term_id,
            "collegeId": "",
            "keyword": "",
            "status": "",
            "myRecordsOnly": "false" # Set to false to get ALL courses, not just yours
        }

        # The strict column schema required by the server (Extracted from your cURL)
        columns = [
            "Id", "SyllabusId", "SyllabusCode", "TermCode", "CollegeCode",
            "DepartmentCode", "CourseCode", "Course", "CourseSection", "CRN",
            "Faculty", "Status", "11"
        ]

        for i, col in enumerate(columns):
            payload[f"columns[{i}][data]"] = col
            payload[f"columns[{i}][name]"] = ""
            payload[f"columns[{i}][searchable]"] = "true"
            payload[f"columns[{i}][orderable]"] = "true"
            payload[f"columns[{i}][search][value]"] = ""
            payload[f"columns[{i}][search][regex]"] = "false"

        try:
            response = requests.post(
                endpoint_url, 
                headers=headers, 
                data=payload,
                allow_redirects=False
            )
            
            if response.status_code in (301, 302):
                print(f"[!] Server redirected us to: {response.headers.get('Location')}")
                sys.exit(1)

            response.raise_for_status()
            data = response.json()

        except requests.exceptions.RequestException as e:
            print(f"[!] Request failed: {e}")
            sys.exit(1)
        except ValueError:
            print("[!] Failed to parse JSON. Raw response snippet:")
            print(response.text[:500])
            sys.exit(1)

        records = data.get("data", [])
        if not records:
            break 

        if total_records is None:
            total_records = data.get("recordsFiltered", data.get("recordsTotal", "Unknown"))
            print(f"[*] Found approximately {total_records} total records. Fetching...")

        for row in records:
            all_records.append({
                "SyllabusCode": row.get("SyllabusCode", ""),
                "TermCode": row.get("TermCode", ""),
                "CollegeCode": row.get("CollegeCode", ""),
                "DepartmentCode": row.get("DepartmentCode", ""),
                "Course": row.get("Course", ""), 
                "CourseCode": row.get("CourseCode", ""),
                "CourseSection": row.get("CourseSection", ""),
                "CRN": row.get("CRN", ""),
                "Faculty": row.get("Faculty", ""),
                "Status": row.get("Status", "")
            })

        print(f"    -> Fetched records {start + 1} to {start + len(records)}...")
        
        start += length
        draw += 1
        time.sleep(0.5)

        if len(records) < length:
            break

    if all_records:
        with open(args.output, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_records)
        print(f"[*] Successfully saved {len(all_records)} courses to '{args.output}'.")
    else:
        print("[*] No courses found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--term-id", required=True, help="Target Semester/Term ID")
    parser.add_argument("--output", default="offered_courses.csv")
    args = parser.parse_args()
    scrape_courses(args)