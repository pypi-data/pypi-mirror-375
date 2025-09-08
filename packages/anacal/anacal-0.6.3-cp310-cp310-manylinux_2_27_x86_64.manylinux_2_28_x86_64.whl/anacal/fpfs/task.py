# Image Tasks of Shapelet Based Measurements
#
# python lib
import numpy as np
import numpy.lib.recfunctions as rfn
from numpy.typing import NDArray
from pydantic import BaseModel, Field

from . import FpfsImage, measure_fpfs
from . import BasePsf
from .base import FpfsKernel


npix_patch = 256
npix_overlap = 64
npix_default = 64


class FpfsTask(FpfsKernel):
    """A base class for measurement

    Args:
    npix (int): number of pixels in a postage stamp
    pixel_scale (float): pixel scale in arcsec
    sigma_arcsec (float): Shapelet kernel size
    noise_variance (float): variance of image noise
    kmax (float | None): maximum k
    psf_array (ndarray): an average PSF image [default: None]
    kmax_thres (float): the tuncation threshold on Gaussian [default: 1e-20]
    do_detection (bool): whether compute detection kernels
    bound (int): minimum distance to boundary [default: 0]
    verbose (bool): whether display INFO
    """

    def __init__(
        self,
        *,
        npix: int,
        pixel_scale: float,
        sigma_arcsec: float,
        noise_variance: float = -1,
        kmax: float | None = None,
        psf_array: NDArray | None = None,
        kmax_thres: float = 1e-20,
        do_detection: bool = True,
        bound: int = 0,
        verbose: bool = False,
    ) -> None:
        super().__init__(
            npix=npix,
            pixel_scale=pixel_scale,
            sigma_arcsec=sigma_arcsec,
            kmax=kmax,
            psf_array=psf_array,
            kmax_thres=kmax_thres,
            do_detection=do_detection,
            verbose=verbose,
        )
        klim = 1e10 if self.kmax is None else (self.kmax / self.pixel_scale)
        self.prepare_fpfs_bases()
        self.mtask = FpfsImage(
            nx=self.npix,
            ny=self.npix,
            scale=self.pixel_scale,
            sigma_arcsec=self.sigma_arcsec,
            klim=klim,
            psf_array=self.psf_array,
            use_estimate=True,
        )

        if self.do_detection:
            self.dtask = FpfsImage(
                nx=npix_patch,
                ny=npix_patch,
                scale=self.pixel_scale,
                sigma_arcsec=self.sigma_arcsec,
                klim=klim,
                psf_array=self.psf_array,
                use_estimate=True,
                npix_overlap=npix_overlap,
                bound=bound,
            )
            if not noise_variance > 0:
                raise ValueError("Noise variance should be positive")
            self.prepare_covariance(variance=noise_variance)
        else:
            self.dtask = None

        return

    def detect(
        self,
        *,
        gal_array: NDArray,
        fthres: float,
        pthres: float,
        omega_v: float,
        v_min: float,
        noise_array: NDArray | None = None,
        mask_array: NDArray | None = None,
        star_cat: NDArray | None = None,
    ) -> NDArray:
        """This function detects galaxy from image

        Args:
        gal_array (NDArray): galaxy image data
        fthres (float): flux threshold
        pthres (float): peak threshold
        omega_v (float): smoothness parameter for pixel difference
        noise_array (NDArray|None): pure noise image
        mask_array (NDArray|None): mask image
        star_cat (NDArray|None): bright star catalog

        Returns:
        (NDArray): galaxy detection catalog
        """
        assert self.dtask is not None
        return self.dtask.detect_source(
            gal_array=gal_array,
            fthres=fthres,
            pthres=pthres,
            std_m00=self.std_m00 * self.pixel_scale**2.0,
            omega_v=omega_v * self.pixel_scale**2.0,
            v_min=v_min * self.pixel_scale**2.0,
            noise_array=noise_array,
            mask_array=mask_array,
        )

    def run_psf_array(
        self,
        *,
        gal_array: NDArray,
        psf_array: NDArray,
        det: NDArray | None = None,
        noise_array: NDArray | None = None,
    ) -> tuple[NDArray, NDArray | None]:
        """This function measure galaxy shapes at the position of the detection
        using PSF image data

        Args:
        gal_array (NDArray): galaxy image data
        psf_array (NDArray): psf image data
        det (list|None): detection catalog
        noise_array (NDArray | None): noise image data [default: None]

        Returns:
        src_g (NDArray): source measurement catalog
        src_n (NDArray): noise measurement catalog
        """
        # self.logger.warning("Input PSF is array")
        src_g = self.mtask.measure_source(
            gal_array=gal_array,
            filter_image=self.bfunc_use,
            psf_array=psf_array,
            det=det,
            do_rotate=False,
        )
        if noise_array is not None:
            src_n = self.mtask.measure_source(
                gal_array=noise_array,
                filter_image=self.bfunc_use,
                psf_array=psf_array,
                det=det,
                do_rotate=True,
            )
            src_g = src_g + src_n
        else:
            src_n = None
        return src_g, src_n

    def run_psf_python(
        self,
        gal_array: NDArray,
        psf_obj: BasePsf,
        det: NDArray,
        noise_array: NDArray | None = None,
    ) -> tuple[NDArray, NDArray | None]:
        """This function measure galaxy shapes at the position of the detection
        using PSF image data

        Args:
        gal_array (NDArray): galaxy image data
        psf_obj (BasePsf): PSF object in python
        noise_array (NDArray | None): noise image data [default: None]
        det (list|None): detection catalog

        Returns:
        src_g (NDArray): source measurement catalog
        src_n (NDArray): noise measurement catalog
        """
        # self.logger.warning("Input PSF is python object")
        det_dtype = det.dtype
        src_g = []
        src_n = []
        for _d in det:
            this_psf_array = psf_obj.draw(x=_d["x"], y=_d["y"])
            # TODO: remove det_array
            det_array = np.array([_d], dtype=det_dtype)
            srow = self.mtask.measure_source(
                gal_array=gal_array,
                filter_image=self.bfunc_use,
                psf_array=this_psf_array,
                det=det_array,
                do_rotate=False,
            )[0]
            if noise_array is not None:
                nrow = self.mtask.measure_source(
                    gal_array=noise_array,
                    filter_image=self.bfunc_use,
                    psf_array=this_psf_array,
                    det=det_array,
                    do_rotate=True,
                )[0]
                srow = srow + nrow
                src_n.append(nrow)
            src_g.append(srow)
        if len(src_n) == 0:
            src_n = None
        else:
            assert len(src_n) == len(src_g)
            src_n = np.array(src_n)
        src_g = np.array(src_g)
        return src_g, src_n


    def run(
        self,
        gal_array: NDArray,
        psf: BasePsf | NDArray,
        det: NDArray | None = None,
        noise_array: NDArray | None = None,
    ):
        """This function measure galaxy shapes at the position of the detection

        Args:
        gal_array (NDArray): galaxy image data
        det (NDArray): detection catalog
        psf (BasePsf | NDArray): psf image data or psf model
        noise_array (NDArray | None): noise image data [default: None]

        Returns:
        (NDArray): galaxy measurement catalog
        """
        if isinstance(psf, np.ndarray):
            src_g, src_n = self.run_psf_array(
                gal_array=gal_array,
                psf_array=psf,
                noise_array=noise_array,
                det=det,
            )
        elif isinstance(psf, BasePsf):
            assert det is not None
            # For the case PSF is a Python object
            src_g, src_n = self.run_psf_python(
                gal_array=gal_array,
                psf_obj=psf,
                noise_array=noise_array,
                det=det,
            )
        else:
            raise RuntimeError("psf does not have a correct type")
        src_g = rfn.unstructured_to_structured(
            arr=src_g,
            dtype=self.dtype,
        )
        if src_n is not None:
            src_n = rfn.unstructured_to_structured(arr=src_n, dtype=self.dtype)

        return {
            "data": src_g,
            "noise": src_n,
        }


class FpfsConfig(BaseModel):
    npix: int = Field(
        default=64,
        description="""size of the stamp before Fourier Transform
        """,
    )
    kmax_thres: float = Field(
        default=1e-12,
        description="""The threshold used to define the upper limit of k we use
        in Fourier space.
        """,
    )
    bound: int = Field(
        default=35,
        description="""Boundary buffer length, the sources in the buffer reion
        are not counted.
        """,
    )
    sigma_arcsec: float = Field(
        default=0.52,
        description="""Smoothing scale of the shapelet and detection kernel.
        """,
    )
    sigma_arcsec1: float = Field(
        default=-1,
        description="""Smoothing scale of the second shapelet kernel.
        """,
    )
    sigma_arcsec2: float = Field(
        default=-1,
        description="""Smoothing scale of the third shapelet kernel.
        """,
    )
    pthres: float = Field(
        default=0.12,
        description="""Detection threshold (peak identification) for the
        pooling.
        """,
    )
    fthres: float = Field(
        default=8.0,
        description="""Detection threshold (minimum signal-to-noise ratio) for
        the first pooling.
        """,
    )
    omega_r2: float = Field(
        default=4.8,
        description="""
        smoothness parameter for r2 cut
        """,
    )
    r2_min: float = Field(
        default=0.1,
        description="""Minimum trace moment matrix
        """,
    )
    omega_v: float = Field(
        default=0.9,
        description="""
        smoothness parameter for v cut
        """,
    )
    v_min: float = Field(
        default=0.45,
        description="""Minimum of v
        """,
    )
    snr_min: float = Field(
        default=12,
        description="""Minimum Signal-to-Noise Ratio for detection.
        """,
    )
    c0: float = Field(
        default=8.4,
        description="""Weighting parameter for m00 for ellipticity definition.
        """,
    )


def process_image(
    *,
    fpfs_config: FpfsConfig,
    pixel_scale: float,
    noise_variance: float,
    mag_zero: float,
    gal_array: NDArray,
    psf_array: NDArray,
    noise_array: NDArray | None = None,
    mask_array: NDArray | None = None,
    star_catalog: NDArray | None = None,
    detection: NDArray | None = None,
    psf_object: BasePsf | None = None,
    do_compute_detect_weight: bool = True,
    only_return_detection_modes: bool = False,
    base_column_name: str | None = None,
):
    """Run measurement algorithms on the input exposure, and optionally
    populate the resulting catalog with extra information.

    Args:
    fpfs_config (FpfsConfig):  configuration object
    pixel_scale (float): pixel scale in arcsec
    noise_variance (float): variance of image noise
    mag_zero (float): magnitude zero point
    do_detection (bool): whether compute detection kernel
    gal_array (NDArray[float64]): galaxy exposure array
    psf_array (ndarray): an average PSF image
    noise_array (NDArray | None): pure noise array
    mask_array (NDArray | None): mask array (1 for masked)
    star_catalog (NDArray | None): bright star catalog
    detection (NDArray | None): detection catalog
    psf_object (BasePsf | None): PSF object
    do_compute_detect_weight (bool): whether to compute detection weight
    only_return_detection_modes (bool): only return linear modes for detection
    base_column_name (str | None): base column name

    Returns:
    (NDArray) FPFS catalog
    """
    if only_return_detection_modes:
        assert do_compute_detect_weight

    ratio = 1.0 / (10 ** ((30 - mag_zero) / 2.5))
    r2_min = fpfs_config.r2_min * ratio
    omega_r2 = fpfs_config.omega_r2 * ratio
    v_min = fpfs_config.v_min * ratio
    omega_v = fpfs_config.omega_v * ratio
    fpfs_c0 = fpfs_config.c0 * ratio

    if psf_object is None:
        psf_object = psf_array

    out_list = []

    if do_compute_detect_weight or (detection is None):
        ftask = FpfsTask(
            npix=fpfs_config.npix,
            pixel_scale=pixel_scale,
            sigma_arcsec=fpfs_config.sigma_arcsec,
            noise_variance=noise_variance,
            psf_array=psf_array,
            kmax_thres=fpfs_config.kmax_thres,
            do_detection=True,
            bound=fpfs_config.bound,
        )
        std_m00 = ftask.std_m00
        m00_min = fpfs_config.snr_min * std_m00
        if detection is None:
            detection = ftask.detect(
                gal_array=gal_array,
                fthres=fpfs_config.fthres,
                pthres=fpfs_config.pthres,
                noise_array=noise_array,
                v_min=v_min,
                omega_v=omega_v,
                mask_array=mask_array,
                star_cat=star_catalog,
            )
        else:
            colnames = ("y", "x")
            if detection.dtype.names != colnames:
                raise ValueError("detection has wrong cloumn names")
        out_list.append(detection)

        if do_compute_detect_weight:
            src = ftask.run(
                gal_array=gal_array,
                psf=psf_object,
                det=detection,
                noise_array=noise_array,
            )
            if only_return_detection_modes:
                return src
            meas = measure_fpfs(
                C0=fpfs_c0,
                v_min=v_min,
                omega_v=omega_v,
                pthres=fpfs_config.pthres,
                m00_min=m00_min,
                std_m00=std_m00,
                r2_min=r2_min,
                omega_r2=omega_r2,
                x_array=src["data"],
                y_array=src["noise"],
            )
            del src
            map_dict = {name: "fpfs_" + name for name in meas.dtype.names}
            out_list.append(rfn.rename_fields(meas, map_dict))

        del ftask

    if fpfs_config.sigma_arcsec1 > 0:
        ftask = FpfsTask(
            npix=fpfs_config.npix,
            pixel_scale=pixel_scale,
            sigma_arcsec=fpfs_config.sigma_arcsec1,
            psf_array=psf_array,
            kmax_thres=fpfs_config.kmax_thres,
            do_detection=False,
        )
        src = ftask.run(
            gal_array=gal_array,
            psf=psf_object,
            det=detection,
            noise_array=noise_array,
        )
        meas1 = measure_fpfs(
            C0=fpfs_c0,
            x_array=src["data"],
            y_array=src["noise"],
        )
        del src, ftask
        map_dict = {name: "fpfs1_" + name for name in meas1.dtype.names}
        out_list.append(rfn.rename_fields(meas1, map_dict))
        del meas1

    if fpfs_config.sigma_arcsec2 > 0:
        ftask = FpfsTask(
            npix=fpfs_config.npix,
            pixel_scale=pixel_scale,
            sigma_arcsec=fpfs_config.sigma_arcsec2,
            psf_array=psf_array,
            kmax_thres=fpfs_config.kmax_thres,
            do_detection=False,
        )
        src = ftask.run(
            gal_array=gal_array,
            psf=psf_object,
            det=detection,
            noise_array=noise_array,
        )
        meas2 = measure_fpfs(
            C0=fpfs_c0,
            x_array=src["data"],
            y_array=src["noise"],
        )
        del src, ftask
        map_dict = {name: "fpfs2_" + name for name in meas2.dtype.names}
        out_list.append(rfn.rename_fields(meas2, map_dict))
        del meas2

    result = rfn.merge_arrays(
        out_list,
        flatten=True,
        usemask=False,
    )
    if base_column_name is not None:
        assert result.dtype.names is not None
        map_dict = {
            name: base_column_name + name for name in result.dtype.names
        }
        result = rfn.rename_fields(result, map_dict)

    return result
