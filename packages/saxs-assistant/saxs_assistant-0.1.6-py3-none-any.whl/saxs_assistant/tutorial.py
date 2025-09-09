import webbrowser


def show_tutorial():
    """
    Opens the tutorial page for this package in the default web browser.
    """
    tutorial_url = "https://github.com/C3344/SAXS-Assistant/blob/main/Supplemental%20Data/Tutorial%20PDF.pdf"
    print(f"Opening tutorial: {tutorial_url}")
    webbrowser.open(tutorial_url)


def show_supplemental():
    """
    Opens the tutorial page for this package in the default web browser.
    """
    tutorial_url = (
        "https://github.com/C3344/SAXS-Assistant/tree/main/Supplemental%20Data"
    )
    print(f"Opening link to supplemental data: {tutorial_url}")
    webbrowser.open(tutorial_url)
