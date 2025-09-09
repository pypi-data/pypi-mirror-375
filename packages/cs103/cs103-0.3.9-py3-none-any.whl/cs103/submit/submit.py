#Imports 
import subprocess
import sys
from pip._internal import main as pip
import pathlib
import importlib 
import os
import ipywidgets as widgets
import glob
import tempfile
import shutil
from IPython.display import Javascript
from typing import List, Optional


def install(package: str) -> None:
    """
    Install the given Python package using pip.
    """
    pip(['install', '--user', package])
    

# Attempt to install the required packages canvasapi and python-dotenv
# TODO: replace with properly declared dependencies. We think we've done this already, should we delete this code?
try:
    import os
    import os.path
    from canvasapi import Canvas
    from dotenv import load_dotenv
except:
    print("Attempting to install canvasapi:")
    install("canvasapi")
    print("Attempting to install python-dotenv:")
    install("python-dotenv")
    print("Exiting kernel to force a restart now that installs are complete:")
    os._exit(1) 

#Variables 

API_URL = 'https://canvas.ubc.ca/'
ALLOWED_EXTENSIONS = ['ipynb', 'csv', 'txt', 'png']
token_success = False
API_KEY=""

def touch_path(path_str: str) -> None:
    """
    Run the equivalent of UNIX touch on path_str, where path_str
    can contain ~ to refer to the user's home directory, managed
    via Path.expanduser. Touches with user read/write permission
    and tries to deny group/other permissions.
    """
    envp = pathlib.Path(path_str). expanduser()
    envp.touch(0o600)

#Token Verification:
def token_verif(course: int):
    """
    Attempts to load the user's Canvas API token from ~/.env and access
    the given Canvas course number.
    
    WARNING: If the token is not in ~/.env, deletes and recreates ~/.env.
    
    TODO: gentler management of .env file or switch to a .jupyter-canvas-submit.env file.
    
    On success, initializes the global variable API_KEY with the key and 
    changes the global variable token_success to True.
    
    TODO: perhaps return the API key on success or a flag for failure (e.g., None) otherwise.
    """
    def test_token():
        #Attempts to access the token in the .env 
        #file and access the course with that token
        touch_path("~/.env")   
        load_dotenv()
        global API_KEY
        API_KEY= os.getenv("API_KEY")
        canvas = Canvas(API_URL, API_KEY)
        course_got = canvas.get_course(course)
        global token_success
        token_success = True
        
    try:
        test_token()
    
    except:
        print("We can't seem to find your token, if you need help finding it please see:")
        print("https://documentcloud.adobe.com/link/track?uri=urn%3Aaaid%3Ascds%3AUS%3A5a18408c-2102-4dc5-8f50-f8205f9b85bf")
        print("Please copy and paste your token here and then hit enter:")
        token = input()
        
        #TODO: If API key is incorrect in the .env file, we want to delete the 
        #line with the API key, however right now it just deletes the entire .env file
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]
            os.remove(os.path.expanduser("~/.env"))
            touch_path("~/.env") 
        
                
        with open(os.path.expanduser("~/.env"), "a") as f:
            f.write("\nAPI_KEY = " + token)
        
        try: 
            test_token()
            
        except:
            print("We are still unable to access your course, please submit manually, then bring this up with a TA or instructor.")
        
def convert_notebook_to_html( file_name: str, allow_errors: bool = False) -> bool:  
    """
    Attempts to convert the given notebook file to HTML. The conversion process can also
    produce error output. If allow_errors is True, this function will produce the HTML even
    if there are errors. If not, it will fail in the presences of errors. On failure, it also
    prints the error text.
    
    The file should be in the current working directory.
    """
    if allow_errors: 
        outp= subprocess.run(["jupyter", "nbconvert",   "--execute", "--allow-errors","--ExecutePreprocessor.timeout=300",
                              "--to",  "html",  file_name], capture_output= True)
    else:
        outp= subprocess.run(["jupyter", "nbconvert",   "--execute", "--to",  "html",  file_name], capture_output= True)
     
    convert_success = outp.returncode == 0 
    
    if not convert_success:
        print(outp.stderr.decode("ascii"))
        
    return convert_success 
     
     
            
def file_ipynb(file_name: str) -> bool:
    """
    return True iff file_name ends in .ipynb (i.e., is a Jupyter notebook).
    """
    return file_name[-6:] == ".ipynb"

def file_csv(file_name: str) -> bool:
    """
    return True iff file_name ends in .csv (i.e., is a CSV file).
    """
    return file_name[-4:] == ".csv"

        
def submit_assignment(files: List[str], assign: int, c: int, allow_errors: bool = False) -> Optional[str]:
    """
    Attempt to submit the given list of files to the given assignment number
    in the given course number. If allow_errors is True, submits even if any
    notebook(s) in files produce errors when run and converted to HTML (else
    stops with a failure in that case). Works only if API_URL and API_KEY
    have already been successfully set.
    
    Any Jupyter notebooks are submitted as both ipynb and corresponding html.
    
    returns the URL for a successful submission or None if unsuccessful
    """
    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(c)
    assignment = course.get_assignment(assign)
    
    # To submit files as part of a Canvas assignment, we need to 
    # first stage the files into Canvas.
    submit_these_id = []
    
    
    all_successful = True
    for file in files:
        if file_ipynb(file): 
            # TODO: right now we upload the html file first then ipynb. This seems fine for now but should check it later.
            this_worked= convert_notebook_to_html(file_name=file, allow_errors= allow_errors)
            all_successful = all_successful and this_worked
            if this_worked:
                file2 = assignment.upload_to_submission(file[:-6] + '.html')
                submit_these_id.append(file2[1]['id'])

       
        file1 = assignment.upload_to_submission(file)
        submit_these_id.append(file1[1]['id'])
         
       
    if (not all_successful) or (submit_these_id == []) :
        return None
                
                
    
    submission = assignment.submit({ 'submission_type' : 'online_upload', 'file_ids' : submit_these_id})
   
    return submission.preview_url
    
def submit_assignment_in_temp(files: List[str], assign: int, c: int, allow_errors: bool = False) -> Optional[str]:
    """
    Generate a temporary directory, move all the requested files there (so they are isolated from other
    files, at least in that directory), switch to that directory, and submit. Switches back to the original
    working directory before return.
    
    c is the course number and assign the assignment number to submit to.
    
    API_URL and API_KEY must be successfully set before calling this function to succeed.
    
    Returns the URL for a successful submission or None if unsuccessful.
    """
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tempdir:
        try:
            for file in files:
                shutil.copy(file, tempdir)
            os.chdir(tempdir)
            return submit_assignment(files, assign, c, allow_errors)
        finally:
            os.chdir(cwd)

#interface definition  

# TODO: docstrings and signatures for widget functions.
def token_widget():
    token = widgets.Valid(
            value=token_success,
            description='Token')
    return token

def course_menu_widget():
    course_menu = widgets.Dropdown(
           options=['CS103_2018W1', 'CS103_2018W2', 'CS103_2019W1'],
           value='CS103_2019W1',
           description='Course:')
    return course_menu

def asn_menu_widget():
    asn_menu = widgets.Dropdown(
           options=['Module 1 tutorial', 'Module 2 tutorial','Module 3 tutorial', 'Module 4 tutorial', 
                    'Module 5 tutorial','Module 6 tutorial','Module 7 tutorial', 'Module 8 tutorial', 'Project submission'],
           value='Module 2 tutorial',
           description='Assignment:')
    return asn_menu

def files_widget():
    all_files = [file for ext in ALLOWED_EXTENSIONS for file in glob.glob('*.' + ext)]
    files = widgets.SelectMultiple(
            options=all_files,
            value=[all_files[0]],
            layout=widgets.Layout(width='50%', height='100%'),
            rows=len(all_files),
            description='Files',
            disabled=False)
    return files

def submit_button_widget():
    button = widgets.Button(
        description='submit',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='submit',
        icon='check')
    return button

def allow_error_button_widget():
    button = widgets.Button(
        description='Submit even if there are errors',
        layout=widgets.Layout(width='50%', height='80px'),
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Submit even if there are errors',
        icon='check')
    return button

def missing_token_widget():
    missing_token = widgets.Text(
        value='',
        placeholder='Your token here',
        description='Token:',
        disabled=False)
    return missing_token

def try_save():
    """
    This wasn't saving consistently :(
    We think it would work if it were on the main thread. 
    
    Attempts to save current notebook, 
    otherwise prints an informative error message
    """
    try:
        Javascript("IPython.notebook.save_notebook()")
    except:
        print("""We tried to automatically save your notebook, in case you are submitting it.
        But something didn't work, please make sure to save your notebook before submitting.
        We will continue with the files as they are now.""")
        

# TODO: docstring for submit
def submit(course_key:int, assign_key:int)-> None:
    """
    
    """
    t = token_widget()
    cm = course_menu_widget()
    am = asn_menu_widget()
    f = files_widget()
    b = submit_button_widget()
    mt = missing_token_widget()
    aebw= allow_error_button_widget()
    
    def submit_selected(button):
            
        files= list(f.value)

        if len(files)<1:
                print("No files have been selected. Please pick the files you would like to submit and try again.")
                return 

        allow_errors = button == aebw

        try:

            #TODO:  general notes 
            
            if allow_errors:
                print("We are about to submit the files even if there are errors:")
            else:
                print("We are about to submit the files:")
            print(", ".join(files))
            print()
            print("- We do this by moving only the files you selected to their own space, restarting a kernel,")
            print("  and running them from top to bottom.")
            print("- This ensures that the files you submit are exactly what the course staff needs to recreate your output.")
            print("- We then submit these to Canvas for you and, if successful, give you a link where you can review your submission.")
            print("- If there is an error, there will be a VERY LONG error message below.")
            print("  Read our suggestions at the bottom and try to ream the error message bottom up.")
            print()
            print("-----------------------------------------------------------------------------------------------")
            print()
            
            URL = submit_assignment_in_temp(files, assign_key, course_key, allow_errors)
            success = URL is not None
            if success and not allow_errors:
                print("Your assignment was submitted succesfully!")         
                print("Please check your submission at this link: " + URL)
                print("It will be easiest to check your submission using the HTML file at that link.")
                print()
                
            elif success and allow_errors:
                print("Your assignment was submitted succesfully!")
                print("However, we submitted even though there was an error.")
                print("If you have time, you may want to debug your code.")
                print('You can work on debugging by selecting "Restart and Run All"')
                print('from the "Kernel" menu and looking for the error.')
                print("Please check your submission at this link: " + URL)
                print("It will be easiest to check your submission using the HTML file at that link.")
                print()

            elif not success and not allow_errors:
                # TODO: make clear that students should read the error messages above to understand what went wrong.
                # TODO: mention the common case "If your submission has an error because a file was not found, be sure you are submitting that file!"?
                print("ERROR!")
                print("We attempted to submit these selected files:")
                print(", ".join(files))
                print()
                print("A jupyter notebook in the submission caused an error.")
                print()
                print("Consider these possibilities:")
                print("   1. Most likely, there is an error in your code. You might not even SEE this error unless" + 
                    " you try 'Restart and Run All'")
                print("      from the 'Kernel' menu.")
                print("   2. If your code requires other files to run, you may be seeing a 'FileNotFoundException' above. ")
                print("      Resubmit, ensuring you have selected ALL files you need.")
                print("   3. You may be seeing a TimeoutError. This could simply mean your code takes a long time to run. ")
                print("      Likely when you run your own code, some cell shows [*] next to it for a long time.")
                print("      If you click the \"Submit even if there are errors\" button below, we'll try giving you much more time.")
                print("      If that still doesn't work, you may need to debug or submit manually.")
                print("   4. You may have made unsaved changes. Try to save and resubmit.")
                print()
                print("If you really want to submit this assignment with the errors please click" +
                      " the \"Submit even if there are errors\" button")  
                display(aebw)
                print()

            elif not success and allow_errors:
                print("We are still unable to submit your assignment. Some of the suggestions above may help.")
                print("However, at this point please submit your assignment manually.")
                print("Then work with course staff to help you debug so you can submit successfully in future.")
                print()
        except:
            print("ERROR! Something went wrong with the submission, perhaps with accessing Canvas for course key " + str(course_key) +
                  ", assignment key " + str(assign_key) + ", files:")
            print(", ".join(files))
            print("and your token.")
            print("Please submit manually and ask a member of course staff for help")
            print()
            
            # :(
            
        # general end notes 
        print("WARNING: We can only see saved changes. ANY UNSAVED CHANGES would not have been submitted.")
        print("Save before each submission!")
        print("-----------------------------------------------------------------------------------------------")
        print()

            
    if token_success:
        display(t,f,b)
    else:
        token_verif(course_key)
        to= token_widget()
        display(to,f,b)
        
    b.on_click(submit_selected)
    aebw.on_click(submit_selected)
    
    
    

# be aware that the overall cs103 library has its own __all__
__all__ = [
    "submit"
]
