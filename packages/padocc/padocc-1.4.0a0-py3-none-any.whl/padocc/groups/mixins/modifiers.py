__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import os
import json

from typing import Callable, Union, Any

from padocc import ProjectOperation
from padocc.core.utils import BASE_CFG, source_opts, valid_project_code

class ModifiersMixin:
    """
    Modifiers to the group in terms of the projects associated,
    allows adding and removing projects.

    This is a behavioural Mixin class and thus should not be
    directly accessed. Where possible, encapsulated classes 
    should contain all relevant parameters for their operation
    as per convention, however this is not the case for mixin
    classes. The mixin classes here will explicitly state
    where they are designed to be used, as an extension of an 
    existing class.
    
    Use case: GroupOperation [ONLY]
    """

    @classmethod
    def help(cls, func: Callable = print):
        func('Modifiers:')
        func(
            ' > group.add_project() - Add a new project, '
            'requires a base config (padocc.core.utils.BASE_CFG) compliant dictionary')
        func(' > group.remove_project() - Delete project and all associated files')
        func(' > group.transfer_project() - Transfer project to a new "receiver" group')
        func(' > group.merge() - Merge two groups')
        func(
            ' > group.unmerge() - Split one group into two sets, '
            'given a list of datasets to move into the new group.')

    def set_all_values(self, attr: str, value: Any, repeat_id: str = 'main'):
        """
        Set a particular value for all projects in a group.
        """
        self.logger.info(f'Applying {attr}:{value} to all projects')

        for project in self.__iter__(repeat_id=repeat_id):
            try:
                setattr(project, attr, value)
            except Exception as err:
                self.logger.error('Error when trying to apply value to all projects')
                raise err
            project.save_files()

        self.logger.info('All projects saved')

    def apply_pfunc(self, pfunc: Callable, repeat_id: str = 'main'):
        """
        Apply a custom function across all projects.
        """
        self.logger.info(f'Applying {pfunc} to all projects')

        for project in self.__iter__(repeat_id=repeat_id):
            try:
                project = pfunc(project)
            except Exception as err:
                self.logger.error('Error when trying to perform custom function:')
                raise err
            project.save_files()

        self.logger.info('All projects saved')
    
    def catalog_ceda(
            self,
            final_location: str, 
            api_key: str, 
            collection: str,
            name_list: Union[list,None] = None,
            repeat_id: str = 'main'
        ):
        """
        Catalog all projects in the group into the 
        ``ceda-cloud-projects`` index."""

        if name_list is not None:
            if len(name_list) != len(self.proj_codes[repeat_id]):
                raise ValueError(
                    'Insufficient replacement names provided - '
                    f'needs {len(self.proj_codes[repeat_id])}, '
                    f'given {len(name_list)}'
                )

        for pid, proj_code in enumerate(self.proj_codes[repeat_id]):

            name_replace = None
            if name_list is not None:
                name_replace = name_list[pid]

            proj = self[proj_code]
            proj.catalog_ceda(
                final_location,
                api_key,
                collection,
                name_replace = name_replace
            )

    def add_project(
            self,
            config: Union[str,dict],
            remote_s3: Union[dict, str, None] = None,
            moles_tags: bool = False,
        ):
        """
        Add a project to this group. 

        :param config:  (str | dict) The configuration details to add new project. Can either be 
            a path to a json file or json content directly. Can also be either a properly formatted
            base config file (needs ``proj_code``, ``pattern`` etc.) or a moles_esgf input file.

        :param moles_tags:  (bool) Option for CEDA staff to integrate output from another package.
        """

        if isinstance(config, str):
            if config.endswith('.json'):
                with open(config) as f:
                    config = json.load(f)
            elif config.endswith('.csv'):
                cfg = {}
                with open(config) as f:
                    for line in f.readlines():
                        key = line.split(',')[0]
                        fileset = line.split(',')[1]
                        cfg[key] = fileset
            
                config = cfg
            else:
                config = json.loads(config)
        
        configs = []
        if moles_tags:
            for key, fileset in config.items():
                conf = dict(BASE_CFG)
                conf['proj_code'] = key
                conf['pattern'] = fileset

                accept = True
                for f in fileset:
                    if str('.' + f.split('.')[-1]) not in source_opts:
                        accept = False

                if accept:
                    configs.append(conf)
                else:
                    self.logger.info(f'Rejected {key} - not all files are friendly.')
        else:
            configs.append(config)

        new_codes = []
        recombine = False
        for config in configs:

            if config['proj_code'] in self.proj_codes['main']:
                self.logger.warning(
                    f'proj_code {config["proj_code"]} already exists for this group.'
                )
                if not self._forceful:
                    continue
                # Recombine sets if contains duplicates and doing overwrites.
                recombine = True

            status = valid_project_code(config['proj_code'])
            if not status:
                raise ValueError(
                    'One or more failed project code checks'
                )

            new_codes.append(config['proj_code'])

            self._init_project(config, remote_s3=remote_s3)

        if recombine:
            self._add_proj_codeset('temp',new_codes)
            self.merge_subsets(['main','temp'], 'main')
            self._delete_proj_codeset('temp')
        else:
            for code in new_codes:
                self.proj_codes['main'].append(code)
        self.save_files()

    def remove_projects(self, proj_code: str, ask: bool = True) -> None:
        """
        Remove one or more projects from this group
        """
        proj_codes = proj_code.split(',')
        code_labels = []
        for i in proj_codes:
            if i in self.proj_codes['main']:
                code_labels.append(i)
            elif i.isnumeric():
                code_labels.append(self.proj_codes['main'][i])
        for pc in code_labels:
            self.remove_project(pc, ask=ask)

    def remove_project(self, proj_code: str, ask: bool = True) -> None:
        """
        Remove a project from this group
        Steps required:
        1. Remove the project directory including all internal files.
        2. Remove the project code from all project files.
        """

        if ask:
            inp = input(f'Are you sure you want to delete {proj_code}? (Y/N) ')
            if inp != 'Y':
                self.logger.warning(f'Skipped Deleting directory (User entered {inp})')
                return

        for pset in self.proj_codes.values():
            if proj_code in pset:
                pset.remove(proj_code)

        if proj_code in self.datasets:
            self.datasets.pop(proj_code)
        if proj_code in self.faultlist:
            self.faultlist.pop(proj_code)

        proj_op = ProjectOperation(
            proj_code,
            self.workdir,
            groupID=self.groupID,
            forceful=self._forceful,
            dryrun=self._dryrun
        )

        proj_op.delete_project(ask=False)

    def transfer_projects(self, proj_codes: Union[list,str], receiver_group, repeat_id: str = 'main') -> None:
        """
        Transfer multiple projects between groups
        """

        if isinstance(proj_codes,str):
            proj_codes = [self.proj_codes[repeat_id][int(p)] for p in proj_codes.split(',')]
        elif repeat_id != 'main':
            proj_codes = self.proj_codes[repeat_id]
        
        for proj_code in list(proj_codes):
            self.transfer_project(proj_code, receiver_group)

    def transfer_project(self, proj_code: str, receiver_group) -> None:
        """
        Transfer an existing project to a new group
        """

        # 0. Check all objects exist
        if proj_code not in self.proj_codes['main']:
            raise ValueError(
                f'{proj_code} not found in group {self.groupID}'
            )
        
        if proj_code in receiver_group.proj_codes['main']:
            raise ValueError(
                f'proj_code {proj_code} already exists for '
                f'group {receiver_group.groupID}'
            )

        # 1. Transfer in proj codes
        for pset in self.proj_codes.values():
            if proj_code in pset:
                pset.remove(proj_code)
        receiver_group.proj_codes['main'].append(proj_code)

        # 2. Transfer in datasets
        new_datasets = []
        for ds in self.datasets:
            if ds[0] == proj_code:
                receiver_group.datasets.append(ds)
            else:
                new_datasets.append(ds)
        self.datasets.set(new_datasets)

        self.save_files()
        receiver_group.save_files()

        # 3. Migrate project
        proj_op = ProjectOperation(
            proj_code,
            self.workdir,
            self.groupID,
            verbose=self._verbose,
            logid=f'transfer-{proj_code}'
        )

        proj_op = proj_op.migrate(receiver_group.groupID)

    def merge(group_A,group_B):
        """
        Merge group B into group A.
        1. Migrate all projects from B to A and reset groupID values.
        2. Combine datasets.csv
        3. Combine project codes
        4. Combine faultlists.

        Note: This is not a class method. The 
        ``self`` object is replaced by ``group_A``
        for convenience.
        """

        new_proj_dir = f'{group_A.workdir}/in_progress/{group_A.groupID}'
        group_A.logger.info(f'Merging {group_B.groupID} into {group_A.groupID}')

        # Combine projects
        for proj_code in group_B.proj_codes['main']:
            proj_op = ProjectOperation(
                proj_code,
                group_B.workdir,
                group_B.groupID
            )
            group_A.logger.debug(f'Migrating project {proj_code}')
            proj_op.migrate(group_A.groupID)

        # Datasets
        group_A.datasets.set(
            group_A.datasets.get() + group_B.datasets.get()
        )
        group_B.datasets.remove_file()
        group_A.logger.debug(f'Removed dataset file for {group_B.groupID}')

        # faultlists
        group_A.faultlist.set(
            group_A.faultlist.get() + group_B.faultlist.get()
        )
        group_B.faultlist.remove_file()
        group_A.logger.debug(f'Removed faultlist file for {group_B.groupID}')

        # Subsets
        for name, subset in group_B.proj_codes.items():
            if name not in group_A.proj_codes:
                subset.move_file(group_A.groupdir)
                group_A.logger.debug(f'Migrating subset {name}')
            else:
                group_A.proj_codes[name].set(
                    group_A.proj_codes[name].get() + subset.get()
                )
                group_A.logger.debug(f'Merging subset {name}')
                subset.remove_file()

        group_A.logger.info("Merge operation complete")
        del group_B

    def unmerge(group_A, group_B, dataset_list: list):
        """
        Separate elements from group_A into group_B
        according to the list
        1. Migrate projects
        2. Set the datasets
        3. Set the faultlists
        4. Project codes (remove group B sections)
        
        Note: This is not a class method. The 
        ``self`` object is replaced by ``group_A``
        for convenience.
        """

        group_A.logger.info(
            f"Separating {len(dataset_list)} datasets from "
            f"{group_A.groupID} to {group_B.groupID}")
        
        new_proj_dir = f'{group_B.workdir}/in_progress/{group_B.groupID}'

        # Combine projects
        for proj_code in dataset_list:
            proj_op = ProjectOperation(
                proj_code,
                group_A.workdir,
                group_A.groupID
            )

            proj_op.move_to(new_proj_dir)
            proj_op.groupID = group_B.groupID
        
        # Set datasets
        group_B.datasets.set(dataset_list)
        group_A.datasets.set(
            [ds for ds in group_A.datasets if ds not in dataset_list]
        )

        group_A.logger.debug(f"Created datasets file for {group_B.groupID}")

        # Set faultlist
        A_faultlist, B_faultlist = [],[]
        for bl in group_A.faultlist:
            if bl in dataset_list:
                B_faultlist.append(bl)
            else:
                A_faultlist.append(bl)

        group_A.faultlist.set(A_faultlist)
        group_B.faultlist.set(B_faultlist)
        group_A.logger.debug(f"Created faultlist file for {group_B.groupID}")

        # Combine project subsets
        group_B.proj_codes['main'].set(dataset_list)
        for name, subset in group_A.proj_codes.items():
            if name != 'main':
                subset.set([s for s in subset if s not in dataset_list])
        group_A.logger.debug(f"Removed all datasets from all {group_A.groupID} subsets")


        group_A.logger.info("Unmerge operation complete")

    def delete_group(self, ask: bool = True) -> None:
        """
        Delete the entire set of files associated with this group.
        """

        complete = self.get_codes_by_status()['complete']
        if len(complete) != len(self):
            self.logger.warning(f'Not all projects appear fully complete ({len(complete)}/{len(self)})')
            ask = True

        if ask:
            x=input(f'Delete all files relating to group: {self.groupID}? (Y/N) ')
            if x != 'Y':
                return
        
        for project in self:
            project.delete_project(ask=False)

        os.system(f'rm -rf {self.workdir}/in_progress/{self.groupID}')
        os.system(f'rm -rf {self.groupdir}')

        self.logger.info(f'Deleted group - {self.groupID}')
        return None