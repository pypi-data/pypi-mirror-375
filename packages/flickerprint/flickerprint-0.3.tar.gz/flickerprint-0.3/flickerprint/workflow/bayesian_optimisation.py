import numpy as np
import os
from datetime import datetime
import skimage as ski
import tensorflow as tf
import trieste
import warnings

from trieste.models.gpflow import build_gpr, GaussianProcessRegression
from trieste.acquisition.rule import EfficientGlobalOptimization

from dataclasses import dataclass
from pathlib import Path

import flickerprint.common.boundary_extraction as be
from flickerprint.common.configuration import config
from flickerprint.common import configuration
import flickerprint.common.granule_locator as gl
import flickerprint.common.frame_gen as fg


""" Perform Bayesian optimisation to determine parameters for DoG algorithm.
"""

@dataclass
class GranuleDetectorBayes(gl.GranuleDetector):
    """
    Daughter Class to Granule Dector.
    """ 
    def findGranules(self, threshold, min_sigma, max_sigma):
        """
        Redefine class to accomendate for structure of optimisation.
        """
        method = config("image_processing","method")

        if (method == "gradient"):
            self.processed_image = self.frame.im_data
        elif (method == "intensity"):
            self.processed_image = gl._process_vesicles(self.frame.im_data)
        else:
            raise ValueError("no granule detection method {}".format(method))

        min_size = _convertFromSigma(min_sigma, self.frame.pixel_size)
        max_size = _convertFromSigma(max_sigma, self.frame.pixel_size)

        self.granule_locations = gl._detect_granules_dog( 
            self.processed_image,
            min_size,
            max_size,
            self.frame.pixel_size,
            threshold=threshold,
        )

        return self.granule_locations

    def flood_granules(self, min_sigma, max_sigma, threshold):
        """
        Return the number of granules that can be succesfully flooded.
        """
        blobs_mask = [self._fillGranule(blob, min_sigma, max_sigma, threshold) for blob in self.granule_locations]
        blobs_area = np.array([np.sum(i) if i is not None else 0 for i in blobs_mask])

        blobs_accepted_mask = blobs_area > 0
        return np.sum(blobs_accepted_mask)

    def _fillGranule(self, blob, min_sigmaBO, max_sigmaBO, thresholdBO):
        """
        Adapted version of the _fillGranule method from the main class to work with the 
        Bayesian optimisation framework.
        """
        threshold = float(config("image_processing", "fill_threshold"))

        method = config("image_processing","method")

        x, y, r = blob
        x = int(x)
        y = int(y)

        # Move x, y to the brightest spot in the surrounding region
        prev_intensity = self.processed_image[x, y]
        x, y = self._refineCentre(x, y, radius=5)
        new_intensity = self.processed_image[x, y]

        if new_intensity < prev_intensity:
            print(f"{prev_intensity:6d} {new_intensity:6d}", end=" ")
            print("Error!")

        # Filter on the magnitude of the central point
        center_intensity = self.processed_image[x, y]
        # TODO: Scale this by the maximum intensity of the image
        max_intensity = self.processed_image.max()
        if center_intensity < max_intensity * thresholdBO:
            return None

        if (method == "gradient"):
            # The tolerance is the difference from centre point in abs. intensity
            tolerance = center_intensity * (1.0 - threshold)
        elif (method == "intensity"):
            # mask is binary so no tolerance needed
            tolerance = None
        else:
            raise ValueError("no granule detection method {}".format(method))

        # First test
        mask = ski.morphology.flood(
            self.processed_image, (x, y), tolerance=tolerance, connectivity=1
        )

        area = mask.sum()

        # Filter out granules with areas which fall outside of the threshold range.
        pixel_size = self.frame.pixel_size

        min_size = _convertFromSigma(min_sigmaBO, pixel_size)
        max_size = _convertFromSigma(max_sigmaBO, pixel_size)

        if pixel_size == None:
            pixel_size = 1
        if area > int(np.pi * max_size ** 2 / pixel_size ** 2):
            return None
        if area < int(np.pi * min_size ** 2 / pixel_size ** 2):
            return None

        return mask
    
    def labelGranules(self, min_sigma, max_sigma, threshold):
        """
        Keeps the same structure has the original labelGranules but is adaptet such that it
        takes the parameters from the Bayesian optimisation as input.
        """
        method = config("image_processing","method")

        if (method == "gradient"):
            self.processed_image = self.frame.im_data
        elif (method == "intensity"):
            self.processed_image = gl._process_vesicles(self.frame.im_data)
        else:
            raise ValueError("no granule detection method {}".format(method))

        pixel_size = self.frame.pixel_size

        min_size = _convertFromSigma(min_sigma, pixel_size)
        max_size = _convertFromSigma(max_sigma, pixel_size)

        self.granule_locations = gl._detect_granules_dog( 
                self.processed_image,
                min_size,
                max_size,
                self.frame.pixel_size,
                threshold=threshold,
            ) 

        self.labelled_granules, n_granules = self._fillGranules(min_sigma, max_sigma, threshold)
        return self.labelled_granules, n_granules

    def _fillGranules(self, min_sigma, max_sigma, threshold):
        """
        Keeps the same structure has the original labelGranules but is adaptet such that it
        takes the parameters from the Bayesian optimisation as input.

        _fillGranule method is changed 
        """
        # Generate a masked binary image for each of the granules, removing those
        # where we fail to find a granule
        masks = [self._fillGranule(b, min_sigma, max_sigma, threshold) for b in self.granule_locations]
        self.mask_area = np.array([True if i is not None else False for i in masks])
        masks = list(filter(lambda m: m is not None, masks))
        masks = np.array(masks, dtype=np.int16)

        if len(masks) == 0:
            return None, 0

        # OR all of the masks into one image, this ignores overlapping regions
        self.mask = masks.any(axis=0)
        labelledImage = ski.measure.label(self.mask)
        labelledImage = ski.segmentation.clear_border(labelledImage)
        return labelledImage, len(masks)
    
class Sim:
    def __init__(self, threshold_constraint, images):
        self.threshold = threshold_constraint

        self.images = images

    def constraint(self, input_data):
        """
        Buffer function that acts as function to be optimised in for the optimiser.
        Calls "real" function with the threshold values and gives additional fixed parameters (i.e. data).
        """
        threshold, min_sigma, max_sigma = extractParametersFromInput(input_data)
        objectives = np.array([bayesOptFunction_maxSG_multiImages(t, mins, maxs, self.images) for t, mins, maxs in zip(threshold, min_sigma, max_sigma)])
        return -tf.constant(np.array([objectives]).T, dtype='float64')
    
    def objective(self, input_data):
        """
        """
        threshold, min_sigma, max_sigma = extractParametersFromInput(input_data)
        objectives = np.array([bayesOptFunction_minBlobs_multiImages(t, mins, maxs, self.images) for t, mins, maxs in zip(threshold, min_sigma, max_sigma)])
        # minus in this case because bayes_opt_function_min_blobs_multi_images returns a negative number
        return -tf.constant(np.array([objectives]).T, dtype='float64')


def _convertFromSigma(sigma, pixel_size):
        """
        Convert sigma values from DoG to physical values
        """
        scale = 1.0 / np.sqrt(2)
        return sigma*pixel_size/scale

def extractParametersFromInput(input_data):
        """
        Transform the parameters used by trieste into a format that can be handled 
        by the optimisation function.
        """
        threshold, min_sigma, max_sigma = input_data[..., -3], input_data[..., -2], input_data[..., -1]
        try:
            threshold = threshold.numpy()
            min_sigma = min_sigma.numpy()
            max_sigma = max_sigma.numpy()
        except AttributeError:
            pass
        return threshold, min_sigma, max_sigma

def bayesOptFunction_maxSG_multiImages(threshold, min_sigma, max_sigma, images):
    """
    Minimalistic optimimzation function.
    Finds the lowest number of flooded blobs for the images of each video file for the given
    parameters. The sum of these are then returned. 
    Goal is to maximise this sum.

    Images refer to video files. From each video file multiple images can be selected. 

    1. Use DoG algorithm with optimisation parameters to find number blobs in the images.
    2. Try to flood the found blobs.
    3. Take the minimum number of blobs that could be flooded in any of the images and add it 
       to the total number of flooded blobs
    4. Objective: sum of the minimum number of blobs in each video file
    """
    boundary_method = config("image_processing", "method")

    total_n_flooded_blobs = 0
    for image in images:
        n_granules_in_image = []
        for frame in image:
            # find all granules/blobs in the frame 
            # frame.findGranules(threshold, min_sigma, max_sigma)
            labelledGranules, n_granules = frame.labelGranules(min_sigma, max_sigma, threshold)

            if n_granules == 0:
                n_granules_in_image.append(n_granules)
                continue

            boundedGranule = []
            for granule in frame.granules():
                be_granule = be.BoundaryExtraction(granule, boundary_method)
                be_granule.angle_sweep(400)
                boundedGranule.append(be_granule.validate_boundary())

            # test how many blobs fulfill flooding criteria
            # n_granules_in_image.append(frame.flood_granules(min_sigma, max_sigma, threshold))
            n_granules_in_image.append(sum(boundedGranule))
        total_n_flooded_blobs += np.min(n_granules_in_image)

    return total_n_flooded_blobs

def bayesOptFunction_minBlobs_multiImages(threshold, min_sigma, max_sigma, images):
    """
    Minimalistic function optimimzation function that only concerns itself with the return of the constraint.
    Only function necessary to calulate the flooding are called.

    !!! Images refer to video files. From each video file multiple images can be selected. 

    1. Uses DoG algorithm to find number of blobs in images
    2. Takes the average number of blobs and adds it to total average number of blobs found 
    """
    total_n_blobs = 0
    for image in images:
        n_blobs_in_image = []
        for frame in image:
            # find the total number of granules/blobs in each frame
            n_blobs_in_image.append(len(frame.findGranules(threshold, min_sigma, max_sigma)))
        total_n_blobs += np.mean(n_blobs_in_image) # maybe max

    return -total_n_blobs/len(images)

def optimisationMaxSG(images, num_steps, num_initial_points=5):
    """
    Wrapper function to initialise and run optimisation to find the maximum number of stress granules.
    """
    # define objective here so I can use images
    def objectiveMaxSG(input_data):
        """
        Buffer function that acts as function to be optimised in for the optimiser.
        Calls "real" function with the threshold values and gives additional fixed parameters (i.e. data).
        """
        threshold, min_sigma, max_sigma = extractParametersFromInput(input_data)

        objectives = np.array([bayesOptFunction_maxSG_multiImages(t, mins, maxs, images) for t, mins, maxs in zip(threshold, min_sigma, max_sigma)])
        return -tf.constant(np.array([objectives]).T, dtype='float64')

    # define search space
    search_space = trieste.space.Box([0.05, 2, 14], [1, 7, 22])

    # define observer
    observer = trieste.objectives.utils.mk_observer(objectiveMaxSG)

    # sample initial points
    initial_query_points = search_space.sample_sobol(num_initial_points)
    initial_data = observer(initial_query_points)

    # build Gaussian model
    gpflow_model = build_gpr(initial_data, search_space, likelihood_variance=None)
    model = GaussianProcessRegression(gpflow_model, num_kernel_samples=100)

    # run optimisation
    bo = trieste.bayesian_optimizer.BayesianOptimizer(observer, search_space)

    result = bo.optimize(num_steps, initial_data, model)
    dataset = result.try_get_final_dataset()

    # print best result
    observations_true = dataset.observations.numpy()
    query_points_true = dataset.query_points.numpy()

    sorted_data = sorted(zip(query_points_true, observations_true), key=lambda x: x[1])

    try:
        print('Best query point: ', sorted_data[0][0])
        print('Corresponding observation value: ', sorted_data[0][1])
    except IndexError:
        print('Could not find any valid points.')
    return dataset

def optimisationReduceInvalidSGs(images, threshold_constraint, num_steps=20, probe_params=None, num_initial_points=5):
    """
    Wrapper function to initialise and run optimisation to reduce the number of invalid SGs.

    Follows very closely the example for constrained optimisation in the trieste documentation.
    """
    # initialise class
    simObject = Sim(threshold_constraint, images)

    # define search space
    search_space = trieste.space.Box([0.05, 2, 14], [1, 7, 22])

    # define observer
    OBJECTIVE = "OBJECTIVE"
    CONSTRAINT = "CONSTRAINT"

    def observer(query_points):
        return {
            OBJECTIVE: trieste.data.Dataset(query_points, simObject.objective(query_points)),
            CONSTRAINT: trieste.data.Dataset(query_points, simObject.constraint(query_points)),
    }

    # initial points
    if probe_params is not None:
        if len(probe_params) < num_initial_points:
            probe_params_np = probe_params.numpy()
            random_probe = search_space.sample_sobol(num_initial_points - len(probe_params)).numpy()
            initial_data = observer(np.concatenate([probe_params_np, random_probe]))
        else:
            initial_data = observer(probe_params)
    else:
        initial_data = observer(search_space.sample_sobol(num_initial_points))

    # define BO model
    def create_bo_model(data):
        gpr = build_gpr(data, search_space, likelihood_variance=1e-7)
        return GaussianProcessRegression(gpr)

    initial_models = trieste.utils.map_values(create_bo_model, initial_data)

    # define acquisition processes 
    pof = trieste.acquisition.ProbabilityOfFeasibility(threshold=simObject.threshold)
    eci = trieste.acquisition.ExpectedConstrainedImprovement(
        OBJECTIVE, pof.using(CONSTRAINT)
    )
    rule = EfficientGlobalOptimization(eci)  # type: ignore

    # run optimisation
    bo = trieste.bayesian_optimizer.BayesianOptimizer(observer, search_space)

    result = bo.optimize(
        num_steps, initial_data, initial_models, rule, track_state=False
    )
    data = result.try_get_final_datasets()
    return data

def check_dir_structure(experiment_dir):
    """
    Check the directory structure to make sure everything needed is there.
    If the config file specifices a microscope file location different from the default, this will be used instead.
    """
    l_required_files = ['images', 'config.yaml']
    if experiment_dir.exists():
        l_dir_content = os.listdir(experiment_dir)
        if not len(set(l_required_files).intersection(l_dir_content)):
            raise ValueError(f'Provided directory {experiment_dir} does not have the required project file structure.')
    else:
        raise IOError(f"Provided output_dir is not directory: {experiment_dir}")
    if config("workflow", "image_dir") != "default_images":
        if Path(config("workflow", "image_dir")).exists():
            return get_image_pathes(config("workflow", "image_dir"))
        else:
            raise IOError(f"Provided Microscope image directory {config('workflow', 'image_dir')} is not a valid directory.")
    else:
        return get_image_pathes(os.path.join(experiment_dir, 'images'))

def get_image_pathes(dir_path):
    """
    Returns a list containing all image pathes.
    """
    images_names = os.listdir(dir_path)
    images_pathes = [os.path.join(dir_path, i) for i in images_names]
    return np.sort(images_pathes)

def get_random_indicies(n_images, n_samples, method='random', rng=None):
    """
    Returns an array of length n_samples of random indicies. The indicies lie between 0 and n_images.
    """
    if rng is None:
        rng = np.random.default_rng(None)
    if method == 'random':
        # images_indices = rng.integers(n_images, size=n_samples)
        images_indices = rng.permutation(n_images)[:n_samples]
    elif method == 'sequential':
        images_index = rng.integers(n_images - n_samples, size=1)[0]
        images_indices = np.arange(images_index, images_index + n_samples, 1)
    elif method == 'batch':
        print('Not implemented yet.')
    else:
        raise NameError(f'{method} is not a valid method. Choose one of the following three: random, sequential, batch.')
    
    return images_indices

def get_sorted_results(data, threshold=None):
    """
    Get the values of the best attempt in the optimisation.

    Returns
    -------
    sorted_data : np.array
        List of querry points sorted by optimisation score
    """
    if threshold is None:
        observations_true = data.observations.numpy()
        query_points_true = data.query_points.numpy()
    else:
        mask_true = (data['CONSTRAINT'].observations.numpy() < threshold)[:,0]
        observations_true = data['OBJECTIVE'].observations.numpy()[mask_true]
        query_points_true = data['OBJECTIVE'].query_points.numpy()[mask_true]

    sorted_data = sorted(zip(query_points_true, observations_true), key=lambda x: x[1])
    return sorted_data

def run_parameter_search(l_granule_detectors, n_iter=30, constraint_multiplier=0.9, verbose=2):
    """
    Initiate the partly lexicographic Bayesian optimisation.
    First runs a maximisation to find all possible granules.
    Afterwards runs an minimisation to reduce the number of blobs found. The minimisation runs with the constraint to
    keep the number of SG above a certain threshold. 

    Returns
    ------
    data_blobs_sorted : list
        List of all querry points sorted by objective
    """
    # optimiser_max_SG = optimisationWrapper_maxSG(l_granule_detectors, n_iter=n_iter, verbose=verbose)
    data_max_SG = optimisationMaxSG(l_granule_detectors, n_iter)
    print('Finished first optimization.')

    # sort the results of the first optimisation by optimisation score
    max_SG_results_sorted = get_sorted_results(data_max_SG)

    # take lowest integer below to allow for a bit more freedom
    max_SG = np.floor(max_SG_results_sorted[0][1][0])

    # determine how many "good" granules the paramaters should find
    max_SG_sub = max_SG * constraint_multiplier

    # get the best results from the previous optimisation and use these as initial guesses
    # for the next optimisation 
    probe_params = [i[0] for i in max_SG_results_sorted if i[1] > max_SG_sub][:5]
    probe_params = tf.constant(probe_params)

    # call second optimsation function
    data_min_blobs = optimisationReduceInvalidSGs(l_granule_detectors, max_SG_sub, n_iter, probe_params)
    data_blobs_sorted = get_sorted_results(data_min_blobs, max_SG_sub)
    return data_blobs_sorted

def update_config_file(data, config_location, frame):
    """
    Update the parameter values in the config file with the new values from the optimisation.
    """
    # get the best result from the sorted data
    parameter = data[0][0]
    
    pixel_size = frame.pixel_size
    # Read in the current configuration settings
    # d_parameter_config = config.parse_config(config_location)
    d_parameter_config = {}
    d_parameter_config['granule_minimum_intensity'] = parameter[0]
    d_parameter_config['granule_minimum_radius'] = _convertFromSigma(parameter[1], pixel_size)
    d_parameter_config['granule_maximum_radius'] = _convertFromSigma(parameter[2], pixel_size)

    _save_old_parameter(config_location)
    # I think this is overwriting the current specified values and putting them back to the default (where they are not specified).
    # We need to to read all of the current parameters above first.
    configuration.write_config(d_parameter_config, config_location)
    config.refresh(config_location)

def _save_old_parameter(config_location):
    """
    Log the old parameters into 'old_parameter.txt'.
    """
    old_parameter = config_location.parent / "old_parameter.txt"
    
    write_mode = 'w'
    if os.path.isfile(old_parameter):
        write_mode = 'a'

    with open(old_parameter, write_mode) as f:
        f.write(f'------ Following parameters have been changed at {datetime.now()} ------ \n')
        f.write(f'granule_minimum_intensity : {config("image_processing", "granule_minimum_intensity")}\n')
        f.write(f'granule_minimum_radius : {config("image_processing", "granule_minimum_radius")}\n')
        f.write(f'granule_maximum_radius : {config("image_processing", "granule_maximum_radius")}\n\n')

def get_images_for_BO(experiment_dir, n_samples, n_frames_per_sample, method, seed=None):
    l_images = check_dir_structure(experiment_dir)
    n_images = len(l_images)

    if n_images < n_samples:
        n_samples = n_images

    rng = np.random.default_rng(seed)
    l_image_indicies = get_random_indicies(n_images, n_samples, method=method, rng=rng)
    l_images = l_images[l_image_indicies]
    
    l_frames_in_images = []
    for e, im_path in enumerate(l_images):
        gen_image = fg.bioformatsGen(Path(im_path))
        first_frame = next(gen_image)
        n_frames = first_frame.total_frames

        l_frame_indicies = get_random_indicies(n_frames, n_frames_per_sample, method=method, rng=rng)
        
        l_frames = []
        for e, frame in enumerate(gen_image):
            if e not in l_frame_indicies:
                continue
            else:
                l_frames.append(GranuleDetectorBayes(frame))
                if len(l_frames) == n_frames_per_sample:
                    break
        l_frames_in_images.append(l_frames)
    return l_frames_in_images

@fg.vmManager
def main(experiment_dir: Path, n_samples: int=12, n_frames_per_sample: int=2, method: str='random', n_iter=30, constraint_multiplier: float=0.9, seed=None):
    """
    Run Bayesian optimisation.
    """

    print(f"\n====================\nParameter Estimation\n====================\n")
    config_location = experiment_dir / "config.yaml"
    print(f"config_location = {config_location}")
    config.refresh(config_location)

    print('Loading images...')
    l_frames_in_images = get_images_for_BO(experiment_dir, n_samples, n_frames_per_sample, method, seed)

    print('Running optimisation process...')
    warnings.filterwarnings('ignore')
    data_optimisation = run_parameter_search(l_frames_in_images, n_iter=n_iter, constraint_multiplier=constraint_multiplier)
    update_config_file(data_optimisation, config_location, l_frames_in_images[0][0].frame)


if __name__ == '__main__':
    fg.startVM()

    @fg.vmManager
    def main_test():
        experiment_dir = Path('experiments/as_02')
        main(experiment_dir, n_samples=6, n_frames_per_sample=5, n_iter=5, seed=4)

    main_test()