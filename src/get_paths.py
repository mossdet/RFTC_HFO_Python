import os


path = os.path.dirname(os.path.abspath(__file__))
cutIdx = path.rfind(os.path.sep)
workspacePath = path[:cutIdx]
cutIdx = path.rfind(os.path.sep)
workspacePath = path[:cutIdx]
images_path = workspacePath + os.path.sep + 'Images' + os.path.sep
data_path = workspacePath + os.path.sep + 'Data' + os.path.sep
eeg_path = data_path + 'EEG' + os.path.sep
micromed_eeg_path = "F:/ForschungsProjekte/RFTC/Project_Files/PatientFilesMicromed/AllPatients/"
coordinates_path = data_path + 'Coordinates' + os.path.sep
characterization_paths = data_path + 'Characterization' + os.path.sep

os.makedirs(data_path, exist_ok=True)
os.makedirs(images_path, exist_ok=True)


def get_images_path():
    return images_path


def get_data_path():
    return data_path


def get_eeg_path():
    return eeg_path


def get_micromed_eeg_path():
    return micromed_eeg_path


def get_coordinates_path():
    return coordinates_path


def get_charact_paths():
    return characterization_paths
