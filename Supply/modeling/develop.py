from modeling.filters import filter_product_type, filter_by_vacancy, \
    filter_by_profitability
import logging

from modeling.dataframe_updates import update_mgra
import utils.config as config
from utils.constants import MGRA, \
    AVERAGE_UNIT_SQFT_POSTFIX, \
    AVERAGE_LAND_USAGE_PER_UNIT_POSTFIX, UNITS_PER_YEAR_POSTFIX, \
    OFFICE, COMMERCIAL, INDUSTRIAL, SINGLE_FAMILY, MULTI_FAMILY, \
    ProductTypeLabels


def parameters_for_product_type(product_type):
    return config.parameters[product_type + UNITS_PER_YEAR_POSTFIX], \
        config.parameters[product_type + AVERAGE_UNIT_SQFT_POSTFIX], \
        config.parameters[product_type +
                          AVERAGE_LAND_USAGE_PER_UNIT_POSTFIX]


def buildable_units(mgra, product_type_labels,
                    area_per_unit, max_units, vacancy_caps):
    # determine max units to build
    vacancy_cap = vacancy_caps.loc[mgra.index].values.item()

    # TODO: also use profitability filter value for this mgra
    # to determine the number of profitable units to build.

    # TODO: use capacity values for residential
    if product_type_labels.is_residential():
        pass

    # only build up to 95% of the vacant space
    available_units_by_land = mgra[
        product_type_labels.vacant_acres].values.item() * \
        0.95 // area_per_unit

    # this is a sanity check, no development should be larger than this number
    largest_development = config.parameters['largest_development_size']
    return int(min(max_units, largest_development,
                   vacancy_cap, available_units_by_land))


def normalize(dataframe):
    # also works with pandas Series
    return (dataframe - dataframe.min()) / (dataframe.max() - dataframe.min())


def develop_product_type(mgras, product_type_labels, progress):
    if progress is not None:
        progress.set_description('developing {}'.format(
            product_type_labels.product_type))

    new_units_to_build, square_feet_per_unit, acreage_per_unit = \
        parameters_for_product_type(product_type_labels.product_type)

    built_units = 0
    while built_units < new_units_to_build:
        max_units = new_units_to_build - built_units

        # Filter
        # filter for MGRA's that have vacant land available for more units
        filtered = filter_product_type(
            mgras, product_type_labels.vacant_acres, acreage_per_unit)
        available_count = len(filtered)

        filtered, vacancy_caps = filter_by_vacancy(
            filtered, product_type_labels)
        non_vacant_count = len(filtered)

        filtered, vacancy_caps, profits = filter_by_profitability(
            filtered, product_type_labels, vacancy_caps)
        profitable_count = len(filtered)

        logging.debug(
            'filtered to {} profitable / {} non-vacant / {}'.format(
                profitable_count, non_vacant_count, available_count
            ) + ' MGRA\'s with space available')

        if len(filtered) < 1:
            print('out of usable mgras for product type {}'.format(
                product_type_labels.product_type))
            print('evaluate filtering methods\nexiting')
            return None, progress

        # Sample
        # vacancy_weights = normalize(vacancy_caps)
        # profit_weights = normalize(profits)
        selected_row = filtered.sample(n=1, weights=vacancy_caps)
        selected_ID = selected_row[MGRA].iloc[0]

        buildable_count = buildable_units(
            selected_row, product_type_labels,
            acreage_per_unit, max_units, vacancy_caps
        )
        built_units += buildable_count

        logging.debug('building {} {} units on MGRA #{}'.format(
            buildable_count, product_type_labels.product_type, selected_ID))

        # develop buildable_count units by updating the MGRA in the dataframe
        mgras = update_mgra(mgras, selected_ID, square_feet_per_unit,
                            acreage_per_unit, buildable_count,
                            product_type_labels)

    if progress is not None:
        progress.update()
    return mgras, progress


def develop(mgras, progress=None):
    """
    Arguments
        mgras:
            A pandas dataframe of mgra's that will be updated with new values
            based on demand inputs found in parameters.yaml
    Returns:
        a pandas dataframe with selected MGRA's updated
    """
    product_types = [SINGLE_FAMILY, MULTI_FAMILY,
                     COMMERCIAL, OFFICE, INDUSTRIAL]
    for product_type in product_types:
        product_type_labels = ProductTypeLabels(product_type)
        mgras, progress = develop_product_type(
            mgras, product_type_labels, progress)
        if mgras is None:
            return mgras, progress

    # tests don't use a progress bar
    if progress is not None:
        return mgras, progress
    else:
        return mgras