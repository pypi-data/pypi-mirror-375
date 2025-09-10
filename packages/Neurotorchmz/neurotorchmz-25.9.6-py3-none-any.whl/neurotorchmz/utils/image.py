from ..core.task_system import Task  
from ..core.serialize import Serializable, DeserializeError, SerializeError
from ..core.logs import logger

import collections
from dataclasses import asdict
from enum import Enum
from typing import Callable, Self, Any, cast, Literal
import numpy as np
import pims
import tifffile
import nd2
from pathlib import Path
import gc
import time

class ImageProperties:
    """
        A class that supports lazy loading and caching of image properties like mean, median, std, min, max and clippedMin (=np.min(0, self.min))
        Returns scalars (except for the img property, where it returns the image used to initializate this object.
    """
    def __init__(self, img: np.ndarray|None):
        self._img = img
        self._mean = None
        self._std = None
        self._median = None
        self._min = None
        self._max = None


    @property
    def mean(self) -> np.floating|None:
        if self._img is None:
            return None
        if self._mean is None:
            self._mean = np.mean(self._img)
        return self._mean
    
    @property
    def median(self) -> np.floating|None:
        if self._img is None:
            return None
        if self._median is None:
            self._median = np.median(self._img)
        return self._median
    
    @property
    def std(self) -> np.floating|None:
        if self._img is None:
            return None
        if self._std is None:
            self._std = np.std(self._img)
        return self._std
    
    @property
    def min(self) -> np.floating|None:
        if self._img is None:
            return None
        if self._min is None:
            self._min = np.min(self._img)
        return self._min
    
    @property
    def max(self) -> np.floating|None:
        if self._img is None:
            return None
        if self._max is None:
            self._max = np.max(self._img)
        return self._max

    @property
    def minClipped(self) -> np.floating|None:
        if self.min is None:
            return None
        return np.max(np.array([0, self.min]))
    
    @property
    def img(self) -> np.ndarray|None:
        return self._img
    
    def __del__(self):
        del self._img


class AxisImage:
    """
        A class that supports lazy loading and caching of subimages derived from an main image by calculating for example the
        mean, median, std, min or max over an given axis. Note that the axis specifies the axis which should be kept. Returns the image or the ImageProperties
        
        Example for the axis: An AxisImage for an 3D Image (t, y, x) with argument axis=0 will calculate the mean (median, std, min, max) for each pixel.
        Providing axis=(1,2) will calculate the same for each image frame.
    """

    def __init__(self, img: np.ndarray|None, axis:tuple, name: str|None = None):
        self._img = img
        self._img_float = None
        self._axis = axis
        self._name = name
        self._props = None
        self._mean = None
        self._mean_normed = None
        self._std = None
        self._std_normed = None
        self._median = None
        self._min = None
        self._max = None

    @property
    def axis(self) -> tuple:
        return self._axis
    
    @property
    def name(self) -> str|None:
        return self._name

    @property
    def mean_image(self) -> np.ndarray|None:
        """ Mean image over the specified axis """
        return self.mean_props.img

    @property
    def mean_normed_image(self) -> np.ndarray|None:
        """ Normalized Mean image (max value is garanter to be 255 or 0) over the specified axis """
        return self.mean_normed_props.img
    
    @property
    def median_image(self) -> np.ndarray|None:
        """ Median image over the specified axis """
        return self.median_props.img
    
    @property
    def std_image(self) -> np.ndarray|None:
        """ Std image over the specified axis """
        return self.std_props.img
    
    @property
    def std_normed_image(self) -> np.ndarray|None:
        """ Normalized Std image (max value is garanter to be 255 or 0) over the specified axis """
        return self.std_normed_props.img
    
    @property
    def min_image(self) -> np.ndarray|None:
        """ Minimum image over the specified axis """
        return self.min_props.img
    
    @property
    def max_image(self) -> np.ndarray|None:
        """ Maximum image over the specified axis """
        return self.max_props.img
    
    @property
    def image(self) -> np.ndarray|None:
        return self._img
    
    @property
    def image_props(self) -> ImageProperties:
        """ Returns the properties of the original image """
        if self._props is None:
            self._props = ImageProperties(self._img)
        return self._props

    @property
    def mean_props(self) -> ImageProperties:
        """ Returns the mean image properties as float image """
        if self._mean is None:
            if self._img is None:
                self._mean = ImageProperties(None)
            else:
                t0 = time.perf_counter()
                self._mean = ImageProperties(np.mean(self._img, axis=self._axis, dtype="float32"))
                logger.debug(f"Calculated mean view for AxisImage '{self._name if self._name is not None else ''}' on axis '{self._axis}' in {(time.perf_counter() - t0):1.3f} s")
        return self._mean
    
    @property
    def mean_normed_props(self) -> ImageProperties:
        if self._mean_normed is None:
            if self._img is None or self.mean_image is None:
                self._mean_normed = ImageProperties(None)
            else:
                self._mean_normed = ImageProperties((self.mean_image*255/self.mean_props.max).astype(self._img.dtype))
        return self._mean_normed
    
    @property
    def median_props(self) -> ImageProperties:
        if self._median is None:
            if self._img is None:
                self._median = ImageProperties(None)
            else:
                t0 = time.perf_counter()
                self._median = ImageProperties(np.median(self._img, axis=self._axis))
                logger.debug(f"Calculated median view for AxisImage '{self._name if self._name is not None else ''}' on axis '{self._axis}' in {(time.perf_counter() - t0):1.3f} s")
        return self._median
    
    @property
    def std_props(self) -> ImageProperties:
        if self._std is None:
            if self._img is None:
                self._std = ImageProperties(None)
            else:
                t0 = time.perf_counter()
                self._std = ImageProperties(np.std(self._img, axis=self._axis, dtype="float32"))
                logger.debug(f"Calculated std view for AxisImage '{self._name if self._name is not None else ''}' on axis '{self._axis}' in {(time.perf_counter() - t0):1.3f} s")
        return self._std
    
    @property
    def std_normed_props(self) -> ImageProperties:
        if self._std_normed is None:
            if self._img is None or self.std_image is None:
                self._std_normed = ImageProperties(None)
            else:
                self._std_normed = ImageProperties((self.std_image*255/self.std_props.max).astype(self._img.dtype))
        return self._std_normed
    
    @property
    def min_props(self) -> ImageProperties:
        if self._min is None:
            if self._img is None:
                self._min = ImageProperties(None)
            else:
                t0 = time.perf_counter()
                self._min = ImageProperties(np.min(self._img, axis=self._axis))
                logger.debug(f"Calculated minimum view for AxisImage '{self._name if self._name is not None else ''}' on axis '{self._axis}' in {(time.perf_counter() - t0):1.3f} s")
        return self._min
    
    @property
    def max_props(self) -> ImageProperties:
        if self._max is None:
            if self._img is None:
                self._max = ImageProperties(None)
            else:
                t0 = time.perf_counter()
                self._max = ImageProperties(np.max(self._img, axis=self._axis))
                logger.debug(f"Calculated maximum view for AxisImage '{self._name if self._name is not None else ''}' on axis '{self._axis}' in {(time.perf_counter() - t0):1.3f} s")
        return self._max
    
    # def _float_dtype(self, dtype: np.dtype) -> np.dtype:
    #     """ Converts a integer dtype to a integer dtype """
    #     match dtype:
    #         case np.uint8|np.uint16|np.int8|np.float16:
    #             return np.dtype(np.float16)
    #         case _:
    #             return np.dtype(np.float32)


    def copy(self) -> "AxisImage":
        return AxisImage(self._img, self._axis, self._name)
    
    def __del__(self):
        del self._img

class FunctionType(Enum):
    """ A simple wrapper to encode the type of a image function with an priority """

    PRE_FUNCTION = 30
    XY = 20
    T = 10


class ImageObject(Serializable):
    """
        A class for holding a) the image provided in form an three dimensional numpy array (time, y, x) and b) the derived images and properties, for example
        the difference Image (img_diff). All properties are lazy loaded, i. e. they are calculated on first access
    """

    SUPPORTED_EXPORT_EXTENSIONS = [("Lossless compressed Tiff", ("*.tiff", "*.tif"))] 
    
    def __init__(self, conv_cache_size: int = 1, diff_conv_cache_size: int = 3):
        global SignalObject
        from .signal_detection import SignalObject
        self._task_open_image = Task(lambda task, **kwargs: None, "ImageObject", run_async=True, keep_alive=False)
        self.conv_cache_size = conv_cache_size
        self.diff_conv_cache_size = diff_conv_cache_size
        self.clear()

    def clear(self):
        """ Resets the ImageObject and clears all stored images and metadata """
        self._name: str|None = None
        self._name_without_extension: str|None = None
        self._path: Path|None = None
        self._metadata: dict|None = None

        self._img: np.ndarray|None = None
        self._img_views: dict[str, dict[ImageView|None, AxisImage]] = {"default" : {}}
        self._img_functions: list[tuple[str, Callable[[AxisImage], AxisImage], bool, FunctionType|int]] = []

        self._img_diff: np.ndarray|None = None
        self._img_diff_views: dict[str, dict[ImageView|None, AxisImage]] = {"default" : {}}
        self._img_diff_functions: list[tuple[str, Callable[[AxisImage, AxisImage], AxisImage], bool, FunctionType|int]] = []

        self.img_size: int|None = None

        self._signal_obj: SignalObject = SignalObject(self)

    def serialize(self, **kwargs) -> dict:
        r: dict[str, Any] = {
            "name": self._name
        }
        if self._path is not None:
            r["path"] = self._path
        else:
            raise SerializeError("Can not serialize an ImageObject without a path")
        return r
    
    @classmethod
    def deserialize(cls, serialize_dict: dict, **kwargs) -> Self:
        imgObj = cls()
        if "path" not in serialize_dict.keys():
            raise DeserializeError("Can not deserialize an ImageObject without a path") 
        task = imgObj.open_file(serialize_dict["path"], precompute=True)
        task.join()
        return imgObj

    @property
    def name(self) -> str:
        """ Get or set the name of the ImageObject """
        if self._name is None:
            return ""
        return self._name
    
    @name.setter
    def name(self, val):
        if val is None or isinstance(val, str):
            self._name = val

    @property
    def name_without_extension(self) -> str:
        if self._name_without_extension is None:
            return self.name
        return self._name_without_extension
    
    @name_without_extension.setter
    def name_without_extension(self, val):
        if val is None or isinstance(val, str):
            self._name_without_extension = val

    @property
    def path(self) -> Path|None:
        """ Returns the path of the current ImageObject or None if not originating from a file """
        return self._path
    
    @property
    def metadata(self) -> dict[str, Any]|None:
        return self._metadata
    
    # Img and ImageDiff properties

    @property
    def img(self) -> np.ndarray | None:
        """
            Get or set the image. Note that setting to a new value will remove the old diff image

            :raises UnsupportedImageError: The image is not a valid image stack
        """
        return self.img_view(ImageView.DEFAULT).image
    
    @img.setter
    def img(self, image: np.ndarray):
        if not ImageObject._is_valid_image_stack(image): raise UnsupportedImageError()
        self.clear()
        _max = np.max(image)
        if _max <= 1:
            image = 255*image
            _max = 255*_max
        if not (np.issubdtype(image.dtype, np.integer) or np.issubdtype(image.dtype, np.floating)):
            raise UnsupportedImageError(f"The image dtype ({image.dtype}) is not supported")
            
        if np.issubdtype(image.dtype, np.integer):
            if _max < 2**8:
                image = image.astype(np.uint8) if image.dtype != np.uint8 else image
            elif _max < 2**16:
                image = image.astype(np.uint16) if image.dtype != np.uint16 else image
            elif _max < 2**32:
                image = image.astype(np.uint32) if image.dtype != np.uint32 else image
            elif _max < 2**63: # Here 2**63 to support also the signed datatype
                image = image.astype(np.uint64) if image.dtype != np.uint64 else image
            else:
                raise UnsupportedImageError(f"The image dtype ({image.dtype}) is not supported")

        self._img = image
        self.img_size = self._img.nbytes
        
    @property
    def img_raw(self) -> np.ndarray|None:
        """ Returns the image without any convolutions applied """
        return self._img

    @img_raw.setter
    def img_raw(self, image: np.ndarray):
        self.img = image
    
    @property
    def img_diff(self) -> np.ndarray | None:
        """ 
            Get or set the diff image. Note that setting to a new value will remove the old image

            :raises UnsupportedImageError: The image is not a valid image stack
        """
        return self.img_diff_view(ImageView.DEFAULT).image

    @img_diff.setter
    def img_diff(self, image: np.ndarray):
        if not ImageObject._is_valid_image_stack(image): raise UnsupportedImageError()
        self.clear()
        _max = np.max(image)
        if _max <= 1:
            image = 255*image
            _max = 255*_max
        if not (np.issubdtype(image.dtype, np.integer) or np.issubdtype(image.dtype, np.floating)):
            raise UnsupportedImageError(f"The image dtype ({image.dtype}) is not supported")
            
        if np.issubdtype(image.dtype, np.integer):
            if _max < 2**7:
                image = image.astype(np.int8)
            elif _max < 2**15:
                image = image.astype(np.int16)
            elif _max < 2**31:
                image = image.astype(np.int32)
            elif _max < 2**63:
                image = image.astype(np.int64)
            else:
                raise UnsupportedImageError(f"The image dtype ({image.dtype}) is not supported")
        
        self._img_diff = image
        
    @property
    def img_diff_raw(self) -> np.ndarray | None:
        if self._img_diff is None and (_img_signed := self.img_signed) is not None:
            t0 = time.perf_counter()
            self._img_diff = np.diff(_img_signed, axis=0)
            t1 = time.perf_counter()
            logger.debug(f"Calculated the delta video in {(t1-t0):1.3f} s")
        return self._img_diff
    
    @img_diff_raw.setter
    def img_diff_raw(self, image: np.ndarray):
        self.img_diff = image

    @property
    def img_signed(self) -> np.ndarray | None:
        """
            Returns a numpy view with a signed datatype (e.g. for calculating the diffImage). 
        """
        if self._img is None or (_max := self.img_props.max) is None:
            return None
        if self._img.dtype.kind in ("i", "f"):
            return self._img
        if _max < 2**7:
            return self._img.view("int8") if self._img.dtype == np.uint8 else self._img.astype("int8")
        elif _max < 2**15:
            return self._img.view("int16") if self._img.dtype == np.uint16 else self._img.astype("int16")
        elif _max < 2**31:
            return self._img.view("int32") if self._img.dtype == np.uint32 else self._img.astype("int32")
        return self._img.view("int64")  if self._img.dtype == np.uint64 else self._img.astype("int64")

    # ImageProperties
    
    @property
    def img_props(self) -> ImageProperties:
        """ Returns the image properties (e.g. median, mean or maximum) """
        return self.img_view(ImageView.DEFAULT).image_props
    
    @property
    def img_diff_props(self) -> ImageProperties:
        """ Returns the diff image properties (e.g. median, mean or maximum) """
        return self.img_diff_view(ImageView.DEFAULT).image_props
    
    def img_frame_props(self, frame:int) -> ImageProperties:
        """ Returns the image properties for a given frame """
        # Edge case, do not use caching
        if self.img is None or frame < 0 or frame >= self.img.shape[0]:
            return ImageProperties(None)
        return ImageProperties(self.img[frame])
    
    def img_diff_frame_props(self, frame:int) -> ImageProperties:
        """ Returns the image diff properties for a given frame """
        # Edge case, do not use caching
        if self.img_diff is None or frame < 0 or frame >= self.img_diff.shape[0]:
            return ImageProperties(None)
        return ImageProperties(self.img_diff[frame])
    
    # Image View

    def img_view(self, mode: "ImageView", fn_list: list[tuple[str, Callable[[AxisImage], AxisImage], bool, FunctionType|int]]|Literal["default"]|None = None, cache: bool = True) -> AxisImage:
        """ Returns a view of the current image given an ImageView mode """
        if ImageView.DEFAULT not in self._img_views:
            self._img_views["default"][ImageView.DEFAULT] = AxisImage(self.img_raw, axis=ImageView.DEFAULT.value, name=f"{self.name}-img")

        if fn_list is None:
            fn_list = self._img_functions
        elif fn_list == "default":
            fn_list = []
        id = self.get_functions_identifier(fn_list)

        if id not in self._img_views.keys():
            logger.debug(f"Calculating img function for identifier '{id}' on '{self.name}'")
            fn_img = self._img_views["default"][ImageView.DEFAULT]
            for i, (name, fn, cache_fn, priority) in enumerate(fn_list):
                fn_id = self.get_functions_identifier(fn_list[:i+1])
                fn_hash = "@" + fn_id.split("@")[1] if "@" in fn_id else ""
                fn_img = fn(fn_img)
                fn_img._name = f"{self.name}-{name}{fn_hash}-img"

                if cache_fn and fn_id not in self._img_views:
                    self._img_views[fn_id] = {ImageView.DEFAULT: fn_img}

            if cache:
                self._img_views[id] = {ImageView.DEFAULT: fn_img}
        else:
            fn_img = self._img_views[id][ImageView.DEFAULT]

        if mode not in self._img_views[id].keys():
            axis_image = AxisImage(fn_img.image, axis=mode.value, name=fn_img._name)
            if cache:
                self._img_views[id][mode] = axis_image
        else:
            axis_image = self._img_views[id][mode]

        self.clear_cache()
        
        return axis_image
        
    
    def img_diff_view(self, mode: "ImageView", fn_list: list[tuple[str, Callable[[AxisImage, AxisImage], AxisImage], bool, FunctionType|int]]|Literal["default"]|None = None, cache: bool = True) -> AxisImage:
        """ Returns a view of the current image given an ImageView mode """
        if ImageView.DEFAULT not in self._img_diff_views:
            self._img_diff_views["default"][ImageView.DEFAULT] = AxisImage(self.img_diff_raw, axis=ImageView.DEFAULT.value, name=f"{self.name}-img_diff")

        if fn_list is None:
            fn_list = self._img_diff_functions
        elif fn_list == "default":
            fn_list = []
        id = self.get_functions_identifier(fn_list)

        if id not in self._img_diff_views.keys():
            logger.debug(f"Calculating img_diff function for identifier '{id}' on '{self.name}'")
            fn_img = self._img_diff_views["default"][ImageView.DEFAULT]
            img = self.img_view(ImageView.DEFAULT, "default")
            for i, (name, fn, cache_fn, priority) in enumerate(fn_list):
                fn_id = self.get_functions_identifier(fn_list[:i+1])
                fn_hash = "@" + fn_id.split("@")[1] if "@" in fn_id else ""
                fn_img = fn(img, fn_img)
                fn_img._name = f"{self.name}-{name}{fn_hash}-img_diff"

                if cache_fn and fn_id not in self._img_diff_views:
                    self._img_diff_views[fn_id] = {ImageView.DEFAULT: fn_img}

            if cache:
                self._img_diff_views[id] = {ImageView.DEFAULT: fn_img}
        else:
            fn_img = self._img_diff_views[id][ImageView.DEFAULT]

        if mode not in self._img_diff_views[id].keys():
            axis_image = AxisImage(fn_img.image, axis=mode.value, name=fn_img._name)
            if cache:
                self._img_diff_views[id][mode] = axis_image
        else:
            axis_image = self._img_diff_views[id][mode]

        self.clear_cache()
        
        return axis_image
    
    # Signal

    @property
    def signal_obj(self) -> "SignalObject":
        return self._signal_obj
    
    # Convolution functions

    @property
    def img_functions(self) -> list[tuple[str, Callable[[AxisImage], AxisImage], bool, FunctionType|int]]:
        """ 
        Returns the current list of image functions. An image function is intended to modify an image by accepting an AxisImage and returning a new axis image.
        The functions inside the list are called first to last with the result from the predecessor (first with self.img_raw).
        Every list entry must have an name (str), an Callable (AxisImage) -> AxisImage, the cache flag (bool) and priority (int). The priority is used to sort
        the entries and should be set to zero on default
        """
        return self._img_functions

    @property
    def img_diff_functions(self) -> list[tuple[str, Callable[[AxisImage, AxisImage], AxisImage], bool, FunctionType|int]]:
        """ 
        Returns the current list of img_diff functions. An image function is intended to modify an image by accepting the image and image diff as parameters 
        (both as AxisImage) and returning a new axis image.
        The functions inside the list are called first to last with the result from the predecessor (first with self.img_diff_raw).
        Every list entry must have an name (str), an Callable (img AxisImage, img_diff AxisImage) -> AxisImage, the cache flag (bool) and priority (int)
        The priority is used to sort the entries and should be set to zero on default
        """
        return self._img_diff_functions
    
    def invalidate_functions(self) -> None:
        """ This function should be called when changes to the underlying img_functions and img_diff_functions objects were performed """
        self.signal_obj.clear()

    def get_functions_identifier(self, functions: list[tuple[str, Callable[..., AxisImage], bool, FunctionType|int]]) -> str:
        if len(functions) == 0:
            return "default"
        return "-".join([name for name, fn, cache, priority in functions]) + (hex(hash("".join([str(id(fn)) for name, fn, cache, priority in functions]))).replace("0x", "@") if len(functions) > 0 else "")

    def sort_functions(self) -> None:
        self._img_functions.sort(key=lambda v: v[3].value if isinstance(v[3], FunctionType) else v[3], reverse=True)
        self._img_diff_functions.sort(key=lambda v: v[3].value if isinstance(v[3], FunctionType) else v[3], reverse=True)

    def clear_cache(self, full_clear: bool = False) -> None:
        """Clears caches of unsused convolutions """
        gc_count = 0
        fn_id = self.get_functions_identifier(self._img_functions)
        for k in list(self._img_views.keys()):
            if not full_clear and len(self._img_views) <= self.conv_cache_size:
                break
            if k != "default" and k != fn_id:
                del self._img_views[k]
                gc_count += 1

        fn_diff_id = self.get_functions_identifier(self._img_diff_functions)   
        for k in list(self._img_diff_views.keys()):
            if not full_clear and len(self._img_diff_views) <= self.diff_conv_cache_size:
                break
            if k != "default" and k != fn_diff_id:
                del self._img_diff_views[k]
                gc_count += 1

        if gc_count > 0:
            logger.debug(f"Garbage collect {gc_count} convolutions")

    # Image loading
    
    def precompute_image(self, task_continue: bool = False, run_async:bool = True) -> Task:
        """ 
            Precalculate the image views to prevent stuttering during runtime.

            :param bool task_continue: This function supports the continuation of an existing task (for example from opening an image file)
            :param bool async_mode: Controls if the precomputation runs in a different thread. Has no effect when task_continue is set
            :returns Task: The task object of this task
            :raises AlreadyLoading: There is already a task working on this ImageObject
        """
        if not task_continue and self._task_open_image.running:
            raise AlreadyLoadingError()

        def _precompute(task: Task):
            t0 = time.perf_counter()
            _progIni = task._step if task._step is not None else 0
            task.set_step_progress(_progIni, "preparing ImgView (Spatial Mean)")
            self.img_view(ImageView.SPATIAL).mean_image
            task.set_step_progress(_progIni, "preparing ImgView (Spatial Std)")
            self.img_view(ImageView.SPATIAL).std_image
            gc.collect()
            task.set_step_progress(1+_progIni, "preparing delta video")
            self.img_diff
            gc.collect()
            task.set_step_progress(2+_progIni, "preparing ImgDiffView (Spatial Max)")
            self.img_diff_view(ImageView.SPATIAL).max_image
            task.set_step_progress(2+_progIni, "preparing ImgDiffView (Spatial Std)")
            self.img_diff_view(ImageView.SPATIAL).std_normed_image
            gc.collect()
            task.set_step_progress(2+_progIni, "preparing ImgDiffView (Temporal Max)")
            self.img_diff_view(ImageView.TEMPORAL).max_image
            task.set_step_progress(2+_progIni, "preparing ImgDiffView (Temporal Std)")
            self.img_diff_view(ImageView.TEMPORAL).std_image
            gc.collect()
            logger.debug(f"Precomputed image '{self.name}' in {(time.perf_counter()-t0):1.3f} s")

        if task_continue:
            _precompute(self._task_open_image)
        else:
            self._task_open_image.reset(function=_precompute, name="preparing ImageObject", run_async=run_async)
            self._task_open_image.set_step_mode(3)
            self._task_open_image.start()
        return self._task_open_image
        
    def set_image_precompute(self, img:np.ndarray, name:str|None = None, name_without_extension: str|None = None, run_async:bool = True) -> Task:
        """ 
            Set a new image with a given name and run precompute_image() on it.

            :param np.ndarray img: The image
            :param str name: Name of the image
            :param bool async_mode: Controls if the precomputation runs in a different thread
            :returns Task: The task object of this task
            :raises AlreadyLoading: There is already a task working on this ImageObject
        """
        if not ImageObject._is_valid_image_stack(img):
            raise UnsupportedImageError()
        self.img = img
        self.name = name
        self.name_without_extension = name_without_extension
        return self.precompute_image(run_async=run_async)


    def open_file(self, path: Path|str, precompute:bool = False, run_async:bool = True) -> Task:
        """ 
            Open an image using a given path.

            :param Path|str path: The path to the image file
            :param bool precompute: Controls if the loaded image is also precomputed
            :param bool run_async: Controls if the precomputation runs in a different thread
            :returns Task: The task object of this task
            :raises AlreadyLoading: There is already a task working on this ImageObject
            :raises FileNotFoundError: Can't find the file
            :raises UnsupportedImageError: The image is unsupported or has an error
            :raises ImageShapeError: The image has an invalid shape
        
        """
        if self._task_open_image.running:
            raise AlreadyLoadingError()
        
        if isinstance(path, str):
            path = Path(path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError()
        
        self.clear()

        def _Load(task: Task):
            t0 = time.perf_counter()
            task.set_step_progress(0, "reading File")
            _metadata = None
            if path.suffix.lower() in [".tif", ".tiff"]:
                logger.debug(f"Opening '{path.name}' with the tifffile lib")
                with tifffile.TiffFile(path) as tif:
                    img = tif.asarray()
                    if tif.shaped_metadata is not None:      
                        if len(tif.shaped_metadata) >= 2:
                            _metadata = {i: d for i, d in enumerate(tif.shaped_metadata)}
                        elif len(tif.shaped_metadata) == 1:
                            _metadata = tif.shaped_metadata[0]
            elif nd2.is_supported_file(path):
                logger.debug(f"Opening '{path.name}' with the nd2 lib")
                with nd2.ND2File(path) as nd2file:
                    img = nd2file.asarray()
                    if isinstance(nd2file.metadata, dict):
                        _metadata = nd2file.metadata
                    else:
                        _metadata = asdict(nd2file.metadata)
            else:
                logger.debug(f"Opening '{path.name}' with PIMS")
                try:
                    _pimsImg = pims.open(str(path))
                except FileNotFoundError:
                    raise FileNotFoundError()
                except Exception as ex:
                    raise UnsupportedImageError(path.name)
                task.set_step_progress(1, "converting")
                imgNP = np.zeros(shape=_pimsImg.shape, dtype=_pimsImg.dtype)
                imgNP = [_pimsImg[i] for i in range(_pimsImg.shape[0])]
                img = np.array(imgNP)
                if getattr(_pimsImg, "get_metadata_raw", None) != None: 
                    _metadata = collections.OrderedDict(sorted(_pimsImg.get_metadata_raw().items()))
            if len(img.shape) not in [3,4]:
                raise ImageShapeError(img.shape)
            if len(img.shape) == 4 and img.shape[3] == 1:
                img = np.squeeze(img, axis=3)
            elif len(img.shape) == 4 and img.shape[3] == 3:
                logger.warning(f"Image '{path.name}' is a colored image, but will be opened as a grey scaled image")
                img = np.dot(img[..., :3], [0.2989, 0.5870, 0.1140]).astype(img.dtype)
            self.img = img
            self._metadata = _metadata
            self._path = path
            self.name = path.name
            self.name_without_extension = path.stem

            t1 = time.perf_counter()
            logger.debug(f"Read file '{path.name}' in {(t1-t0):1.3f} s")
            
            if precompute:
                self.precompute_image(task_continue=True, run_async=run_async)

        self._task_open_image.reset(function=_Load, name="open image file", run_async=run_async)
        self._task_open_image.set_step_mode(2 + 4*precompute)
        self._task_open_image.start()
        return self._task_open_image
    
    def export_img(self, path: Path) -> None:
        """ Export the current img """
        if self.img is None:
            raise NoImageError()
        match path.suffix.lower():
            case ".tif"|".tiff":
                tifffile.imwrite(path, data=self.img, metadata=self.metadata, compression="zlib")
            case _:
                raise UnsupportedExtensionError(f"The extension '{path.suffix}' is not supported for exporting")
        logger.info(f"Exported the video as '{path.name}'")

    def export_img_diff(self, path: Path) -> None:
        """ Export the current img_diff"""    
        if self.img_diff is None:
            raise NoImageError()
        match path.suffix.lower():
            case ".tif"|".tiff":
                tifffile.imwrite(path, data=self.img_diff, metadata=self.metadata, compression="zlib")
            case _:
                raise UnsupportedExtensionError(f"The extension '{path.suffix}' is not supported for exporting")
        logger.info(f"Exported the delta video as '{path.name}'")
    
    # Static functions

    @staticmethod
    def _is_valid_image_stack(image: Any) -> bool:
        if not isinstance(image, np.ndarray):
            return False
        if len(image.shape) != 3:
            return False
        return True
    
class ImageView(Enum):
    """ 
        Collapse a 3D image (t, y, x) into a smaller dimension
    """

    DEFAULT = (0,1,2)
    """ DEFAULT: Returns the original 3D image """

    SPATIAL = (0,)
    """ SPATIAL: Removes the temporal component and creates a 2D image """
    TEMPORAL = (1,2)
    """ TEMPORAL: Removes the spatial component and creates an 1D time series """

class ImageObjectError(Exception):
    """ ImageObject Error"""
    pass

class NoImageError(ImageObjectError):
    """ There is no img or img_diff loaded"""
    pass

class UnsupportedExtensionError(ImageObjectError):
    """ Raised when the extension of the image is not supported"""

class AlreadyLoadingError(ImageObjectError):
    """ Already loading an Image into an ImageObject"""
    pass

class UnsupportedImageError(ImageObjectError):
    """ The image is unsupported """
    
    def __init__(self, msg: str|None = None, file_name: str|None = None, exception: Exception|None = None, *args):
        super().__init__(*args)
        self.msg = msg
        self.exception = exception
        self.file_name = file_name

class ImageShapeError(ImageObjectError):
    """ The image has an invalid shape """

    def __init__(self, shape: tuple|None = None, *args):
        super().__init__(*args)
        self.shape = shape


