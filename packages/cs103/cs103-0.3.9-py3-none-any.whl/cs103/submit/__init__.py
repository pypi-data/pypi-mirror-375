from . import submit as internal_submit
from ..testing.testing import *
from ..typecheck.typecheck import *
from typing import List

# Our non-CPSC103-specific version of submit does not use the 103 testing
# or typecheck libraries, and may have extra arguments/configuration required.
#
# So, we wrap it here in a CPSC 103-specific version:

@typecheck
def submit(course_code: int, assignment_code: int) -> None:
    """
    Displays a form used for students to submit their CPSC 103 assignments.
    The course_code is a Canvas-generated numeric code for the course to 
    submit. The assignment_code is similar but for the assignment. You can
    see both numbers in the URL (web address) when you open a Canvas 
    assignment, but typically we will prepare your starter file with the 
    appropriate course and assignment codes already!
    
    Starts by ensuring that the "key" needed to access a student's account on
    Canvas has been configured. If not, gives guidance on configuring that key.
    
    Once the key is ready, requests additional information (particularly file
    or files to submit), checks that the set of files chosen will run correctly,
    and submits them to Canvas, providing a URL (web address) for the student to
    check that the submitted file looks correct.
    
    Students can check their submission using the HTML file submitted (which
    should open easily in their browser) or by downloading all the files
    submitted to their computer and re-uploading them to their Syzygy account.
    """
    return internal_submit.submit(course_code, assignment_code)

__all__ = ['submit']