#%% Imports -------------------------------------------------------------------

import numpy as np
from joblib import Parallel, delayed 

# bdtools
from bdtools.norm import norm_pct

# Scipy
from scipy.ndimage import distance_transform_edt

# Skimage
from skimage.measure import label
from skimage.filters import gaussian
from skimage.transform import rescale, resize
from skimage.segmentation import find_boundaries
from skimage.morphology import binary_dilation, skeletonize

#%% Function: get_edt ---------------------------------------------------------

def get_edt(
        arr, 
        target="foreground", 
        sampling=1, 
        normalize="none", 
        rescale_factor=1, 
        parallel=True
        ):
        
    """ 
    Euclidean distance tranform.
    Based on scipy.ndimage distance_transform_edt().

    Compute Euclidean distance tranform (edt) for boolean or integer labelled
    mask array. If boolean, edt is applied over the entire array, whereas if 
    labelled, edt is applied individually for each objects.
    
    Parameters
    ----------
    arr : 2D or 3D ndarray (bool or uint8, uint16, int32)
        Boolean : True foreground, False background.
        Labelled : non-zero integers objects, 0 background.
        
    target : str, optional, default="foreground"
        - "foreground" : foreground distance to closest background pixel.
        - "background" : background distance to closest foreground pixel.
        
    sampling : float or tuple of floats, optional, default=1
        From Scipy "Spacing of elements along each dimension. If a sequence, 
        must be of length equal to the input rank; if a single number, this is
        used for all axes".
    
    normalize : str, optional, default="none"
        - "none" : no normalization.
        - "global" : 0 to 1 normalization globally over the entire array.
        - "object" : 0 to 1 normalization for each object individually.
    
    rescale_factor : float, optional, default=1.
        Rescaling factor applied to input array before processing. Rescaling
        introduces precision loss, especially near object boundaries or for 
        small objects.
    
    parallel : bool
        Compute edt in parallel if True and target is "foreground".
                
    Returns
    -------  
    edt : 2D or 3D ndarray (float)
        Euclidean distance tranform of the input array.
        
    """
    
    if not (np.issubdtype(arr.dtype, np.integer) or
            np.issubdtype(arr.dtype, np.bool_)):
        raise TypeError("Provided array must be bool or integers labels")
        
    if np.all(arr == arr.flat[0]):
        return np.zeros_like(arr, dtype="bool")
    
    valid_targets = ["foreground", "background"]
    if target not in valid_targets:
        raise ValueError(
            f"Invalid value for target: '{target}'."
            f" Expected one of {valid_targets}."
            )
    
    valid_normalize = ["none", "global", "object"]
    if normalize not in valid_normalize:
        raise ValueError(
            f"Invalid value for normalize: '{normalize}'."
            f" Expected one of {valid_normalize}."
            )

    # Nested function(s) ------------------------------------------------------
    
    def _get_edt(lab, normalize=normalize):
        edt = arr == lab
        edt = binary_dilation(edt)
        edt = distance_transform_edt(edt, sampling=sampling) * 1 / rescale_factor
        if normalize == "object":
            edt = norm_pct(edt, pct_low=0, pct_high=99.9, mask=edt > 0)
        return edt
        
    # Execute -----------------------------------------------------------------
    
    arr = arr.copy()
    
    if rescale_factor < 1:
        arr_copy = arr.copy()
        arr = rescale(arr, rescale_factor, order=0)
            
    if target == "foreground":
        arr[find_boundaries(arr, mode="inner") == 1] = 0
        arr = label(arr > 0)
        labels = np.unique(arr)[1:]
        if parallel:
            edt = Parallel(n_jobs=-1)(
                delayed(_get_edt)(lab) for lab in labels)
        else:
            edt = [_get_edt(lab) for lab in labels]        
        edt = np.nanmax(np.stack(edt), axis=0).astype("float32")
    else:
        edt = distance_transform_edt(np.invert(arr > 0), sampling=sampling)
        
    if normalize == "global":
        edt = norm_pct(edt, pct_low=0, pct_high=99.9, mask=edt > 0)
        
    if rescale_factor < 1:
        edt = resize(edt, arr_copy.shape, order=1)
        edt = gaussian(edt, sigma=1 / rescale_factor / 2)
        if target == "foreground":
            edt[arr_copy == 0] = 0
        else:
            edt[arr_copy != 0] = 0
        
    return edt
            
#%% Function: get_skel() ------------------------------------------------------

def get_skel(arr, parallel=True):
    
    """ 
    Skeletonize.
    Based on scipy.ndimage skeletonize().

    Compute skeleton for boolean or integer labelled mask array. If boolean, 
    skeletonize() is applied over the entire array, whereas if labelled, 
    skeletonize() is applied individually for each objects.
    
    Parameters
    ----------
    arr : 2D ndarray (bool or uint8, uint16, int32)
        Boolean : True foreground, False background.
        Labelled : non-zero integers objects, 0 background.
    
    parallel : bool
        Compute skeletonize() in parallel if True.
                
    Returns
    -------  
    skel : 2D ndarray (bool)
        skeleton of the input array.
        
    """
    
    if not (np.issubdtype(arr.dtype, np.integer) or
            np.issubdtype(arr.dtype, np.bool_)):
        raise TypeError("Provided array must be bool or integers labels")
        
    if np.all(arr == arr.flat[0]):
        return np.zeros_like(arr, dtype="bool")
    
    # Nested function(s) ------------------------------------------------------
    
    def _get_skel(lab):
        skel = np.zeros_like(arr)
        skel[arr == lab] = True
        skel = skeletonize(skel)
        return skel
    
    # Execute -----------------------------------------------------------------
    
    arr = arr.copy()
    arr[find_boundaries(arr, mode="inner") == 1] = 0
    arr = label(arr > 0)
    labels = np.unique(arr)[1:]
    if parallel:
        skel = Parallel(n_jobs=-1)(
            delayed(_get_skel)(lab) for lab in labels)
    else:
        skel = [_get_skel(lab) for lab in labels]   
    skel = np.max(np.stack(skel), axis=0)
    
    return skel

#%% Execute -------------------------------------------------------------------

if __name__ == "__main__":
        
    # Imports
    import time
    import napari
    from skimage import io
    from pathlib import Path

    # Parameters
    # dataset = "em_mito"
    dataset = "fluo_nuclei_instance"
    img_norm = "global"
    msk_type = "skeletons"
    patch_size = 128
    patch_overlap = 0
    
    # Paths
    local_path = Path.cwd().parent / "_local"
    msks_path = local_path / f"{dataset}" / f"{dataset}_msk_trn.tif"
    
    # Load masks
    msks = io.imread(msks_path)

    # get_edt()
    print("get_edt() : ", end="", flush=True)
    t0 = time.time()
    edt_outputs = []
    for msk in msks:
        edt_outputs.append(
            get_edt(
                msk, 
                target="foreground", 
                sampling=1, 
                normalize="none", 
                rescale_factor=1, 
                parallel=True,
                )   
            )
    edt_outputs = np.stack(edt_outputs)
    t1 = time.time()
    print(f"{t1 - t0:.3f}s")
    
    # get_skel()
    print("get_skel() : ", end="", flush=True)
    t0 = time.time()
    skel_outputs = []
    for msk in msks:
        skel_outputs.append(get_skel(msk, parallel=True))
    skel_outputs = np.stack(skel_outputs)
    t1 = time.time()
    print(f"{t1 - t0:.3f}s")
    
    # Display
    viewer = napari.Viewer()
    viewer.add_labels(msks)
    viewer.add_image(edt_outputs, blending="additive")
    viewer.add_image(skel_outputs, blending="additive")