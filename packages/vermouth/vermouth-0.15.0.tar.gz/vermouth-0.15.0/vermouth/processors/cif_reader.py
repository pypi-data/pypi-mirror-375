#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2025 University of Groningen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Provides a processor that reads a CIF file.

See also
--------
:mod:`vermouth.pdb.cif`
"""


from ..pdb import CIFReader
from .processor import Processor


class CIFInput(Processor):
    """
    Reads CIF files.

    Attributes
    ----------
    filename: str
        The filename to parse.
    exclude: collections.abc.Container[str]
        A collection of residue names that should not be parsed and excluded
        from the final molecule(s)
    ignh: bool
        If True, hydrogens will be discarded from the input structure.
    modelidx: int
        If the cif file contains multiple models, which one to select.

    See also
    --------
    :func:`~vermouth.pdb.cif.read_cif_file`

    """
    def __init__(self, filename, exclude=(), ignh=False, modelidx=0):
        super().__init__()
        self.filename = filename
        self.exclude = exclude
        self.ignh = ignh
        self.modelidx = modelidx

    def run_system(self, system):
        molecules = CIFReader(self.filename, self.exclude, self.ignh, self.modelidx).reader()
        for molecule in molecules:
            system.add_molecule(molecule)
