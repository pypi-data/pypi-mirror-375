# spectroflat
`spectroflat` is a Python based library to flat field spatially resolved spectro-polarimetric data.
It allows for flat-field calibration data to be to obtained for diffraction-grating-based, long-slit
solar spectrographs combined with temporally modulated polarimetry from high-resolution solar telescopes. 
This approach is based on nominal flat-fielding procedures performed during the instrument’s science operations.

The Python library can be plugged into existing Python-based data reduction pipelines or used as
a standalone calibration tool. Our results demonstrate a suppression of fringes, sensor artifacts, 
and fixed-pattern imprints in demodulated data by one order of magnitude. 
For intensity images, the photon noise level can be closely attained after calibration.
The data calibrated with the `spectroflat` method offer robust and precise inversion results and allow 
for spectral image reconstruction.

This library is intended to be an extension of the
"[Precise reduction of solar spectra obtained with large CCD arrays](https://www.aanda.org/articles/aa/pdf/2002/42/aa2154.pdf)"
method, presented by Wöhl et al. (2002), to spectro-polarimetric instruments covering a large spectral field of view with many lines.

## Citation
When using this library to reduce your data, please cite:
Hoelken et al. "Spectroflat: A generic spectrum and flat-field calibration library for spectro-polarimetric data"
([DOI: 10.1051/0004-6361/202348877](https://doi.org/10.1051/0004-6361/202348877),
[NASA ADS](https://ui.adsabs.harvard.edu/abs/2024A%26A...687A..22H/abstract))

## Versioning
We follow the [Semantic Versioning](https://semver.org/) pattern. In short semantic versioning boils down to:
- PATCH 0.0.x level changes for implementation level detail changes, such as small bug fixes
- MINOR 0.x.0 level changes for any backwards compatible API changes, such as new functionality/features
- MAJOR x.0.0 level changes for backwards incompatible API and algorithm changes, such as changes that will 
   break existing users code if they update and or change the outcome of the code notably.

### Original algorithm
The spectroflat algorithm `1.X.X` is described and evaluated in 
Hölken et al. (2023) "Spectroflat: A generic calibration library for spectro-polarimetric data". [see above]

### Changes in `2.X.X`:
The smile extraction can now be done iteratively (`default=2`, use `Config.iterations` to adjust).
Usually, the residual offset correction is below 0.1 px in the second iteration.   
Consequently, we removed the dust flat iteration, as now the first extraction yields correct results.

- [**Braking change**] The property `pre_flat` of the `Analyzer` now exclusively holds the actual pre flat from the preparation step.
  The dust flat is now stored in the  `dust_flat`property.
- [*Deprecation*] The property `gain_table` of the `Analyzer` class is now deprecated and replaced by `illumination_pattern`.


# In a nutshell
A working usage example is provided in the [`example.py`](example.py). 
All available configuration keywords (and their effects) are documented 
[here](https://hoelken.pages.gwdg.de/spectroflat/doc/spectroflat/base/config.html).

Below we briefly introduce the core input and output data of the library.

## Input data 
The input data must be calibrated for the camera zero-input response (dark current and bias level) and 
relevant non-linearity effects. If each modulation state is to be corrected with its own set of calibration data 
an average of all frames from the flat field recording belonging to each modulation state has to be provided. 

Input data shall be provided as a `numpy` Array with dimensions modulation state, spatial location 
along the spectrograph slit and wavelength position. 

## Extracted Data
After the successful execution of the `Analyzer` the following results are available.

### Pre-Flat
```python
analyzer.pre_flat
```

The pre-flat is generated in the preparation step from fitting a polynomial along every column of the input data.
It is a preliminary version of the dust flat (see below).

### Dust-Flat
```python
analyzer.dust_flat
```

The dust-flat is a combination of the sensor and slit flat that 
contains most of the "hard" flat field features.
Most prominently the following is corrected:
- Sensor features (e.g. column-to-column response patterns, dust on the sensor itself)
- Slit features (e.g. dust on the slit resulting in line features in the spectral direction)
- Fixed optical fringes and illumination impurities.

The dust flat might be split in Sensor Flat and Slit Flat by the mean profile method applied along 
the spectrograph slit dimension. 

`spectroflat` provides a utility function separate the sensor- and slit-flat parts in the dust flat:
`spectroflat.utils.ffing.split_sensor_slit_flat`. 
It takes the dust-flat and the corrected rotation. The rotation value can either be taken from the header 
of the offset map or the configuration. 

### Smile offset map
```python
analyzer.offset_map
```

spectroflat characterizes the smile distortion by tracking the change of every spectral absorption or emission 
line with respect to the reference profile generated from the central rows. The map list the offset each pixel 
has, compared to that reference, with sub-pixel precision.  

### Illumination pattern
```python
analyzer.illumination_pattern
```

Typically, the illumination patterns are in the 10−6 range and are not used.  
This result is kept for compatibility with the approach of Wöhl et al. (2002).

### PDF Report
A report summary with relevant plots to inspect the quality of the extracted products. 

## Technical Documentation

**NOTE** This library expects the spacial domain on the vertical-axis and
the spectral domain on the horizontal axis. 
spectroflat does not include any file reading/writing routines and expects `numpy` arrays as input. 

Please refer to ([Hoelken et al. (2024)](https://doi.org/10.1051/0004-6361/202348877) for a deeper introduction 
and scientific evaluation of the library. 
Refer to the  [API Documentation](https://hoelken.pages.gwdg.de/spectroflat/doc/spectroflat/) for 
implementation details. 
Especially the entries on available 
[Configuration](https://hoelken.pages.gwdg.de/spectroflat/doc/spectroflat/base/config.html) values 
are of general interest. 

The [`example.py`](example.py) script provides a usage example. 
However, running the library as such is relatively straight forward. 
The delicate part is to determine the best set of configuration values, 
as quite some knowledge on the instrument and targeted science case is needed.
If you need help getting started, feel free to contact the maintainer(s) [see below] directly.

## Contact
This code is developed and maintained at the Max Planck Institute for 
Solar System Research (MPS) Göttingen.

### Maintainer 
- Johannes Hoelken ([hoelken@mps.mpg.de](mailto:hoelken@mps.mpg.de))

### Contributing 
Any contribution that follows our [Code of Conduct](CODE_OF_CONDUCT.md) and that helps to advance the `spectroflat`
library is highly welcome.

**Bug reports & feature requests** are welcome via gitlab issues or email. 
Issues can either be opened via the web interface (needs access to the gitlab.gwdg.de), 
send to the gitlab project via email gitlab+hoelken-spectroflat-26032-8c4m26ry9b7ughm5m0lp3xyvk-issue@gwdg.de, 
or send to the maintainers email address(es) directly. 

To ease bug fixing please provide a reproducible description and/or relevant testing data in bug reports.
If provided data needs to be handled confidentially, please email the maintainer(s) directly.

**Code contributions** are welcome as merge or pull requests and will undergo a code review.
Any provided code must satisfy the python code style (i.e., the `stylecheck.bash` needs to pass) and 
have at least 80 % test coverage.
Development forks of the repository are explicitly recommended.

Your **working examples** are also highly welcome, if you are willing and allowed to share them.  
For the future we want to build an example library with instrument description and a corresponding working configuration. 
Please use the [template](examples/0_TEMPLATE.md) for a contribution. 

### Contributions
- Alex Feller
- Francisco Iglesias

## License
BSD clause-2, see [LICENSE](LICENSE)