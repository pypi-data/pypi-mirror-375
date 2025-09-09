"""
@Author: Luo Jiejian
"""
import os
import subprocess
import tempfile
from typing import Optional, List

import numpy as np
import trimesh
from Bio.PDB import Selection
from Bio.PDB.ResidueDepth import _get_atom_radius, _read_vertex_array
from gemmi_protools import StructureParser
from gemmi_protools import gemmi2bio


def _read_face_array(filename: str):
    with open(filename) as fp:
        face_list = []
        for line in fp:
            sl = line.split()
            if len(sl) != 5:
                # skip header
                continue
            vl = [int(x) for x in sl[0:3]]
            face_list.append(vl)
    return np.array(face_list)


def get_mesh(struct_file: str, chains: Optional[List[str]] = None, MSMS: str = "msms"):
    """

    :param struct_file: str
        .pdb, .cif, .pdb.gz, .cif.gz
    :param chains: a list of chain names
        default None to include all chains
    :param MSMS: str
        path of msms executable
    :return:
        https://ccsb.scripps.edu/msms/downloads/
    """

    try:
        st = StructureParser()
        st.load_from_file(struct_file)
        st.clean_structure(remove_ligand=True)

        bio_st = gemmi2bio(st.STRUCT)
        model = bio_st[0]

        # Replace pdb_to_xyzr
        # Make x,y,z,radius file
        atom_list = Selection.unfold_entities(model, "A")

        xyz_tmp = tempfile.NamedTemporaryFile(delete=False).name
        with open(xyz_tmp, "w") as pdb_to_xyzr:
            for atom in atom_list:
                x, y, z = atom.coord
                radius = _get_atom_radius(atom, rtype="united")
                pdb_to_xyzr.write(f"{x:6.3f}\t{y:6.3f}\t{z:6.3f}\t{radius:1.2f}\n")

        # Make surface
        surface_tmp = tempfile.NamedTemporaryFile(delete=False).name
        msms_tmp = tempfile.NamedTemporaryFile(delete=False).name
        MSMS = MSMS + " -no_header -probe_radius 1.5 -if %s -of %s > " + msms_tmp
        make_surface = MSMS % (xyz_tmp, surface_tmp)
        subprocess.call(make_surface, shell=True)
        face_file = surface_tmp + ".face"
        surface_file = surface_tmp + ".vert"
        if not os.path.isfile(surface_file):
            raise RuntimeError(
                f"Failed to generate surface file using command:\n{make_surface}"
            )

    except Exception as e:
        print(str(e))
        mesh = None
    else:
        # Read surface vertices from vertex file
        vertices = _read_vertex_array(surface_file)
        faces = _read_face_array(face_file)
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces - 1)
        mesh.merge_vertices()
        mesh.update_faces(mesh.unique_faces())
        mesh.update_faces(mesh.nondegenerate_faces())
        mesh.remove_unreferenced_vertices()
    finally:
        # Remove temporary files
        for fn in [xyz_tmp, surface_tmp, msms_tmp, face_file, surface_file]:
            try:
                os.remove(fn)
            except OSError:
                pass

    return mesh
