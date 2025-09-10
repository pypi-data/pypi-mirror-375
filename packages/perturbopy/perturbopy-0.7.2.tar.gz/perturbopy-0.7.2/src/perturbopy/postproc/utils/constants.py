"""
This is a module for working with constants, including storing values for different units and finding conversion factors.

"""

prefix_exps_dict = {'y': -24, 'z': -21, 'a': -18, 'f': -15,
                    'p': -12, 'n': -9, 'mu': -6, 'm': -3,
                    'c': -2, 'd': -1, 'da': 1, 'h': 2,
                    'k': 3, 'M': 6, 'G': 9, 'T': 12,
                    'P': 15, 'E': 18, 'Z': 21, 'Y': 24}

energy_units_names = {'eV': ['ev', 'electron-volt', 'electronvolt', 'electronvolts', 'electron-volts'],
                      'Ha': ['ha', 'hartree', 'eh', 'e_h', 'hartrees'],
                      'J': ['j', 'joule', 'joules'],
                      'Ry': ['ry', 'rydberg', 'rydbergs']}

energy_units_vals = {'eV': (2.7211396132, 1), 'Ha': (1, 0), 'J': (4.359748199, -18), 'Ry': (2.0, 0)}

length_units_names = {'bohr': ['bohr', 'a.u', 'atomic units', 'au'], 'angstrom': ['angstrom, a'], 'm': ['m', 'meter']}

length_units_vals = {'bohr': (1, 0), 'angstrom': (0.529177249, 0), 'm': (5.29177249, -11)}

recip_points_units_names = {'cartesian': ['tpiba', 'cartesian', 'cart'], 'crystal': ['crystal', 'cryst', 'frac', 'fractional']}


def prefix_exp(prefix):
    """"
    Finds the exponent corresponding to a prefix.
    For example, the prefix 'c' (centi) corresponds to 1e-2, so the exponent returned would be -2.

    Parameters
    ----------
    prefix : str
        The 1-2 letter case-sensitive prefix.

    Returns
    -------
    exponent : int
        The exponent corresponding to the prefix.

    Raises
    ------
    ValueError
        If `prefix` is not in prefix_exps_dict.keys(). These are:
            ['y', 'z', 'a', 'f', 'p', 'n', 'mu', 'm', 'c', 'd',
             'da', 'h', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']

    Examples
    --------
    >>> prefix_exp('c')
    -2
    >>> prefix_exp('mu')
    -6
    >>> prefix_exp(k)
    3

    """

    if prefix == '':
        return 0
    else:
        if prefix not in prefix_exps_dict.keys():
            raise ValueError(f"Please choose prefixes from the following list: {list(prefix_exps_dict.keys())}")

        return prefix_exps_dict[prefix]


def find_prefix_and_base_units(user_input_units, units_dict):
    """
    Dissects units to a prefix and base units, both with standardized names as specified by units_dict.
    For example, for the units 'meV', the prefix is 'm' and the base units are 'eV'.

    Parameters
    ----------
    user_input_units : str
        The units to be analyzed for its prefix and base.

    units_dict : dict
        A dictionary specifying the standard unit name corresponding to a set of possible units names (case-insensitive).

        For example, several possible variations of the unit hatree include Ha, hartree, etc. If Ha is
        chosen as the standard name, then the dictionary entry will be:
        {'Ha': ['ha', 'hartree', 'eh', 'e_h', 'hartrees']}

        Adding the unit Joule to the dict, and setting its standard name to 'J':
        {'Ha': ['ha', 'hartree', 'eh', 'e_h', 'hartrees'], 'J': ['j', 'joule', 'joules']}

    Returns
    -------
    prefix : str
        The standardized prefix.

    standard_units_name : str
        The standardized base unit name.

    Raises
    ------
    ValueError
        If the user_input_units, after removing any prefixes, is not in the keys or values of the units_dict.

    Examples
    --------
    >>> find_prefix_and_base_units('nm', {'m':['m', 'meter']})
    ('n', 'm')
    >>> find_prefix_and_base_units('nmeter', {'m':['m', 'meter']})
    ('n', 'm')
    >>> find_prefix_and_base_units('meter', {'m':['m', 'meter']})
    ('', 'm')
    >>> find_prefix_and_base_units('cm', {'m':['m', 'meter']}, 'bohr': ['bohr', 'a.u'])
    ('c', 'm')
    >>> find_prefix_and_base_units('a.u.', {'m':['m', 'meter']}, 'bohr': ['bohr', 'a.u.'])
    ('', 'bohr')


    """

    user_input_units = user_input_units.replace(' ', '').replace('-', '')

    # only case where prefix may get confused
    if user_input_units == 'mm':
        return 'm', 'm'

    for units_name in units_dict.keys():
        for name_variation in units_dict[units_name]:
            if name_variation in user_input_units.lower():
                user_input_units_split = user_input_units.lower().split(name_variation)

                if len(user_input_units_split) == 2 and user_input_units_split[1] == '':

                    prefix = user_input_units[:len(user_input_units_split[0])]
                    standard_units_name = units_name

                    return prefix, standard_units_name

    raise ValueError(f"Please choose units from the following list: {list(units_dict.keys())}")


def standardize_units_name(user_input_units, units_dict):
    """
    Converts any units to their standard name as specified in units_dict. Uses find_prefix_and_base_units to convert
    user_input_units to a prefix and standardized base units, then combines them into one string.

    Parameters
    ----------
    user_input_units : str
        The units to be standardized

    units_dict : dict
        A dictionary specifying the standard unit name corresponding to a set of possible units names (case-insensitive).
        See prefix_and_base_units for details.

    Returns
    -------
    standard_units : str
       The standardized units name.

    Examples
    --------
    >>> find_prefix_and_base_units('nm', {'m':['m', 'meter']})
    'nm'
    >>> find_prefix_and_base_units('nmeter', {'m':['m', 'meter']})
    'nm'
    >>> find_prefix_and_base_units('a.u.', {'m':['m', 'meter']}, 'bohr': ['bohr', 'a.u.'])
    'bohr'

    """
    prefix, units = find_prefix_and_base_units(user_input_units, units_dict)

    return prefix + units


def conversion_factor(init_units, final_units, units_names, units_vals):
    """
    Finds the conversion factor between two units.

    Parameters
    ----------
    init_units : str
        The initial units in the conversion.

    final_units : str
        The final units in the conversion.

    units_names : dict
        A dictionary specifying the standard unit name corresponding to a set of possible units names (case-insensitive).
        See prefix_and_base_units for details.

    units_vals : dict
        A dictionary specifying the conversion factors between different units, with units labeled by their standard name as
        specified in units_names. Values are represented as tuples (base, exponent).

        Example: For energies, possible units include hartrees and electron-volts.' Setting one value (hartree = 1), the remaining values
                 are the conversion factors between different units and hartrees.

                 energy_units_vals = {'eV': (2.7211396132, 1), 'Ha': (1, 0),'Ry': (0.5, 0)}

    Returns
    -------
    conversion_factor : float
       The conversion factor to convert from init_units to final_units.

    Raises
    ------
    ValueError
        If the base units of `init_units` or `final_units` are not in the keys of `units_vals`

    Examples
    --------
        >>> conversion_factor('fm', 'cm', {m': ['m', 'meter']},
                                          {'m': (5.29177249, -11)})
        1e-13
        >>> conversion_factor('a.u', 'bohr', {'bohr': ['bohr', 'a.u'], 'angstrom': ['angstrom, a']},
                                             {'bohr': (1, 0), 'angstrom': (0.529177249, 0)})
        1.0
        >>> conversion_factor('a.u', 'angstrom', {'bohr': ['bohr', 'a.u'], 'angstrom': ['angstrom, a']},
                                                 {'bohr': (1, 0), 'angstrom': (0.529177249, 0)})
        0.529177249

    """

    init_prefix, init_units = find_prefix_and_base_units(init_units, units_names)
    final_prefix, final_units = find_prefix_and_base_units(final_units, units_names)

    if init_units not in units_vals.keys() or final_units not in units_vals.keys():
        raise ValueError(f"Base units {init_units}, {final_units} are not in the units_vals dictionary: {list(units_vals.keys())}")

    init_val = units_vals[init_units]
    final_val = units_vals[final_units]

    conversion_factor = (final_val[0] / init_val[0],
                         (final_val[1] - prefix_exp(final_prefix)) - (init_val[1] - prefix_exp(init_prefix)))

    return conversion_factor[0] * 10**(conversion_factor[1])


def energy_conversion_factor(init_units, final_units):
    """
    find the conversion factor between two energy units.

    Parameters
    ----------
    init_units : str
        The initial units in the conversion.

    final_units : str
        The final units in the conversion.

    Returns
    -------
    conversion_factor : float
        The conversion factor to convert from init_units to final_units.

    Examples
    --------
    >>> energy_conversion_factor('meV', 'Ha')
    3.674930882447527e-05
    >>> energy_conversion_factor('Ry', 'Ha')
    2.0

    """

    return conversion_factor(init_units, final_units, energy_units_names, energy_units_vals)


def length_conversion_factor(init_units, final_units):
    """
    find the conversion factor between two length units.

    Parameters
    ----------
    init_units : str
        The initial units in the conversion.

    final_units : str
        The final units in the conversion.

    Returns
    -------
    conversion_factor : float
        The conversion factor to convert from init_units to final_units.

    Examples
    --------
    >>> length_conversion_factor('a.u', 'bohr')
    1.0
    >>> length_conversion_factor('a.u', 'nm')
    5.29177249e-2

    """

    return conversion_factor(init_units, final_units, length_units_names, length_units_vals)


def hbar(units):
    """
    find the value of hbar for specific units.

    Parameters
    ----------
    units : str
       The units hbar should be returned in.

    Returns
    -------
    hbar : float
       The value of hbar in the specified units.

    Raises
    ------
    ValueError
        If `units` is not in the keys of `hbar_dict`

    """
    hbar_dict = {'ev*fs': (6.582119569, -1), 'ev*s': (6.582119569, -16), 'atomic': (1, 0), 'J*s': (1.054571817, -34)}

    if units not in hbar_dict.keys():
        raise ValueError(f"Please choose hbar units from the following list: {list(hbar_dict.keys())}")

    return hbar_dict[units][0] * (10 ** hbar_dict[units][1])
