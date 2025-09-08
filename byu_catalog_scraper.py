import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

# --------- Configuration ----------
BASE_URL = "https://catalog.byu.edu"
PROGRAM_OUTCOMES_SELECTOR = "div#programLearningOutcomes div.field-item"
COURSE_LINK_SELECTOR = "a.custom-link[data-course-id]"
COURSE_OUTCOMES_SELECTOR = "#learningOutcomes div.field-value"
# -----------------------------------

def scrape_major(url_or_file, output_file="outcomes.txt", offline=False):
    """
    Scrapes program and course outcomes from a BYU catalog URL or local HTML file.

    Parameters:
        url_or_file (str): URL to the BYU catalog program page or path to local HTML file.
        output_file (str): Path to save the text output.
        offline (bool): If True, reads from a local file instead of fetching from the web.
    """
    # Load program page
    if offline:
        html = Path(url_or_file).read_text(encoding="utf-8")
    else:
        resp = requests.get(url_or_file)
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")

    # --- Extract program outcomes ---
    program_outcomes = []
    for el in soup.select(PROGRAM_OUTCOMES_SELECTOR):
        text = el.get_text(" ", strip=True)
        if text:
            program_outcomes.append(text)

    if not program_outcomes:
        for el in soup.select("div.field-value"):
            text = el.get_text(" ", strip=True)
            if text and ("Students" in text or len(text) > 40):
                program_outcomes.append(text)

    # --- Find course links ---
    course_links = []
    all_course_links = soup.select(COURSE_LINK_SELECTOR)

    for a in all_course_links:
        href = a.get("href")
        course_name = a.get_text(" ", strip=True)
        if href:
            if not href.startswith("http"):
                href = BASE_URL + href
            course_links.append((course_name, href))

    # --- Visit each course and extract outcomes ---
    course_outcomes = {}
    for course_name, link in course_links:
        try:
            r = requests.get(link)
            r.raise_for_status()
            csoup = BeautifulSoup(r.text, "html.parser")

            title_elem = csoup.select_one("title")
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                if "| BYU Catalog" in title_text:
                    actual_course_name = title_text.split("|")[0].strip()
                else:
                    actual_course_name = title_text
            else:
                actual_course_name = course_name

            outcomes = []
            for block in csoup.select(COURSE_OUTCOMES_SELECTOR):
                t = block.get_text(" ", strip=True)
                if t:
                    outcomes.append(t)

            time.sleep(0.3)

        except Exception:
            outcomes = []
            actual_course_name = f"{course_name} (error)"

        if not outcomes:
            outcomes = ["(no course outcomes found)"]

        course_outcomes[actual_course_name] = outcomes

    # --- Write text output ---
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Program Outcomes\n")
        f.write("================\n")
        for po in program_outcomes:
            f.write(f"- {po}\n")
        f.write("\n----------------\n\nCourses and Outcomes\n")
        f.write("====================\n\n")
        for course, outcomes in course_outcomes.items():
            f.write(f"{course}\n")
            f.write("-" * len(course) + "\n")
            for o in outcomes:
                f.write(f"- {o}\n")
            f.write("\n")
