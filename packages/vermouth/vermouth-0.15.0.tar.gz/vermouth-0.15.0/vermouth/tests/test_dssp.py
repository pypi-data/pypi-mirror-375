# Copyright 2018 University of Groningen
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
Test the functions required to use DSSP.
"""

import os
import glob
import itertools

import networkx as nx
import numpy as np
import pytest

import vermouth
from vermouth.file_writer import DeferredFileWriter
from vermouth.forcefield import get_native_force_field
from vermouth.dssp import dssp
from vermouth.dssp.dssp import DSSPError, AnnotateDSSP
from vermouth.pdb.pdb import read_pdb
from vermouth.tests.datafiles import (
    PDB_PROTEIN,
    DSSP_OUTPUT,
    DSSP_SS_OUTPUT,
    PDB_ALA5_CG,
    PDB_ALA5,
)
from vermouth.tests.helper_functions import test_molecule, create_sys_all_attrs

DSSP_EXECUTABLE = os.environ.get("VERMOUTH_TEST_DSSP", "dssp")
SECSTRUCT_1BTA = list(
    "CEEEEETTTCCSHHHHHHHHHHHHTCCTTCCCSHHHHHHHHTTT"
    "SCSSEEEEEESTTHHHHTTTSSHHHHHHHHHHHHHTTCCEEEEEC"
)


# TODO: The code is very repetitive. There may be a way to refactor it with
# clever use of parametrize and fixtures.
class TestAnnotateResidues:
    """
    Tests for the :class:`dssp.AnnotateResidues` processor.
    """

    @staticmethod
    def build_molecule(nresidues):
        """
        Build a dummy molecule with the requested number of residues and 3
        atoms per residue.
        """
        molecule = vermouth.molecule.Molecule()
        residue_template = vermouth.molecule.Molecule()
        residue_template.add_nodes_from(
            (idx, {"chain": "", "atomname": str(idx), "resname": "DUMMY", "resid": 1})
            for idx in range(3)
        )
        for _ in range(nresidues):
            molecule.merge_molecule(residue_template)
        return molecule

    @staticmethod
    def sequence_from_mol(molecule, attribute, default=None):
        """
        Extract the content of an attribute for each node of a molecule.
        """
        return [node.get(attribute, default) for node in molecule.nodes.values()]

    def sequence_from_system(self, system, attribute, default=None):
        """
        Extract the content of an attribute for each node of a system.
        """
        return list(
            itertools.chain(
                *(
                    self.sequence_from_mol(molecule, attribute, default)
                    for molecule in system.molecules
                )
            )
        )

    @pytest.mark.parametrize("nres", (0, 1, 3, 10))
    def test_build_molecule(self, nres):
        """
        :meth:`build_molecule` and :meth:`sequence_from_mol` work as excpected.
        """
        expected_resid = list(itertools.chain(*([idx + 1] * 3 for idx in range(nres))))
        expected_atomname = ["0", "1", "2"] * nres
        expected_chain = [""] * (nres * 3)
        expected_resname = ["DUMMY"] * (nres * 3)
        molecule = self.build_molecule(nres)
        assert self.sequence_from_mol(molecule, "resid") == expected_resid
        assert self.sequence_from_mol(molecule, "resname") == expected_resname
        assert self.sequence_from_mol(molecule, "chain") == expected_chain
        assert self.sequence_from_mol(molecule, "atomname") == expected_atomname

    @pytest.fixture
    def single_mol_system(self):
        """
        Build a system with a single molecule that count 5 residues of 3 atoms
        each.
        """
        molecule = self.build_molecule(5)
        system = vermouth.system.System()
        system.molecules = [molecule]
        return system

    @pytest.fixture
    def multi_mol_system_irregular(self):
        """
        Build a system with 3 molecules having 4, 5, and 6 residues,
        respectively.
        """
        system = vermouth.system.System()
        system.molecules = [self.build_molecule(nres) for nres in (4, 5, 6)]
        return system

    @pytest.fixture
    def multi_mol_system_regular(self):
        """
        Build a system with 3 molecules having each 4 residues.
        """
        system = vermouth.system.System()
        system.molecules = [self.build_molecule(4) for _ in range(3)]
        return system

    @pytest.mark.parametrize(
        "sequence",
        (
            "ABCDE",
            ["A", "B", "C", "D", "E"],
            range(5),
        ),
    )
    def test_single_molecule(self, single_mol_system, sequence):
        """
        The simple case with a single molecule and a sequence of the right size
        works as expected.
        """
        expected = list(itertools.chain(*([element] * 3 for element in sequence)))
        processor = dssp.AnnotateResidues("test", sequence)
        processor.run_system(single_mol_system)
        found = self.sequence_from_system(single_mol_system, "test")
        assert found == expected

    @pytest.mark.parametrize(
        "sequence",
        (
            "ABCDEFGHIJKLMNO",
            list("ABCDEFGHIJKLMNO"),
            range(15),
        ),
    )
    def test_multi_molecules_diff_sizes(self, multi_mol_system_irregular, sequence):
        """
        The case of many protein of various sizes and a sequence of the right
        size works as expected.
        """
        expected = list(itertools.chain(*([element] * 3 for element in sequence)))
        processor = dssp.AnnotateResidues("test", sequence)
        processor.run_system(multi_mol_system_irregular)
        found = self.sequence_from_system(multi_mol_system_irregular, "test")
        assert found == expected

    @pytest.mark.parametrize(
        "sequence",
        (
            "ABCD",
            ["A", "B", "C", "D"],
            range(4),
        ),
    )
    def test_multi_molecules_cycle(self, multi_mol_system_regular, sequence):
        """
        The case with multiple molecules with all the same size and one
        sequence to repeat for each molecule works as expected.
        """
        expected = list(itertools.chain(*([element] * 3 for element in sequence)))
        expected = expected * 3
        processor = dssp.AnnotateResidues("test", sequence)
        processor.run_system(multi_mol_system_regular)
        found = self.sequence_from_system(multi_mol_system_regular, "test")
        assert found == expected

    def test_single_molecules_cycle_one(self, single_mol_system):
        """
        One molecule and a one element sequence to repeat over all residues of
        the molecule.
        """
        sequence = "A"
        expected = [sequence] * (5 * 3)
        processor = dssp.AnnotateResidues("test", sequence)
        processor.run_system(single_mol_system)
        found = self.sequence_from_system(single_mol_system, "test")
        assert found == expected

    def test_multi_molecules_cycle_one(self, multi_mol_system_irregular):
        """
        Many molecules and a one element sequence to repeat.
        """
        sequence = "A"
        expected = [sequence] * (15 * 3)
        processor = dssp.AnnotateResidues("test", sequence)
        processor.run_system(multi_mol_system_irregular)
        found = self.sequence_from_system(multi_mol_system_irregular, "test")
        assert found == expected

    @staticmethod
    @pytest.mark.parametrize(
        "sequence",
        (
            "ABC",  # Too short
            "ABCD",  # Too short, match the length of the first molecule
            "ABCDEFGHIFKLMNOPQRSTU",  # Too long
            "",  # Empty
        ),
    )
    def test_wrong_length(multi_mol_system_irregular, sequence):
        """
        Many molecule and a sequence that has the wrong length raises an error.
        """
        processor = dssp.AnnotateResidues("test", sequence)
        with pytest.raises(ValueError):
            processor.run_system(multi_mol_system_irregular)

    @staticmethod
    @pytest.mark.parametrize(
        "sequence",
        (
            "ABC",  # Too short
            "ABCD",  # Too short, match the length of the first molecule
            "ABCDEFGHIFKLMNOPQRSTU",  # Too long
            "",  # Empty
            "ABCDEFGHIJKLMNO",  # Length of all the molecules, without filter
        ),
    )
    def test_wrong_length_with_filter(multi_mol_system_irregular, sequence):
        """
        Many molecules and a sequence that has the wrong length because of a
        molecule selector.
        """
        # We exclude the second molecule. The filter excludes it based on the
        # number of nodes, which is 15 because it has 5 residues with 3 nodes
        # each.
        processor = dssp.AnnotateResidues(
            "test",
            sequence,
            molecule_selector=lambda mol: len(mol.nodes) != (5 * 3),
        )
        with pytest.raises(ValueError):
            processor.run_system(multi_mol_system_irregular)

    @staticmethod
    def test_empty_system_empty_sequence():
        """
        There are no molecules, but the sequence is empty.
        """
        system = vermouth.system.System()
        sequence = ""
        processor = dssp.AnnotateResidues("test", sequence)
        try:
            processor.run_system(system)
        except ValueError:
            pytest.fail("Should not have raised a ValueError.")

    @staticmethod
    def test_empty_system_error():
        """
        There are no molecules, but there is a sequence. Should raise an error.
        """
        system = vermouth.system.System()
        sequence = "not empty"
        processor = dssp.AnnotateResidues("test", sequence)
        with pytest.raises(ValueError):
            processor.run_system(system)

    @staticmethod
    def test_empty_with_filter(multi_mol_system_irregular):
        """
        There is a sequence, but no molecule are accepted by the molecule
        selector. Should raise an error.
        """
        sequence = "not empty"
        processor = dssp.AnnotateResidues(
            "test", sequence, molecule_selector=lambda mol: False
        )
        with pytest.raises(ValueError):
            processor.run_system(multi_mol_system_irregular)

    def test_run_molecule(self, single_mol_system):
        """
        The `run_molecule` method works.
        """
        sequence = "ABCDE"
        expected = list(itertools.chain(*([element] * 3 for element in sequence)))
        processor = dssp.AnnotateResidues("test", sequence)
        processor.run_molecule(single_mol_system.molecules[0])
        found = self.sequence_from_system(single_mol_system, "test")
        assert found == expected

    def test_run_molecule_not_selected(self, single_mol_system):
        """
        The molecule selector works with `run_molecule`.
        """
        sequence = "ABCDE"
        processor = dssp.AnnotateResidues(
            "test", sequence, molecule_selector=lambda mol: False
        )
        processor.run_molecule(single_mol_system.molecules[0])
        found = self.sequence_from_system(single_mol_system, "test")
        assert vermouth.utils.are_all_equal(found)
        assert found[0] is None


#@pytest.mark.parametrize(
#    "input_file, expected",
#    [
#        (str(DSSP_OUTPUT), "".join(SECSTRUCT_1BTA)),
#        (
#            str(DSSP_SS_OUTPUT / "mini-protein1_betasheet.pdb.v2.2.1-3b2-deb_cv1.ssd"),
#            "CEEEEEETTEEEEEECCCCCCTTCEEEEC",
#        ),
#        (
#            str(DSSP_SS_OUTPUT / "mini-protein1_betasheet.pdb.v3.0.0-3b1-deb_cv1.ssd"),
#            "CEEEEEETTEEEEEECCCCCCTTCEEEEC",
#        ),
#        (
#            str(DSSP_SS_OUTPUT / "mini-protein2_helix.pdb.v2.2.1-3b2-deb_cv1.ssd"),
#            "CCSHHHHHHHHHHCCCCHHHHHHHHHHHTSCHHHHHHHTCCC",
#        ),
#        (
#            str(DSSP_SS_OUTPUT / "mini-protein2_helix.pdb.v3.0.0-3b1-deb_cv1.ssd"),
#            "CCSHHHHHHHHHHCCCCHHHHHHHHHHHTSCHHHHHHHTCCC",
#        ),
#        (
#            str(DSSP_SS_OUTPUT / "mini-protein3_trp-cage.pdb.v2.2.1-3b2-deb_cv1.ssd"),
#            "CHHHHHHHTTGGGGTCCCCC",
#        ),
#        (
#            str(DSSP_SS_OUTPUT / "mini-protein3_trp-cage.pdb.v3.0.0-3b1-deb_cv1.ssd"),
#            "CHHHHHHHTTGGGGTCCCCC",
#        ),
#    ],
#)
#def test_read_dssp2(input_file, expected):
#    """
#    Test that :func:`vermouth.dssp.dssp.read_dssp2` returns the expected
#    secondary structure sequence.
#    """
#    with open(input_file, encoding="utf-8") as infile:
#        secondary_structure = dssp.read_dssp2(infile)
#    assert "".join(secondary_structure) == expected
#
#
#@pytest.mark.parametrize("savefile", [True, False])
#def test_run_dssp(savefile, tmp_path):
#    """
#    Test that :func:`vermouth.molecule.dssp.dssp.run_dssp` runs as expected and
#    generate a save file only if requested.
#    """
#    # The test runs twice, once with the savefile set to True so we test with
#    # saving the DSSP output to file, and once with savefile set t False so we
#    # do not generate the file. The "savefile" argument is set by
#    # pytest.mark.parametrize.
#    # The "tmp_path" argument is set by pytest and is the path to a temporary
#    # directory that exists only for one iteration of the test.
#    if savefile:
#        path = tmp_path
#    else:
#        path = None
#    system = vermouth.System()
#    for molecule in read_pdb(str(PDB_PROTEIN)):
#        system.add_molecule(molecule)
#    secondary_structure = dssp.run_dssp(
#        system, executable=DSSP_EXECUTABLE, savedir=path
#    )
#
#    # Make sure we produced the expected sequence of secondary structures
#    assert secondary_structure == SECSTRUCT_1BTA
#
#    # If we test with savefile, then we need to make sure the file is created
#    # and its content corresponds to the reference (excluding the first lines
#    # that are variable or contain non-essencial data read from the PDB file).
#    # If we test without savefile, then we need to make sure the file is not
#    # created.
#    if savefile:
#        DeferredFileWriter().write()
#        assert path.exists()
#        foundfile = list(path.glob('chain_*.ssd'))
#        assert len(foundfile) == 1
#        foundfile = foundfile[0]
#
#        with open(foundfile, encoding="utf-8") as genfile, open(str(DSSP_OUTPUT), encoding="utf-8") as reffile:
#            # DSSP 3 is outputs mostly the same thing as DSSP2, though there
#            # are some differences in non significant whitespaces, and an extra
#            # field header. We need to normalize these differences to be able
#            # to compare.
#            gen = "\n".join(
#                [
#                    line.strip().replace("            CHAIN", "")
#                    for line in genfile.readlines()[6:]
#                ]
#            )
#            ref = "\n".join([line.strip() for line in reffile.readlines()[6:]])
#            assert gen == ref
#    else:
#        # Is the directory empty?
#        assert not list(tmp_path.iterdir())
#
#
#@pytest.mark.parametrize(
#    "pdb, loglevel,expected",
#    [
#        (PDB_PROTEIN, 10, True),  # DEBUG
#        (PDB_PROTEIN, 30, False),  # WARNING
#        # Using a CG pdb will cause a DSSP error, which should preserve the input
#        (PDB_ALA5_CG, 10, True),  # DEBUG
#        (PDB_ALA5_CG, 30, True),  # WARNING
#    ],
#)
#def test_run_dssp_input_file(tmp_path, caplog, pdb, loglevel, expected):
#    """
#    Test that the DSSP input file is preserved (only) in the right conditions
#    """
#    caplog.set_level(loglevel)
#    system = vermouth.System()
#    for molecule in read_pdb(str(pdb)):
#        system.add_molecule(molecule)
#    os.chdir(tmp_path)
#    try:
#        dssp.run_dssp(system, executable=DSSP_EXECUTABLE)
#    except DSSPError:
#        pass
#    if expected:
#        target = 1
#    else:
#        target = 0
#    matches = glob.glob("dssp_in*.pdb")
#    assert len(matches) == target, matches
#    if matches:
#        # Make sure it's a valid PDB file. Mostly anyway.
#        list(read_pdb(matches[0]))
#
#def test_run_dssp_executable():
#    """
#    Test that the executable for dssp is actually found
#    """
#    system = vermouth.System()
#    for molecule in read_pdb(str(PDB_PROTEIN)):
#        system.add_molecule(molecule)
#
#    with pytest.raises(DSSPError):
#        dssp.run_dssp(system, executable='doesnt_exist')

@pytest.mark.parametrize('ss_struct, expected', (
    (list('ABCDE'), list('ABCDE')),
    (list('AB DE'), list('ABCDE')),
    ([['A'], ['B'], ['C'], ['F'], ['G']], list('ABCFG')),
    ([['A'], [' '], ['E'], ['F'], [' ']], list('ACEFC')),
))
def test_mdtraj(monkeypatch, ss_struct, expected):
    # We don't want to test mdtraj.compute_dssp, so mock it.
    compute_dssp = lambda *_, **__: np.array(ss_struct)
    monkeypatch.setattr(vermouth.dssp.dssp.mdtraj, "compute_dssp", compute_dssp)
    system = vermouth.System()
    for molecule in read_pdb(str(PDB_ALA5)):
        system.add_molecule(molecule)

    processor = AnnotateDSSP(executable=None)
    processor.run_system(system)

    found = []
    for mol in system.molecules:
        residues = mol.iter_residues()
        for residue in residues:
            found.append(mol.nodes[residue[0]]['aasecstruct'])

    assert found == expected


#def test_cterm_atomnames():
#    nodes = [
#        dict(
#            resname="ALA",
#            atomname="N",
#            element="N",
#            resid=1,
#            chain="",
#            position=np.array([9.534, 5.359, 0.000]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="CA",
#            element="C",
#            resid=1,
#            chain="",
#            position=np.array([10.190, 6.661, -0.000]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="C",
#            element="C",
#            resid=1,
#            chain="",
#            position=np.array([11.706, 6.515, 0.000]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="O",
#            element="O",
#            resid=1,
#            chain="",
#            position=np.array([12.232, 5.403, 0.000]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="CB",
#            element="C",
#            resid=1,
#            chain="",
#            position=np.array([9.733, 7.484, 1.196]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="H",
#            element="H",
#            resid=1,
#            chain="",
#            position=np.array([10.101, 4.523, 0.000]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="HA",
#            element="H",
#            resid=1,
#            chain="",
#            position=np.array([9.914, 7.191, -0.912]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="1HB",
#            element="H",
#            resid=1,
#            chain="",
#            position=np.array([10.231, 8.454, 1.181]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="2HB",
#            element="H",
#            resid=1,
#            chain="",
#            position=np.array([8.654, 7.630, 1.147]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="3HB",
#            element="H",
#            resid=1,
#            chain="",
#            position=np.array([9.987, 6.960, 2.116]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="N",
#            element="N",
#            resid=2,
#            chain="",
#            position=np.array([12.404, 7.646, 0.000]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="CA",
#            element="C",
#            resid=2,
#            chain="",
#            position=np.array([13.862, 7.646, 0.000]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="C",
#            element="C",
#            resid=2,
#            chain="",
#            position=np.array([14.413, 9.066, 0.000]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="O1",
#            element="O",
#            resid=2,
#            chain="",
#            position=np.array([14.462, 9.691, 1.023]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="O2",
#            element="O",
#            resid=2,
#            chain="",
#            position=np.array([14.798, 9.560, -1.023]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="CB",
#            element="C",
#            resid=2,
#            chain="",
#            position=np.array([14.392, 6.868, -1.196]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="H",
#            element="H",
#            resid=2,
#            chain="",
#            position=np.array([11.912, 8.528, -0.000]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="HA",
#            element="H",
#            resid=2,
#            chain="",
#            position=np.array([14.212, 7.162, 0.912]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="1HB",
#            element="H",
#            resid=2,
#            chain="",
#            position=np.array([15.482, 6.878, -1.181]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="2HB",
#            element="H",
#            resid=2,
#            chain="",
#            position=np.array([14.038, 5.839, -1.147]),
#        ),
#        dict(
#            resname="ALA",
#            atomname="3HB",
#            element="H",
#            resid=2,
#            chain="",
#            position=np.array([14.038, 7.331, -2.116]),
#        ),
#    ]
#    edges = [
#        (0, 1),
#        (0, 5),
#        (1, 2),
#        (1, 4),
#        (1, 6),
#        (2, 3),
#        (4, 7),
#        (4, 8),
#        (4, 9),
#        (2, 10),
#        (10, 11),
#        (10, 16),
#        (11, 12),
#        (11, 15),
#        (11, 17),
#        (12, 13),
#        (12, 14),
#        (15, 18),
#        (15, 19),
#        (15, 20),
#    ]
#    ff = get_native_force_field("charmm")
#    mol = vermouth.molecule.Molecule(force_field=ff)
#    mol.add_nodes_from(enumerate(nodes))
#    mol.add_edges_from(edges)
#    system = vermouth.system.System(force_field=ff)
#    system.add_molecule(mol)
#    vermouth.processors.RepairGraph().run_system(system)
#    vermouth.processors.CanonicalizeModifications().run_system(system)
#    dssp_out = dssp.run_dssp(system, executable=DSSP_EXECUTABLE)
#    assert dssp_out == list("CC")


@pytest.mark.parametrize('sequence, expected', [
    ('H', '3'),
    ('HH', '33'),
    ('CHH', 'C33'),
    ('HHHHHH', '113322'),
    ('EHHHHHHC', 'E113322C'),
    ('HHHHHHHHH', '1111H2222'),
    ('CHHHHHHHHHC', 'C1111H2222C'),
    ('CHHHHEHHHHC', 'C3333E3333C'),
])
def test_convert_dssp_to_martini(sequence, expected):
    found = dssp.convert_dssp_to_martini(sequence)
    assert expected == found

@pytest.mark.parametrize('resnames, ss_string, secstruc',
     (      # protein resnames with secstruc
             ({0: "ALA", 1: "ALA", 2: "ALA",
               3: "GLY", 4: "GLY",
               5: "MET",
               6: "ARG", 7: "ARG", 8: "ARG"},
              'HHHH',
              {1: "H", 2: "H", 3: "H", 4: "H"}
              ),
             # not protein resnames, no secstruc annotated or gets written
             ({0: "A", 1: "A", 2: "A",
               3: "B", 4: "B",
               5: "C",
               6: "D", 7: "D", 8: "D"},
              "",
              {1: "", 2: "", 3: "", 4: ""}
              )
     ))
def test_gmx_system_header(test_molecule, resnames, ss_string, secstruc):

    atypes = {0: "P1", 1: "SN4a", 2: "SN4a",
              3: "SP1", 4: "C1",
              5: "TP1",
              6: "P1", 7: "SN3a", 8: "SP4"}

    system = create_sys_all_attrs(test_molecule,
                                  moltype="molecule_0",
                                  secstruc=secstruc,
                                  defaults={"chain": "A"},
                                  attrs={"resname": resnames,
                                         "atype": atypes})

    # annotate the actual 'secstruct' attribute because create_sys_all_attrs actually annotates cgsecstruct
    dssp.AnnotateResidues(attribute="aasecstruct",
                          sequence="HHHH").run_system(system)

    dssp.AnnotateMartiniSecondaryStructures().run_system(system)

    assert ss_string in system.meta.get('header', [''])
