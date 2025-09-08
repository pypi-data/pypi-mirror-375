__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import json
import logging
import math
import re
from typing import Union

import numpy as np
import yaml

from padocc.core import FalseLogger, ProjectOperation
from padocc.core.errors import ConcatFatalError
from padocc.core.filehandlers import JSONFileHandler
from padocc.core.utils import timestamp

from .compute import ComputeOperation, KerchunkDS, ZarrDS


def _format_float(value: float, logger: logging.Logger = FalseLogger()) -> str:
    """
    Format byte-value with proper units.
    """

    logger.debug(f'Formatting value {value} in bytes')
    if value is not None:
        unit_index = 0
        units = ['','K','M','G','T','P']
        while value > 1000:
            value = value / 1000
            unit_index += 1
        return f'{value:.2f} {units[unit_index]}B'
    else:
        return None
    
def _safe_format(value: int, fstring: str) -> str:
    """Attempt to format a string given some fstring template.
    - Handles issues by returning '', usually when value is None initially."""
    try:
        return fstring.format(value=value)
    except AttributeError:
        return ''
    
def _get_seconds(time_allowed: str) -> int:
    """Convert time in MM:SS to seconds"""
    if not time_allowed:
        return 10000000000
    mins, secs = time_allowed.split(':')
    return int(secs) + 60*int(mins)

def _format_seconds(seconds: int) -> str:
    """Convert time in seconds to MM:SS"""
    mins = int(seconds/60) + 1
    if mins < 10:
        mins = f'0{mins}'
    return f'{mins}:00'

def _perform_safe_calculations(std_vars: list, cpf: list, volms: list, nfiles: int, logger: logging.Logger = FalseLogger()) -> tuple:
    """
    Perform all calculations safely to mitigate errors that arise during data collation.

    :param std_vars:        (list) A list of the variables collected, which should be the same across
                            all input files.

    :param cpf:             (list) The chunks per file recorded for each input file.

    :param volms:           (list) The total data size recorded for each input file.

    :param nfiles:          (int) The total number of files for this dataset

    :param logger:          (obj) Logging object for info/debug/error messages.

    :returns:   Average values of: chunks per file (cpf), number of variables (num_vars), chunk size (avg_chunk),
                spatial resolution of each chunk assuming 2:1 ratio lat/lon (spatial_res), totals of NetCDF and Kerchunk estimate
                data amounts, number of files, total number of chunks and the addition percentage.
    """
    kchunk_const = 167 # Bytes per Kerchunk ref (standard/typical)
    if std_vars:
        num_vars = len(std_vars)
    else:
        num_vars = None
    if not len(cpf) == 0:
        avg_cpf = sum(cpf)/len(cpf)
    else:
        logger.warning('CPF set as none, len cpf is zero')
        avg_cpf = None
    if not len(volms) == 0:
        avg_vol = sum(volms)/len(volms)
    else:
        logger.warning('Volume set as none, len volumes is zero')
        avg_vol = None
    if avg_cpf:
        avg_chunk = avg_vol/avg_cpf
    else:
        avg_chunk = None
        logger.warning('Average chunks is none since CPF is none')
    if num_vars and avg_cpf:
        spatial_res = 180*math.sqrt(2*num_vars/avg_cpf)
    else:
        spatial_res = None

    if nfiles and avg_vol:
        source_data = avg_vol*nfiles
    else:
        source_data = None

    if nfiles and avg_cpf:
        total_chunks = avg_cpf * nfiles
    else:
        total_chunks = None

    if avg_chunk:
        addition = kchunk_const*100/avg_chunk
    else:
        addition = None

    type = 'json'
    if avg_cpf and nfiles:
        cloud_data = avg_cpf * nfiles * kchunk_const
        if cloud_data > 500e6:
            type = 'parq'
    else:
        cloud_data = None

    return avg_cpf, num_vars, avg_chunk, spatial_res, source_data, cloud_data, total_chunks, addition, type

class ScanOperation(ProjectOperation):

    def __init__(
            self, 
            proj_code : str, 
            workdir   : str,
            groupID   : str = None, 
            label     : str = 'scan',
            parallel  : bool = False,
            **kwargs,
        ) -> None:

        self.phase = 'scan'
        if label is None:
            label = 'scan-operation'

        super().__init__(
            proj_code, workdir, groupID=groupID, label=label,**kwargs)
        
        if parallel:
            self.update_status(self.phase, 'Pending',jobid=self._logid)

    def help(self, fn=print):
        super().help(fn=fn)
        fn('')
        fn('Scan Options:')
        fn(' > project.run() - Run a scan for this project')

    def _run(
            self, 
            mode: str = 'kerchunk', 
            ctype: Union[str,None] = None,
            mem_allowed: str = '100MB',
            **kwargs
        ) -> None:
        """Main process handler for scanning phase"""

        self.set_last_run(self.phase, timestamp())
        self.logger.info(f'Starting scan-{mode} operation for {self.proj_code}')

        nfiles = len(self.allfiles)

        if nfiles < 3:
            self.detail_cfg.set({'skipped':True})
            self.logger.info(f'Skip scanning phase (only found {nfiles} files) >> proceed directly to compute')
            self.update_status('scan','Success',jobid=self._logid)
            return
        

        # Create all files in mini-kerchunk set here. Then try an assessment.
        limiter = min(100, max(2, int(nfiles/20)))

        self.logger.info(f'Determined {limiter} files to scan (out of {nfiles})')
        self.logger.info(f'Performing CFA Base Scan (Standard)')
        self._scan_cfa(limiter=limiter)

        if mode == 'zarr':
            self.logger.debug('Performing Zarr Scan')
            self._scan_zarr(limiter=limiter, mem_allowed=mem_allowed)
        elif mode == 'kerchunk':
            self.logger.debug('Performing Kerchunk Scan')
            self._scan_kerchunk(limiter=limiter, ctype=ctype)
        elif mode == 'CFA':
            # CFA is always performed.
            pass
        else:
            self.update_status('scan','ValueError',jobid=self._logid)
            raise ValueError(
                f'Unrecognised mode: {mode} - must be one of ["kerchunk","zarr","CFA"]'
            )

        self.update_status('scan','Success',jobid=self._logid)
        return 'Success'

    def _scan_kerchunk(self, limiter: Union[int,None] = None, ctype: Union[str,None] = None):
        """
        Function to perform scanning with output Kerchunk format.
        """
        self.logger.info('Starting scan process for Kerchunk cloud format')

        if self._thorough:
            self.padocc_aggregation = True

        # Redo this processor call.
        mini_ds = KerchunkDS(
            self.proj_code,
            workdir=self.workdir, 
            groupID=self.groupID,
            thorough=self._thorough, 
            forceful=self._forceful, # Always run from scratch forcefully to get best time estimates.
            logger=self.logger,
            limiter=limiter,
            is_trial=True,
            xarray_kwargs=self._xarray_kwargs)
        
        # Scan mode always uses MultiZarrToZarr
        # Having to do this in order to test aggregation option.

        # Order subset
        filesubset = mini_ds.order_native_files()
        
        mini_ds.create_refs(ctype=ctype, filesubset=filesubset)

        self.padocc_aggregation = mini_ds.padocc_aggregation
        self.virtualizarr       = mini_ds.virtualizarr

        if mini_ds.extra_properties is not None:
            self.base_cfg['data_properties'].update(mini_ds.extra_properties)
        
        self.detail_cfg['kwargs'] = mini_ds.extra_kwargs
        
        escape, is_varwarn, is_skipwarn = False, False, False
        cpf, volms = [],[]

        std_vars   = None
        std_chunks = None
        ctypes   = mini_ds.ctypes
        
        self.logger.info(f'Summarising scan results for {limiter} files')

        for count in range(limiter):
            try:
                volume, chunks_per_file, varchunks = self._summarise_json(count)
                vars = sorted(list(varchunks.keys()))

                # Keeping the below options although may be redundant as have already processed the files
                if not std_vars:
                    std_vars = vars
                if vars != std_vars:
                    self.logger.warning(f'Variables differ between files - {vars} vs {std_vars}')
                    is_varwarn = True

                if not std_chunks:
                    std_chunks = varchunks
                for var in std_vars:
                    if std_chunks[var] != varchunks[var]:
                        raise ConcatFatalError(var=var, chunk1=std_chunks[var], chunk2=varchunks[var])

                cpf.append(chunks_per_file)
                volms.append(volume)

                self.logger.info(f'Data recorded for file {count+1}')
            except Exception as err:
                raise err
            
        timings = {
            'convert_time' : mini_ds.convert_time,
            'concat_time'  : mini_ds.concat_time,
            'validate_time': mini_ds.validate_time
        }

        self._compile_outputs(
            std_vars, cpf, volms, timings, 
            ctypes, escape=escape, scanned_with='kerchunk'
        )

    def _scan_cfa(
            self, 
            limiter: Union[int,None] = None,
            is_core: bool = True
        ) -> None:
        """
        Function to perform scanning with output CFA format.
        """

        # Redo this processor call.
        comp = ComputeOperation(
            self.proj_code,
            workdir=self.workdir, 
            thorough=True, 
            forceful=True, # Always run from scratch forcefully to get best time estimates.
            is_trial=True, 
            logger=self.logger,
            groupID=self.groupID, 
            dryrun=self._dryrun,
        )

        status = comp._run(file_limit=limiter)

        if status == 'Success':
            self.logger.info('Determined data properties:')
            self.logger.info(yaml.dump(self.base_cfg['data_properties']))
        else:
            self.logger.info(f' > Result generation failed - {status}')

        # No longer update status message
        #if is_core:
        #    self.update_status('scan','CFA-'+status,jobid=self._logid)
        return status

    def _scan_zarr(
            self, 
            limiter: Union[int,None] = None,
            mem_allowed: str = '100MB'):
        """
        Function to perform scanning with output Zarr format.
        """

        self.logger.info('Starting scan process for Zarr cloud format')

        # Need a refactor
        mini_ds = ZarrDS(
            self.proj_code,
            workdir=self.workdir, 
            thorough=True, 
            forceful=True, # Always run from scratch forcefully to get best time estimates.
            is_trial=True, 
            logger=self.logger,
            groupID=self.groupID, 
            limiter=limiter, 
            dryrun=self._dryrun,
            mem_allowed=mem_allowed)

        mini_ds.create_store()
        
        # Most of the outputs are currently blank as summaries don't really work well for Zarr.

        timings = {
            'convert_time' : mini_ds.convert_time,
            'concat_time'  : mini_ds.concat_time,
            'validate_time': mini_ds.validate_time
        }
        self._compile_outputs(
            mini_ds.std_vars, mini_ds.cpf, mini_ds.volm, timings,
            [], override_type='zarr')

    def _summarise_json(self, identifier) -> tuple:
        """
        Open previously written JSON cached files and perform analysis.
        """

        if isinstance(identifier, dict):
            # Assume refs passed directly.
            kdict = identifier['refs']
        else:

            fh_kwargs = {
                'dryrun':self._dryrun,
                'forceful':self._forceful,
            }

            fh = JSONFileHandler(self.dir, f'cache/{identifier}', logger=self.logger, **fh_kwargs)
            kdict = fh['refs']

            self.logger.debug(f'Starting Analysis of references for {identifier}')

        if not kdict:
            return None, None, None

        # Perform summations, extract chunk attributes
        sizes  = []
        vars   = {}
        chunks = 0

        for chunkkey in kdict.keys():
            if bool(re.search(r'\d', chunkkey)):
                try:
                    sizes.append(int(kdict[chunkkey][2]))
                except ValueError:
                    pass
                chunks += 1
                continue

            if '/.zarray' in chunkkey:
                var = chunkkey.split('/')[0]
                chunksize = 0
                if var not in vars:
                    if isinstance(kdict[chunkkey], str):
                        chunksize = json.loads(kdict[chunkkey])['chunks']
                    else:
                        chunksize = dict(kdict[chunkkey])['chunks']
                    vars[var] = chunksize

        return np.sum(sizes), chunks, vars

    def _compile_outputs(
        self, 
        std_vars: list[str], 
        cpf: list[int], 
        volms: list[str], 
        timings: dict, 
        ctypes: list[str], 
        escape: bool = None, 
        override_type: str = None, 
        scanned_with : str = None
    ) -> None:

        self.logger.info('Summary complete, compiling outputs')
        (avg_cpf, num_vars, avg_chunk, 
        spatial_res, source_data, cloud_data, 
        total_chunks, addition, type) = _perform_safe_calculations(std_vars, cpf, volms, len(self.allfiles), self.logger)

        details = {
            'source_data'      : _format_float(source_data, logger=self.logger), 
            'cloud_data'       : _format_float(cloud_data, logger=self.logger), 
            'scanned_with'     : scanned_with,
            'num_files'        : len(self.allfiles),
            'chunk_info'     : {
                'chunks_per_file'  : _safe_format(avg_cpf,'{value:.1f}'),
                'total_chunks'     : _safe_format(total_chunks,'{value:.2f}'),
                'estm_chunksize'   : _format_float(avg_chunk, logger=self.logger),
                'estm_spatial_res' : _safe_format(spatial_res,'{value:.2f}') + ' deg',
                'addition'         : _safe_format(addition,'{value:.3f}') + ' %',
            },
            'timings'        : {
                'convert_estm'   : timings['convert_time'],
                'concat_estm'    : timings['concat_time'],
                'validate_estm'  : timings['validate_time'],
                'convert_actual' : None,
                'concat_actual'  : None,
                'validate_actual': None,
            }
        }

        if escape:
            details['scan_status'] = 'FAILED'

        details['driver'] = '/'.join(set(ctypes))

        if total_chunks > 1e8:
            type = 'parq'

        if override_type:
            type = override_type

        # Override existing details
        self.file_type = type
        # File type set in two different places (historic)
        details['type'] = type

        existing_details = self.detail_cfg.get()
        existing_details.update(details)

        self.detail_cfg.set(existing_details)
        self.save_files()

if __name__ == '__main__':
    print('Kerchunk Pipeline Config Scanner - run using master scripts')