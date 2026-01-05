
import os
import time
import json
import pandas as pd
import argparse
from playwright.sync_api import sync_playwright

# Configuration
ARTICLES_DIR = 'Articles'
OUTPUT_FILE = 'extracted_studies.xlsx'
GEMINI_URL = "https://gemini.google.com/app"

# Column Definitions
STUDY_CHARACTERISTICS = [
    ("Study ID", "First author + year (e.g., Barkyoumb 2025)"),
    ("Journal", "Source of publication"),
    ("Country/Region", "Study location(s)"),
    ("Study Design", "Retrospective cohort, RCT, meta-analysis, etc."),
    ("Database/Setting", "National claims, single-center, multicenter, etc."),
    ("Sample Size (Total)", "Number of patients included"),
    ("GLP-1 RA Cohort Size", "Number of patients exposed"),
    ("Control Cohort Size", "Number of patients not exposed"),
    ("Age (mean ± SD)", "Baseline age"),
    ("Sex (% male/female)", "Gender distribution"),
    ("BMI (mean ± SD)", "Baseline BMI"),
    ("Diabetes Status (%)", "% with T2DM"),
    ("Other Comorbidities", "Hypertension, CAD, CKD, smoking, etc."),
    ("GLP-1 Agent(s)", "Semaglutide, liraglutide, tirzepatide, etc."),
    ("Exposure Definition", "Pre-op, peri-op, post-op; duration window"),
    ("Dosing Regimen", "Weekly vs daily, dose escalation"),
    ("Surgical Procedure", "ACDF, PCF, TLIF, PLIF, lumbar fusion, decompression"),
    ("Levels Fused", "Single vs multilevel"),
    ("Follow-up Duration", "90 days, 6 months, 1 year, 2 years, etc."),
    ("Matching/Adjustment", "Propensity score, covariates controlled"),
    ("Risk of Bias", "ROBINS-I, NOS, etc.")
]

OUTCOMES = [
    ("Surgical Site Infection (SSI)", "Yes/No, % incidence"),
    ("Wound Complications", "Dehiscence, delayed healing"),
    ("Venous Thromboembolism (VTE)", "DVT/PE incidence"),
    ("Mortality", "30-day, 90-day, 1-year"),
    ("Readmission", "30-day, 90-day, 1-year"),
    ("Reoperation", "Same-level vs adjacent-level"),
    ("Pseudarthrosis", "Radiographic or clinical nonunion"),
    ("Fusion Success", "Solid fusion rates"),
    ("Implant/Hardware Failure", "Breakage, loosening"),
    ("Operative Time", "Mean ± SD"),
    ("Blood Loss", "Mean ± SD"),
    ("Length of Stay (LOS)", "Median/mean days"),
    ("Emergency Department Visits", "Within 90 days"),
    ("Medical Complications", "Anemia, AKI, renal failure, pneumonia"),
    ("Glycemic Control", "HbA1c change, peri-op glucose variability"),
    ("Cardiovascular Events", "MI, stroke"),
    ("Neurological Outcomes", "Dysphagia, mobility deficits"),
    ("Nutritional/Muscle Outcomes", "Lean mass loss, sarcopenia"),
    ("Adverse Drug Events", "Pancreatitis, thyroid cancer, GI symptoms"),
    ("Other Notes", "Any unique findings (e.g., SEL regression, neuroprotection)")
]

ALL_COLUMNS = [c[0] for c in STUDY_CHARACTERISTICS] + [c[0] for c in OUTCOMES if c[0] != "Study ID"]

def create_prompt():
    prompt = "Extract the following information from the attached PDF. Return the result as a valid JSON object where keys are the 'Column Label' and values are the extracted text. If information is missing, use null.\n\n"
    prompt += "--- Study Characteristics ---\n"
    for label, desc in STUDY_CHARACTERISTICS:
        prompt += f"- {label}: {desc}\n"
    
    prompt += "\n--- Outcomes ---\n"
    for label, desc in OUTCOMES:
        if label == "Study ID": continue 
        prompt += f"- {label}: {desc}\n"
    
    prompt += "\n\nCRUCIAL: Verify the extracted data against the PDF one more time before outputting to ensure accuracy. Return ONLY the JSON object, no markdown formatting."
    return prompt

def extract_data_from_page(page, pdf_path, prompt_text):
    print(f"[{os.path.basename(pdf_path)}] Navigating to Gemini...")
    page.goto(GEMINI_URL)
    time.sleep(5)
    
    # Upload Logic
    print(f"[{os.path.basename(pdf_path)}] Attempting upload...")
    try:
        # Robust Upload Logic with FileChooser
        with page.expect_file_chooser() as fc_info:
            # Click the Plus button
            # Strategy: Aria label OR Material Icon text
            plus_button = page.locator("button[aria-label='Open upload file menu'], button[aria-label='Upload files']")
            
            if plus_button.count() == 0:
                 # Check for icon text 'add'
                 plus_button = page.locator("span.material-symbols-outlined:has-text('add'), span.material-icons-outlined:has-text('add'), mat-icon:has-text('add'), mat-icon:has-text('add_circle')").locator("..").locator("..")

            if plus_button.count() == 0:
                 # Fallback: Just try to click the first button in the input area footer
                 # This is risky but "not clicking anything" is worse
                 print("Trying fallback footer button...")
                 footer = page.locator("bard-mode-switcher").locator("..") # Approximate
                 # No, too complex.
            
            if plus_button.count() > 0:
                print("Found Plus button.")
                try:
                    plus_button.first.evaluate("el => el.style.border = '5px solid red'")
                    time.sleep(0.5)
                    plus_button.first.click(force=True)
                except:
                    plus_button.first.evaluate("el => el.click()")
                
                time.sleep(1)
                
                # Check for menu item
                menu_item = page.locator("div[role='menuitem']:has-text('Upload'), span:has-text('Upload'), li:has-text('Upload'), div:has-text('Upload a file')")
                try:
                    if menu_item.count() > 0:
                        menu_item.first.wait_for(state="visible", timeout=3000)
                        menu_item.first.click(force=True)
                    else:
                        print("Menu item not found, trying ArrowDown...")
                        page.keyboard.press("ArrowDown")
                        time.sleep(0.5)
                        page.keyboard.press("Enter")
                except:
                    page.keyboard.press("ArrowDown")
                    time.sleep(0.5)
                    page.keyboard.press("Enter")
            else:
                 print("Could not find Plus button.")
                 page.screenshot(path="debug_no_plus.png")
                 return None
        
        file_chooser = fc_info.value
        file_chooser.set_files(pdf_path)
        print(f"[{os.path.basename(pdf_path)}] File uploaded. Waiting for processing...")
        time.sleep(10) # Wait for upload
        
    except Exception as e:
        print(f"[{os.path.basename(pdf_path)}] Upload failed: {e}")
        return None

    # Prompting
    try:
        text_area = page.locator("div[contenteditable='true'], textarea")
        text_area.first.fill(prompt_text)
        time.sleep(1)
        text_area.first.press("Enter")
        print(f"[{os.path.basename(pdf_path)}] Prompt sent. Waiting for response...")
        
        # Wait for response
        time.sleep(30) 
        
        # Extract Response
        response_elements = page.locator("model-response, .model-response-text") 
        if response_elements.count() > 0:
            last_response = response_elements.all()[-1].inner_text()
        else:
            last_response = page.content()

        # Parse JSON
        start = last_response.find('{')
        end = last_response.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = last_response[start:end]
            data = json.loads(json_str)
            data['Source File'] = os.path.basename(pdf_path)
            # data['_tab'] = ... # internal use
            return data
        else:
            print(f"[{os.path.basename(pdf_path)}] No JSON found in response.")
            return None

    except Exception as e:
        print(f"[{os.path.basename(pdf_path)}] Interaction failed: {e}")
        return None

def process_study_single_pass(context, pdf_path, prompt_text):
    print(f"\n--- Processing {os.path.basename(pdf_path)} ---")
    page = context.new_page()
    try:
        data = extract_data_from_page(page, pdf_path, prompt_text)
        return [data] if data else []
    finally:
        # User requested "new tab" originally, but usually we close to save resources.
        # "Extract response for each article only once"
        # I will close it to keep browser clean, unless debugging.
        # Given 20 files, keeping 20 tabs might crash.
        page.close()

def get_pdf_files():
    files = [f for f in os.listdir(ARTICLES_DIR) if f.lower().endswith('.pdf')]
    return [os.path.join(ARTICLES_DIR, f) for f in files]

def main(limit=None, browser_channel="chrome"):
    if not os.path.exists(ARTICLES_DIR):
        print(f"Error: Directory {ARTICLES_DIR} does not exist.")
        return

    pdf_files = get_pdf_files()
    
    # Resume Skip Logic
    if os.path.exists(OUTPUT_FILE):
        try:
            existing_df = pd.read_excel(OUTPUT_FILE)
            if 'Source File' in existing_df.columns:
                processed_files = set(existing_df['Source File'].dropna().astype(str).tolist())
                # Normalize basenames for comparison
                processed_basenames = {os.path.basename(f) for f in processed_files}
                
                # Filter out files whose basename matches processed files (or variants like "file (Run 2A)")
                # Actually, our Source File just stores the basename or basename + suffix.
                # A simple basename check might be best if we just strip suffixes.
                # But 'A Fano 2025.pdf (Run 2A)' implies 'A Fano 2025.pdf' was processed.
                
                # Better approach: check if original filename is contained in any processed source file string
                files_to_skip = []
                for pf in pdf_files:
                    basename = os.path.basename(pf)
                    # Check if this basename appears in any recorded source file entry
                    if any(basename in str(recorded) for recorded in processed_files):
                        files_to_skip.append(pf)
                
                original_count = len(pdf_files)
                pdf_files = [f for f in pdf_files if f not in files_to_skip]
                print(f"Skipping {len(files_to_skip)} already processed files. {len(pdf_files)} remaining.")
        except Exception as e:
            print(f"Warning: Could not read existing output file for resume logic: {e}")

    if limit:
        pdf_files = pdf_files[:int(limit)]
    
    print(f"Found {len(pdf_files)} PDF files to process.")

    prompt_text = create_prompt()
    all_results = []

    with sync_playwright() as p:
        profile_name = f"{browser_channel}_profile"
        user_data_dir = os.path.join(os.getcwd(), profile_name)
        print(f"Launching {browser_channel} with profile: {user_data_dir}")
        
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir, 
                headless=False, 
                channel=browser_channel, 
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    "--no-sandbox",
                    "--disable-infobars"
                ],
                ignore_default_args=["--enable-automation"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            if len(browser.pages) > 0:
                page = browser.pages[0]
            else:
                page = browser.new_page()
                
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"Failed to launch {browser_channel}: {e}")
            return
        
        # Login Check
        page = browser.pages[0]
        page.goto(GEMINI_URL)
        time.sleep(5)
        
        # Check if we are already logged in by looking for input area
        try:
            print("Checking login status...")
            page.locator("div[contenteditable='true'], textarea").wait_for(state="visible", timeout=5000)
            print("Login confirmed (Prompt area found). Proceeding immediately.")
        except:
             print("Login verification failed (Prompt area not found). assuming need to log in.")
             print(f"Please log in to Gemini in the opened {browser_channel} window. Waiting 45 seconds...")
             time.sleep(45)

        # Process Files
        for pdf_path in pdf_files:
            study_results = process_study_single_pass(browser, pdf_path, prompt_text)
            
            if study_results:
                all_results.extend(study_results)
                
                # Save Incremental
                df = pd.DataFrame(study_results)
                # Align columns
                for c in ALL_COLUMNS:
                    if c not in df.columns: df[c] = None
                
                cols = ['Source File'] + [c for c in ALL_COLUMNS if c in df.columns]
                df = df[cols]

                if os.path.exists(OUTPUT_FILE):
                    existing = pd.read_excel(OUTPUT_FILE)
                    df = pd.concat([existing, df], ignore_index=True)
                else:
                    # If first write, ensure all columns are present for template structure if needed
                    pass
                
                df.to_excel(OUTPUT_FILE, index=False)
                print(f"Saved {len(study_results)} rows to {OUTPUT_FILE}")

        print("Done. Browser remains open.")
        time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", help="Limit number of files to process", default=None)
    parser.add_argument("--browser", help="Browser channel (chrome, msedge)", default="chrome")
    args = parser.parse_args()
    main(limit=args.limit, browser_channel=args.browser)
