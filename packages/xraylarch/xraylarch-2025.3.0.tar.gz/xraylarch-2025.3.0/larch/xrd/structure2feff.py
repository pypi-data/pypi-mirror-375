import os
from random import Random

from xraydb import atomic_symbol, atomic_number, xray_edge
from larch.utils.strutils import fix_varname, strict_ascii

from larixite.amcsd_utils import (SpacegroupAnalyzer, Molecule,
                                      IMolecule, IStructure)

rng = Random()

def get_atom_map(structure):
    """generalization of pymatgen atom map
    Returns:
        dict of ipots
    """
    unique_pot_atoms = []
    all_sites  = []
    for site in structure:
        for elem in site.species.elements:
            if elem.symbol not in unique_pot_atoms:
                unique_pot_atoms.append(elem.symbol)

    atom_map = {}
    for i, atom in enumerate(unique_pot_atoms):
        atom_map[atom] = i + 1
    return atom_map


def read_structure(structure_text, fmt="cif"):
    """read structure from text

    Arguments
    ---------
      structure_text (string):  text of structure file
      fmt (string):             format of structure file (cif, poscar, etc)

    Returns
    -------
      pymatgen Structure object or Molecule object
    """
    if Molecule is None:
        raise ImportError("pymatgen required. Try 'pip install pymatgen'.")
    try:
        if fmt.lower() in ('cif', 'poscar', 'contcar', 'chgcar', 'locpot', 'cssr', 'vasprun.xml'):
            struct = IStructure.from_str(structure_text, fmt, merge_tol=5.e-4)
        else:
            struct = IMolecule.from_str(structure_text, fmt)
        parse_ok = True
        file_found = True

    except:
        parse_ok = False
        file_found = False
        if os.path.exists(structure_text):
            file_found = True
            fmt = os.path.splitext(structure_text)[-1].lower()
            try:
                if fmt.lower() in ('cif', 'poscar', 'contcar', 'chgcar', 'locpot', 'cssr', 'vasprun.xml'):
                    struct = IStructure.from_file(structure_text, merge_tol=5.e-4)
                else:
                    struct = IMolecule.from_file(structure_text)
                parse_ok = True
            except:
                parse_ok = False

    if not parse_ok:
        if not file_found:
            raise FileNotFoundError(f'file {structure_text:s} not found')
        else:
            raise ValueError('invalid text of structure file')
    return struct

def structure_sites(structure_text, absorber=None, fmt='cif'):
    "return list of sites for the structure"
    struct = read_structure(structure_text, fmt=fmt)
    out = struct.sites
    if absorber is not None:
        abname = absorber.lower()
        out = []
        for site in struct.sites:
            species = site.species_string.lower()
            if ',' in species and ':' in species: # multi-occupancy site
                for siteocc in species.split(','):
                    sname, occ = siteocc.split(':')
                    if sname.strip() == abname:
                        out.append(site)
            elif species == abname:
                out.append(site)
        if len(out) == 0:
            out = struct.sites[0]
    return out

def parse_structure(structure_text, fmt='cif', fname="default.filename"):
    try:
        struct = read_structure(structure_text, fmt=fmt)
    except ValueError:
        return '# could not read structure file'

    return {'formula': struct.composition.reduced_formula, 'sites': struct.sites, 'structure_text': structure_text, 'fmt': fmt, 'fname': fname}


def structure2feffinp(structure_text, absorber, edge=None, cluster_size=8.0,
                      absorber_site=1, site_index=None, extra_titles=None,
                      with_h=False, version8=True, fmt='cif', rng_seed=None):
    """convert structure text to Feff8 or Feff6l input file

    Arguments
    ---------
      structure_text (string):  text of CIF file or name of the CIF file.
      absorber (string or int): atomic symbol or atomic number of absorbing element
                                (see Note 1)
      edge (string or None):    edge for calculation (see Note 2)     [None]
      cluster_size (float):     size of cluster, in Angstroms         [8.0]
      absorber_site (int):      index of site for absorber (see Note 3) [1]
      site_index (int or None): index of site for absorber (see Note 4) [None]
      extra_titles (list of str or None): extra title lines to include [None]
      with_h (bool):            whether to include H atoms [False]
      version8 (bool):          whether to write Feff8l input (see Note 5)[True]
      fmt (string):             format of structure file (cif, poscar, etc) [cif]
      rng_seed (int or None):   seed for RNG to get reproducible occupancy selections [None]
    Returns
    -------
      text of Feff input file

    Notes
    -----
      1. absorber is the atomic symbol or number of the absorbing element, and
         must be an element in the CIF structure.
      2. If edge is a string, it must be one of 'K', 'L', 'M', or 'N' edges (note
         Feff6 supports only 'K', 'L3', 'L2', and 'L1' edges). If edge is None,
         it will be assigned to be 'K' for absorbers with Z < 58 (Ce, with an
         edge energy < 40 keV), and 'L3' for absorbers with Z >= 58.
      3. for structures with multiple sites for the absorbing atom, the site
         can be selected by the order in which they are listed in the sites
         list. This depends on the details of the CIF structure, which can be
         found with `cif_sites(ciftext)`, starting counting by 1.
      4. to explicitly state the index of the site in the sites list, use
         site_index (starting at 1!)
      5. if version8 is False, outputs will be written for Feff6l

    """
    try:
        struct = read_structure(structure_text, fmt=fmt)
    except ValueError:
        return '# could not read structure file'

    global rng
    if rng_seed is not None:
        rng.seed(rng_seed)

    is_molecule = False

    if isinstance(struct, IStructure):
        sgroup = SpacegroupAnalyzer(struct).get_symmetry_dataset()
        space_group = sgroup["international"]
    else:
        space_group = 'Molecule'
        is_molecule = True


    if isinstance(absorber, int):
        absorber   = atomic_symbol(absorber_z)
    absorber_z = atomic_number(absorber)

    if edge is None:
        edge = 'K' if absorber_z < 58 else 'L3'

    edge_energy = xray_edge(absorber, edge).energy
    edge_comment = f'{absorber:s} {edge:s} edge, around {edge_energy:.0f} eV'

    unique_pot_atoms = []
    for site in struct:
        for elem in site.species.elements:
            if elem.symbol not in unique_pot_atoms:
                unique_pot_atoms.append(elem.symbol)

    atoms_map = {}
    for i, atom in enumerate(unique_pot_atoms):
        atoms_map[atom] = i + 1

    if absorber not in atoms_map:
        atlist = ', '.join(atoms_map.keys())
        raise ValueError(f'atomic symbol {absorber:s} not listed in structure data: ({atlist})')


    site_atoms = {}  # map xtal site with list of atoms occupying that site
    site_tags = {}
    absorber_count = 0
    for sindex, site in enumerate(struct.sites):
        site_species = [e.symbol for e in site.species]
        if len(site_species) > 1:
            s_els = [s.symbol for s in site.species.keys()]
            s_wts = [s for s in site.species.values()]
            site_atoms[sindex] = rng.choices(s_els, weights=s_wts, k=1000)
            site_tags[sindex] = f'({site.species_string:s})_{1+sindex:d}'
        else:
            site_atoms[sindex] = [site_species[0]] * 1000
            site_tags[sindex] = f'{site.species_string:s}_{1+sindex:d}'
        if absorber in site_species:
            absorber_count += 1
            if absorber_count == absorber_site:
                absorber_index = sindex

    if site_index is not None:
        absorber_index = site_index - 1

    # print("Got sites ", len(cstruct.sites), len(site_atoms), len(site_tags))

    center = struct[absorber_index].coords
    sphere = struct.get_neighbors(struct[absorber_index], cluster_size)
    symbols = [absorber]
    coords = [[0, 0, 0]]
    tags = [f'{absorber:s}_{1+absorber_index:d}']

    for i, site_dist in enumerate(sphere):
        s_index = site_dist[0].index

        site_symbol = site_atoms[s_index].pop()
        tags.append(site_tags[s_index])
        symbols.append(site_symbol)
        coords.append(site_dist[0].coords - center)
    cluster = Molecule(symbols, coords)

    out_text = ['*** feff input generated by xraylarch structure2feff using pymatgen ***']

    if extra_titles is not None:
        for etitle in extra_titles[:]:
            if not etitle.startswith('TITLE '):
                etitle = 'TITLE ' + etitle
            out_text.append(etitle)

    out_text.append(f'TITLE Formula:    {struct.composition.reduced_formula:s}')
    out_text.append(f'TITLE SpaceGroup: {space_group:s}')
    out_text.append(f'TITLE # sites:    {struct.num_sites}')

    out_text.append('* crystallographics sites: note that these sites may not be unique!')
    out_text.append(f'*     using absorber at site {1+absorber_index:d} in the list below')
    out_text.append(f'*     selected as absorber="{absorber:s}", absorber_site={absorber_site:d}')
    out_text.append('* index   X        Y        Z      species')

    for i, site in enumerate(struct):
        # The method of obtaining the cooridanates depends on whether the structure is a molecule or not
        if is_molecule:
            fc = site.coords
        else:
            fc = site.frac_coords
        species_string = fix_varname(site.species_string.strip())
        marker = '  <- absorber' if  (i == absorber_index) else ''
        out_text.append(f'* {i+1:3d}   {fc[0]:.6f} {fc[1]:.6f} {fc[2]:.6f}  {species_string:s} {marker:s}')

    out_text.extend(['* ', '', ''])

    if version8:
        out_text.append(f'EDGE    {edge:s}')
        out_text.append('S02     1.0')
        out_text.append('CONTROL 1 1 1 1 1 1')
        out_text.append('PRINT   1 0 0 0 0 3')
        out_text.append('EXAFS   20.0')
        out_text.append('NLEG     6')
        out_text.append(f'RPATH   {cluster_size:.2f}')
        out_text.append('*SCF    5.0')

    else:
        edge_index = {'K': 1, 'L1': 2, 'L2': 3, 'L3': 4}[edge]
        out_text.append(f'HOLE    {edge_index:d}  1.0  * {edge_comment:s} (2nd number is S02)')
        out_text.append('CONTROL 1 1 1 0 * phase, paths, feff, chi')
        out_text.append('PRINT   1 0 0 0')
        out_text.append(f'RMAX    {cluster_size:.2f}')

    out_text.extend(['', 'EXCHANGE 0', '',
                     '*  POLARIZATION  0 0 0', '',
                     'POTENTIALS',  '*    IPOT  Z   Tag'])

    # loop to find atoms actually in cluster, in case some atom
    # (maybe fractional occupation) is not included

    at_lines = [(0, cluster[0].x, cluster[0].y, cluster[0].z, 0, absorber, tags[0])]
    ipot_map = {}
    next_ipot = 0
    for i, site in enumerate(cluster[1:]):
        sym = site.species_string
        if sym == 'H' and not with_h:
            continue
        if sym in ipot_map:
            ipot = ipot_map[sym]
        else:
            next_ipot += 1
            ipot_map[sym] = ipot = next_ipot

        dist = cluster.get_distance(0, i+1)
        at_lines.append((dist, site.x, site.y, site.z, ipot, sym, tags[i+1]))


    ipot, z = 0, absorber_z
    out_text.append(f'   {ipot:4d}  {z:4d}   {absorber:s}')
    for sym, ipot in ipot_map.items():
        z = atomic_number(sym)
        out_text.append(f'   {ipot:4d}  {z:4d}   {sym:s}')

    out_text.append('')
    out_text.append('ATOMS')
    out_text.append(f'*    x         y         z       ipot  tag   distance  site_info')

    acount = 0
    for dist, x, y, z, ipot, sym, tag in sorted(at_lines, key=lambda x: x[0]):
        acount += 1
        if acount > 500:
            break
        sym = (sym + ' ')[:2]
        out_text.append(f'   {x: .5f}  {y: .5f}  {z: .5f} {ipot:4d}   {sym:s}    {dist:.5f}  * {tag:s}')

    out_text.append('')
    out_text.append('* END')
    out_text.append('')
    return strict_ascii('\n'.join(out_text))
