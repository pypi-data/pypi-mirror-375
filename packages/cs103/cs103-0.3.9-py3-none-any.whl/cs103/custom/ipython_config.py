import warnings

c = get_config()
c.InteractiveShellApp.matplotlib = "inline"

# could also do this with a regex 
warnings.filterwarnings('ignore', "\'ellipsis\' object is not callable", SyntaxWarning)
