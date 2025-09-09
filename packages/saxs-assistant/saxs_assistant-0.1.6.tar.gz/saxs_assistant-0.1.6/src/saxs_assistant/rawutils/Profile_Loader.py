import os
import re
import numpy as np
from . import sasm as SASM

# import sasm as SASM


# From SourceL RAWAPI
def load_profiles(filename_list, settings=None):
    """
    Loads individual scattering profiles from text files. This could be
    .dat files, but other file types such as .fit, .fir, .int, or .csv
    can also be loaded. This is a convenience wrapper for
    :py:func:`load_files` that only returns profiles. It should not be used
    for images, instead use :py:func:`load_and_integrate_images`.

    Parameters
    ----------
    filename_list: list
        A list of strings containing the full path to each profile to be loaded
        in.
    settings: :class:`bioxtasraw.RAWSettings.RAWSettings`, optional
        The RAW settings to be used when loading in the files,
        such as the calibration values used when radially averaging images.
        Default is none, this is commonly not used.

    Returns
    -------
    profile_list: list
        A list of individual scattering profile (:class:`bioxtasraw.SASM.SASM`)
        items loaded in, including those obtained from radially averaging any
        images.
    """
    if settings is None:
        settings = None  # __default_settings
        pass

    profile_list, iftm_list, secm_list = load_files(
        filename_list, settings
    )  # profile_list, iftm_list, secm_list, img_list = load_files(filename_list, settings)

    return profile_list


def load_files(filename_list, settings, return_all_images=False):
    """
    Loads all types of files that RAW knows how to load. If images are
    included in the list, then the images are radially averaged as part
    of being loaded in.

    Parameters
    ----------
    filename_list: list
        A list of strings containing the full path to each file to be
        loaded in.
    settings: :class:`bioxtasraw.RAWSettings.RAWSettings`
        The RAW settings to be used when loading in the files, such as the
        calibration values used when radially averaging images.
    return_all_images: bool
        If True, all loaded images are returned. If false, only the first loaded
        image of the last file is returned. Useful for minimizing memory use
        if loading and processing a large number of images. False by default.

    Returns
    -------
    profile_list: list
        A list of individual scattering profile (:class:`bioxtasraw.SASM.SASM`)
        items loaded in, including those obtained from radially averaging any
        images.
    ift_list: list
        A list of individual IFT (:class:`bioxtasraw.SASM.IFTM`) items loaded in.
    series_list: list
        A list of individual series (:class:`bioxtasraw.SECM.SECM`) items
        loaded in.
    img_list: list
        A list of individual images (:class:`numpy.array`) loaded in.
    """

    if not isinstance(filename_list, list):
        filename_list = [filename_list]

    profile_list = []
    ift_list = []
    series_list = []
    img_list = []

    for filename in filename_list:
        filename = os.path.abspath(os.path.expanduser(filename))

        file_ext = os.path.splitext(filename)[1]

        is_profile = False

        # if file_ext == '.sec': #Only use .dat files for SAXS_Assistant
        #     secm = SASFileIO.loadSeriesFile(filename, settings)
        #     series_list.append(secm)

        if file_ext == ".ift" or file_ext == ".out":  # changed from elif
            iftm, img = loadFile(filename, settings, return_all_images=False)

            if isinstance(iftm, list):
                ift_list.append(iftm[0])

        # elif file_ext == '.hdf5':
        #     try:
        #         secm = SASFileIO.loadSeriesFile(filename, settings)
        #         series_list.append(secm)
        #     except Exception:
        #         is_profile = True

        else:
            is_profile = True

        if is_profile:
            sasm, img = loadFile(
                filename,
                settings,  # sasm, img = SASFileIO.loadFile(filename, settings, got rid of IO since imported function needed
                return_all_images=return_all_images,
            )

            if img is not None:
                start_point = settings.get("StartPoint")
                end_point = settings.get("EndPoint")

                if not isinstance(sasm, list):
                    qrange = (start_point, len(sasm.getRawQ()) - end_point)
                    sasm.setQrange(qrange)
                else:
                    qrange = (start_point, len(sasm[0].getRawQ()) - end_point)
                    for each_sasm in sasm:
                        each_sasm.setQrange(qrange)

                if isinstance(img, list):
                    if not return_all_images and len(img_list) == 0:
                        img_list.append(img[0])
                    elif not return_all_images:
                        img_list[0] = img[0]
                    else:
                        img_list.extend(img)
                else:
                    if not return_all_images and len(img_list) == 0:
                        img_list.append(img)
                    elif not return_all_images:
                        img_list[0] = img
                    else:
                        img_list.append(img)

            if isinstance(sasm, list):
                profile_list.extend(sasm)
            else:
                profile_list.append(sasm)

    return profile_list, ift_list, series_list  # , img_lis #No images so commented out


# From Source: SASFileIO
def loadFile(filename, raw_settings, no_processing=False, return_all_images=True):
    """Loads a file an returns a SAS Measurement Object (SASM) and the full image if the
    selected file was an Image file

     NB: This is the function used to load any type of file in RAW
    """
    try:
        file_type = checkFileType(filename)
        # print file_type
    except IOError:
        raise
    except Exception as msg:
        print(str(msg))
        file_type = None

    if file_type == "hdf5":
        try:
            hdf5_file = fabio.open(filename)
            file_type = "image"
        except Exception:
            pass
    else:
        hdf5_file = None

    if file_type == "image":  # No images
        try:
            sasm, img = loadImageFile(
                filename, raw_settings, hdf5_file, return_all_images
            )
        except (ValueError, AttributeError) as msg:
            raise SASExceptions.UnrecognizedDataFormat(
                "No data could be retrieved from the file, unknown format."
            )
            traceback.print_exc()
        except Exception:
            traceback.print_exc()
            raise

        # Always do some post processing for image files
        if not isinstance(sasm, list):
            sasm = [sasm]

        for current_sasm in sasm:
            postProcessProfile(current_sasm, raw_settings, no_processing)

    elif file_type == "hdf5":
        sasm = loadHdf5File(filename, raw_settings)
        img = None

    else:
        sasm = loadAsciiFile(filename, file_type)
        img = None

        # If you don't want to post process asci files, return them as a list
        if not isinstance(sasm, list):
            SASM.postProcessSasm(sasm, raw_settings)

    if not isinstance(sasm, list) and (sasm is None or len(sasm.i) == 0):
        raise SASExceptions.UnrecognizedDataFormat(
            "No data could be retrieved from the file, unknown format."
        )

    return sasm, img


def loadAsciiFile(filename, file_type):
    ascii_formats = {
        "rad": loadRadFile,
        "new_rad": loadNewRadFile,
        "primus": loadDatFile,
        # 'bift'       : loadBiftFile, #'ift' is used instead
        "int": loadIntFile,
        "abs": loadIntFile,
        "fit": loadFitFile,
        "fir": loadFitFile,
        "ift": loadIftFile,
        "csv": loadTxtFile,
        "out": loadOutFile,
        "txt": loadTxtFile,
    }

    if file_type is None:
        return None

    sasm = None

    if file_type in ascii_formats:
        sasm = ascii_formats[file_type](filename)

    if sasm is not None and file_type != "ift" and file_type != "out":
        if not isinstance(sasm, list) and len(sasm.i) == 0:
            sasm = None

    if file_type == "rad" and sasm is None:
        sasm = ascii_formats["new_rad"](filename)

        if sasm is None:
            sasm = ascii_formats["primus"](filename)

    if file_type == "primus" and sasm is None:
        sasm = ascii_formats["txt"](filename)

    if sasm is not None and not isinstance(sasm, list):
        sasm.setParameter("filename", os.path.split(filename)[1])

    return sasm


def loadDatFile(filename):
    """Loads a .dat format file"""

    with open(filename, "r") as f:
        lines = f.readlines()

    if len(lines) == 0:
        raise SASExceptions.UnrecognizedDataFormat(
            "No data could be retrieved from the file."
        )

    sasm = makeDatFile(lines, filename)

    return sasm


# ---Need to Attempt new version for as SASDAA2.dat failed due to encoding error. but for now will just note
#


def loadRadFile(filename):
    """NOTE : THIS IS THE OLD RAD FORMAT.."""
    """ Loads a .rad file into a SASM object and attaches the filename and header into the parameters  """

    iq_pattern = four_col_fit
    param_pattern = re.compile(r"[a-zA-Z0-9_]*\s*[:]\s+.*")

    i = []
    q = []
    err = []
    parameters = {"filename": os.path.split(filename)[1]}

    fileheader = {}

    with open(filename, "r") as f:
        for line in f:
            iq_match = iq_pattern.match(line)
            param_match = param_pattern.match(line)

            if iq_match:
                found = iq_match.group().split()
                q.append(float(found[0]))

                i.append(float(found[1]))

                err.append(float(found[2]))

            if param_match:
                found = param_match.group().split()

                if len(found) == 3:
                    try:
                        val = float(found[2])
                    except ValueError:
                        val = found[2]

                    fileheader[found[0]] = val

                elif len(found) > 3:
                    arr = []
                    for each in range(2, len(found)):
                        try:
                            val = float(found[each])
                        except ValueError:
                            val = found[each]

                        arr.append(val)

                    fileheader[found[0]] = arr
                else:
                    fileheader[found[0]] = ""

    parameters = {"filename": os.path.split(filename)[1], "fileHeader": fileheader}

    i = np.array(i)
    q = np.array(q)
    err = np.array(err)

    return SASM.SASM(i, q, err, parameters)


def loadNewRadFile(filename):
    """NOTE : This is a load function for the new rad format"""
    """ Loads a .rad file into a SASM object and attaches the filename and header into the parameters  """

    iq_pattern = three_col_fit
    param_pattern = re.compile(r"[a-zA-Z0-9_]*\s*[:]\s+.*")

    i = []
    q = []
    err = []
    parameters = {"filename": os.path.split(filename)[1]}

    fileheader = {}

    with open(filename, "r") as f:
        for line in f:
            iq_match = iq_pattern.match(line)
            param_match = param_pattern.match(line)

            if iq_match:
                found = iq_match.group().split()
                q.append(float(found[0]))

                i.append(float(found[1]))

                err.append(float(found[2]))

            if param_match:
                found = param_match.group().split()

                if len(found) == 3:
                    try:
                        val = float(found[2])
                    except ValueError:
                        val = found[2]

                    fileheader[found[0]] = val

                elif len(found) > 3:
                    arr = []
                    for each in range(2, len(found)):
                        try:
                            val = float(found[each])
                        except ValueError:
                            val = found[each]

                        arr.append(val)

                    fileheader[found[0]] = arr
                else:
                    fileheader[found[0]] = ""

    parameters = {"filename": os.path.split(filename)[1], "counters": fileheader}

    i = np.array(i)
    q = np.array(q)
    err = np.array(err)

    return SASM.SASM(i, q, err, parameters)


def loadIntFile(filename):
    """Loads a simulated SAXS data curve .int or .abs file"""
    fit_list = [two_col_fit, three_col_fit, four_col_fit, five_col_fit, seven_col_fit]

    i = []
    q = []
    err = []

    with open(filename, "r") as f:
        firstLine = f.readline()

        match = [fit.match(firstLine) for fit in fit_list]

        if any(match):
            fileHeader = {}
        else:
            fileHeader = _parse_header_line(firstLine)

        parameters = {"filename": os.path.split(filename)[1], "counters": fileHeader}

        if len(fileHeader) == 0:
            q, i = _match_int_lines(firstLine, q, i, fit_list)

        for line in f:
            q, i = _match_int_lines(line, q, i, fit_list)

    i = np.array(i)
    q = np.array(q)
    err = np.sqrt(abs(i))

    return SASM.SASM(i, q, err, parameters)


def loadTxtFile(filename):
    """Loads a generic two or three column text file with space, tab, or comma separated values"""
    fit_list = [three_col_fit, i_q_err_match, two_col_fit, i_q_match]

    i = []
    q = []
    err = []

    with open(filename, "r") as f:
        firstLine = f.readline()

        match = [fit.match(firstLine) for fit in fit_list]

        if any(match):
            fileHeader = {}
        else:
            fileHeader = {"comment": firstLine}
            firstline_l = firstLine.lower()
            if "chi^2" in firstline_l:
                chisq = firstline_l.split("chi^2")[-1].strip(":= ").split()[0].strip()
                fileHeader["Chi_squared"] = float(chisq)

            if "rg" in firstline_l:
                rg = firstline_l.split("rg")[-1].strip("t:= ").split()[0].strip()
                fileHeader["Rg"] = float(rg)

            if "dro" in firstline_l:
                dro = firstline_l.split("dro")[-1].strip(":= ").split()[0].strip()
                fileHeader["Hydration_shell_contrast"] = float(dro)

            if "vol" in firstline_l:
                vol = firstline_l.split("vol")[-1].strip(":= ").split()[0].strip()
                fileHeader["Excluded_volume"] = float(vol)

        parameters = {"filename": os.path.split(filename)[1], "counters": fileHeader}

        if len(fileHeader) == 0:
            q, i, err = _match_txt_lines(firstLine, q, i, err, fit_list)

        for line in f:
            q, i, err = _match_txt_lines(line, q, i, err, fit_list)

    i = np.array(i)
    q = np.array(q)

    if len(err) == len(i):
        err = np.array(err)
    else:
        err = np.sqrt(abs(i))

    return SASM.SASM(i, q, err, parameters)


def loadFitFile(filename):
    i = []
    q = []
    err = []
    fit = []

    with open(filename, "r") as f:
        firstLine = f.readline()

        three_col_match = three_col_fit.match(firstLine)
        four_col_match = four_col_fit.match(firstLine)
        five_col_match = five_col_fit.match(firstLine)
        if three_col_match or four_col_match or five_col_match:
            fileHeader = {}

        else:
            fileHeader = _parse_header_line(firstLine)

        if "Experimental" in firstLine:
            sasref = True  # SASREFMX Fit file (Damn those hamburg boys and their 50 different formats!)
        else:
            sasref = False

        parameters = {"filename": os.path.split(filename)[1], "counters": fileHeader}

        path_noext, ext = os.path.splitext(filename)

        fit_parameters = {
            "filename": os.path.split(path_noext)[1] + "_FIT",
            "counters": fileHeader,
        }

        if len(fileHeader) == 0:
            q, i, err, fit = _match_fit_lines(firstLine, q, i, err, fit, sasref)

        for line in f:
            q, i, err, fit = _match_fit_lines(line, q, i, err, fit, sasref)

    if len(i) == 0:
        raise SASExceptions.UnrecognizedDataFormat(
            "No data could be retrieved from the file, unknown format."
        )

    q = np.array(q)
    i = np.array(i)
    err = np.array(err)
    fit = np.array(fit)

    fit_sasm = SASM.SASM(fit, np.copy(q), np.copy(err), fit_parameters)

    sasm = SASM.SASM(i, q, err, parameters)

    return [sasm, fit_sasm]


def loadIftFile(filename):
    # Loads RAW BIFT .ift files into IFTM objects
    iq_pattern = four_col_fit
    pr_pattern = three_col_fit
    extrap_pattern = two_col_fit

    r = []
    p = []
    err = []

    q = []
    i = []
    err_orig = []
    fit = []

    q_extrap = []
    fit_extrap = []

    with open(filename, "r") as f:
        path_noext, ext = os.path.splitext(filename)

        for line in f:
            pr_match = pr_pattern.match(line)
            iq_match = iq_pattern.match(line)
            extrap_match = extrap_pattern.match(line)

            if pr_match:
                found = pr_match.group().split()

                r.append(float(found[0]))
                p.append(float(found[1]))
                err.append(float(found[2]))

            elif iq_match:
                found = iq_match.group().split()

                q.append(float(found[0]))
                i.append(float(found[1]))
                err_orig.append(float(found[2]))
                fit.append(float(found[3]))

            elif extrap_match:
                found = extrap_match.group().split()

                q_extrap.append(float(found[0]))
                fit_extrap.append(float(found[1]))

    p = np.array(p)
    r = np.array(r)
    err = np.array(err)
    i = np.array(i)
    q = np.array(q)
    err_orig = np.array(err_orig)
    fit = np.array(fit)
    q_extrap = np.array(q_extrap)
    fit_extrap = np.array(fit_extrap)

    # Check to see if there is any header from RAW, and if so get that.
    with open(filename, "r") as f:
        all_lines = f.readlines()

    header = []
    for j in range(len(all_lines)):
        if "### HEADER:" in all_lines[j]:
            header = all_lines[j + 1 :]

    hdict = {}

    if len(header) > 0:
        hdr_str = ""
        for each_line in header:
            hdr_str = hdr_str + each_line.lstrip("#")
        try:
            hdict = dict(json.loads(hdr_str))
        except Exception:
            pass

    parameters = hdict
    parameters["filename"] = os.path.split(filename)[1]

    if q.size == 0:
        q = np.array([0, 0])
        i = q
        err_orig = q
        fit = q

    if q_extrap.size == 0:
        q_extrap = q
        fit_extrap = fit

    iftm = SASM.IFTM(p, r, err, i, q, err_orig, fit, parameters, fit_extrap, q_extrap)

    return [iftm]


def loadOutFile(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    iftm = parse_out_file(lines)

    iftm.setParameter("filename", os.path.basename(filename))

    return [iftm]


def checkFileType(filename):
    """Tries to find out what file type it is and reports it back"""

    path, ext = os.path.splitext(filename)

    if ext == ".fit":
        return "fit"
    elif ext == ".fir":
        return "fir"
    elif ext == ".abs":
        return "abs"
    elif ext == ".out":
        return "out"
    elif ext == ".nxs":  # Nexus file
        return "image"
    elif ext == ".edf":
        return "image"
    elif ext == ".ccdraw":
        return "image"
    elif ext == ".int":
        return "int"
    elif (
        ext == ".img"
        or ext == ".imx_0"
        or ext == ".dkx_0"
        or ext == ".dkx_1"
        or ext == ".png"
        or ext == ".mpa"
    ):
        return "image"
    elif ext == ".dat" or ext == ".sub" or ext == ".txt":
        return "primus"
    elif (
        ext == ".mar1200" or ext == ".mar2400" or ext == ".mar2300" or ext == ".mar3600"
    ):
        return "image"
    elif (
        ext == ".img"
        or ext == ".sfrm"
        or ext == ".dm3"
        or ext == ".edf"
        or ext == ".xml"
        or ext == ".cbf"
        or ext == ".kccd"
        or ext == ".msk"
        or ext == ".spr"
        or ext == ".tif"
        or ext == ".mccd"
        or ext == ".mar3450"
        or ext == ".npy"
        or ext == ".pnm"
        or ext == ".No"
    ):
        return "image"
    elif ext == ".ift":
        return "ift"
    elif ext == ".csv":
        return "txt"
    elif ext == ".h5":
        return "hdf5"
    elif ext == ".pdb":
        return "pdb"
    elif ext == ".cif":
        return "cif"
    else:
        try:
            f = fabio.open(filename)
            return "image"
        except Exception:
            try:
                float(ext.strip("."))
            except Exception:
                return "txt"
            return "csv"


def makeDatFile(lines, filename):
    iq_pattern = i_q_err_match

    i = []
    q = []
    err = []

    comment = ""
    line = lines[0]
    j = 0
    while line.split() and line.strip()[0] == "#":
        comment = comment + line
        j = j + 1
        line = lines[j]

    fileHeader = {"comment": comment}
    parameters = {"filename": os.path.split(filename)[1], "counters": fileHeader}

    if comment.find("model_intensity") > -1:
        # FoXS file with a fit! has four data columns
        is_foxs_fit = True
        is_sans_data = False
        imodel = []

    elif comment.find("dQ") > -1:
        # ORNL SANS instrument file
        is_foxs_fit = False
        is_sans_data = True
        qerr = []
    else:
        is_foxs_fit = False
        is_sans_data = False

    header = []
    header_start = False

    for j, line in enumerate(lines):
        iq_match = iq_pattern.match(line)

        if iq_match:
            if is_foxs_fit:
                if "," in line:
                    found = line.split(",")
                else:
                    found = line.split()
                q.append(float(found[0]))
                i.append(float(found[1]))
                imodel.append(float(found[2]))
                err.append(abs(float(found[3])))

            elif is_sans_data:
                found = iq_match.group()
                if "," in found:
                    found = line.split(",")
                else:
                    found = line.split()
                q.append(float(found[0]))
                i.append(float(found[1]))
                err.append(abs(float(found[2])))
                qerr.append(abs(float(found[3])))

            else:
                found = iq_match.group()
                if "," in found:
                    found = found.split(",")
                else:
                    found = found.split()
                q.append(float(found[0]))
                i.append(float(found[1]))
                err.append(abs(float(found[2])))

        # Check to see if there is any header from RAW, and if so get that.
        # Header at the bottom
        if "### HEADER:" in line and len(q) > 0:
            header = lines[j + 1 :]

            # For headers at the bottom, stop trying the regex
            if len(q) > 0:
                break

        # Header at top
        elif "### HEADER:" in line and len(q) == 0:
            header_start = True

        elif header_start and "### DATA:" in line:
            header_start = False

        elif header_start and not iq_match:
            header.append(lines[j])

    if len(header) > 0:
        hdr_str = ""
        for each_line in header:
            hdr_str = hdr_str + each_line.lstrip("#")

        hdict = loadDatHeader(hdr_str)

        for each in hdict:
            if each != "filename":
                parameters[each] = hdict[each]

    i = np.array(i)
    q = np.array(q)
    err = np.array(err)

    sasm = SASM.SASM(i, q, err, parameters)

    if is_foxs_fit:
        parameters2 = copy.copy(parameters)
        parameters2["filename"] = (
            os.path.splitext(os.path.split(filename)[1])[0] + "_FIT"
        )

        sasm_model = SASM.SASM(imodel, q, err, parameters2)

        return [sasm, sasm_model]

    elif is_sans_data:
        sasm.setRawQErr(np.array(qerr))
        sasm._update()

    return sasm


def postProcessProfile(sasm, raw_settings, no_processing):
    """
    Does post-processing on profiles created from images.
    """
    SASM.postProcessSasm(sasm, raw_settings)  # Does dezingering

    if not no_processing:
        # Need to do a little work before we can do glassy carbon normalization
        if raw_settings.get("NormAbsCarbon") and not raw_settings.get(
            "NormAbsCarbonIgnoreBkg"
        ):
            bkg_filename = raw_settings.get("NormAbsCarbonSamEmptyFile")
            bkg_sasm = raw_settings.get("NormAbsCarbonSamEmptySASM")
            if (
                bkg_sasm is None
                or bkg_sasm.getParameter("filename") != os.path.split(bkg_filename)[1]
            ):
                bkg_sasm, junk_img = loadFile(
                    bkg_filename, raw_settings, no_processing=True
                )
                if isinstance(bkg_sasm, list):
                    if len(bkg_sasm) > 1:
                        bkg_sasm = SASProc.average(bkg_sasm, copy_params=False)
                    else:
                        bkg_sasm = bkg_sasm[0]
                raw_settings.set("NormAbsCarbonSamEmptySASM", bkg_sasm)

        try:
            # Does fully glassy carbon abs scale
            SASCalib.postProcessImageSasm(sasm, raw_settings)
        except SASExceptions.AbsScaleNormFailed:
            raise


# Define regular expressions for ascii files
start_match = r"\s*"
end_match = r"\s*$"
num_match = r"[\+-]?\d+\.?\d*[+eE-]*\d*"
sep_match = r"\s*[\s,]\s*"
alt_sep_match = r"\s*[\s,]?\s*"

two_col_fit = re.compile(
    start_match + (num_match + sep_match) * 1 + num_match + end_match
)
i_q_match = re.compile(
    start_match + (num_match + sep_match) * 1 + num_match + alt_sep_match
)
three_col_fit = re.compile(
    start_match + (num_match + sep_match) * 2 + num_match + end_match
)
i_q_err_match = re.compile(
    start_match + (num_match + sep_match) * 2 + num_match + alt_sep_match
)
four_col_fit = re.compile(
    start_match + (num_match + sep_match) * 3 + num_match + end_match
)
five_col_fit = re.compile(
    start_match + (num_match + sep_match) * 4 + num_match + end_match
)
seven_col_fit = re.compile(
    start_match + (num_match + sep_match) * 6 + num_match + end_match
)


# ----- Added for SASDD22
def loadDatHeader(header):
    try:
        hdict = dict(json.loads(header))
        # print 'Loading RAW info/analysis...'
    except Exception:
        # print 'Unable to load header/analysis information. Maybe the file was not generated by RAW or was generated by an old version of RAW?'
        hdict = {}

    if hdict:
        hdict = translateHeader(hdict, to_sasbdb=False)

    return hdict


def translateHeader(header, to_sasbdb=True):
    """
    Translates the header keywords to or from matching SASBDB format. This is
    to add compatibility with SASBDB while maintaining compatibility with older
    RAW formats and RAW internals.
    """
    new_header = copy.deepcopy(header)

    for key in header.keys():
        if isinstance(header[key], dict):
            new_header[key] = translateHeader(header[key], to_sasbdb)
        else:
            if to_sasbdb:
                if key in sasbdb_trans:
                    new_header[sasbdb_trans[key]] = new_header.pop(key)
            else:
                if key in sasbdb_back_trans:
                    new_header[sasbdb_back_trans[key]] = new_header.pop(key)

    return new_header


sasbdb_trans = {
    # First general RAW keywords
    "Sample_Detector_Distance": "Sample-to-detector distance (mm)",
    "Wavelength": "Wavelength (A)",
    # Next BioCAT specific keywords
    "Exposure_time/frame_s": "Exposure time/frame (s)",
    "LC_flow_rate_mL/min": "Flow rate (ml/min)",
}

sasbdb_back_trans = {value: key for (key, value) in sasbdb_trans.items()}


def _match_txt_lines(line, q, i, err, fit_list):
    for fit in fit_list:
        match = fit.match(line)

        if match:
            data = match.group()
            if "," in data:
                data = data.split(",")
            else:
                data = data.split()

            q.append(float(data[0]))
            i.append(float(data[1]))

            if len(data) == 3:
                try:
                    err.append(float(data[2]))
                except Exception:
                    pass

            break

    return q, i, err
