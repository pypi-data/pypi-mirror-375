"""Smoke tests for plotting functions, simply check that they run without errors.

To see the plots created during testing, replace plt.close("all") with plt.show()
"""

import matplotlib.pyplot as plt
import pytest

import pymgcv.plot as gplt
from pymgcv.gam import BAM, GAM, AbstractGAM
from pymgcv.terms import L

from . import gam_test_cases as tc


def get_cases_1d_continuous(gam_type: type[AbstractGAM]):
    cases = [
        (tc.linear_gam, {}),
        (tc.smooth_1d_gam, {"residuals": True}),
        (tc.smooth_1d_by_numeric_gam, {}),
        (tc.smooth_1d_random_wiggly_curve_gam, {"level": "A"}),
        (tc.smooth_1d_by_categorical_gam, {"level": "A"}),
        (tc.linear_functional_smooth_1d_gam, {}),
    ]
    return {
        f"{gam_type.__name__} - {f.__name__}": (f(gam_type), kwargs)
        for f, kwargs in cases
    }


cases_1d_continuous = get_cases_1d_continuous(GAM) | get_cases_1d_continuous(BAM)


@pytest.mark.parametrize(
    ("test_case", "kwargs"),
    cases_1d_continuous.values(),
    ids=cases_1d_continuous.keys(),
)
def test_continuous_1d(test_case: tc.GAMTestCase, kwargs: dict):
    gam = test_case.gam_model.fit(test_case.data, **test_case.fit_kwargs)
    term = list(gam.predictors.values())[0][0]
    gplt.continuous_1d(**kwargs, gam=gam, term=term, data=test_case.data)
    plt.close("all")


def get_cases_2d_continuous(gam_type: type[AbstractGAM]):
    test_cases_1d_continuous = [
        (tc.smooth_2d_gam, {}),
        (tc.tensor_2d_gam, {}),
        (tc.tensor_2d_by_numeric_gam, {}),
        (tc.tensor_2d_by_categorical_gam, {"level": "A"}),
        (tc.tensor_2d_random_wiggly_curve_gam, {"level": "A"}),
        (tc.linear_functional_tensor_2d_gam, {}),
    ]
    return {
        f"{gam_type.__name__} - {f.__name__}": (f(gam_type), kwargs)
        for f, kwargs in test_cases_1d_continuous
    }


cases_2d_continuous = get_cases_2d_continuous(GAM) | get_cases_2d_continuous(BAM)


@pytest.mark.parametrize(
    ("test_case", "kwargs"),
    cases_2d_continuous.values(),
    ids=cases_2d_continuous.keys(),
)
def test_continuous_2d(test_case: tc.GAMTestCase, kwargs: dict):
    gam = test_case.gam_model.fit(test_case.data, **test_case.fit_kwargs)
    term = list(gam.predictors.values())[0][0]
    gplt.continuous_2d(**kwargs, gam=gam, term=term, data=test_case.data)
    plt.close("all")


@pytest.mark.parametrize(
    "gam_type",
    [GAM, BAM],
)
def test_categorical(gam_type: type[AbstractGAM]):
    test_case = tc.categorical_linear_gam(gam_type)
    gam = test_case.gam_model.fit(test_case.data, **test_case.fit_kwargs)
    term = list(gam.predictors.values())[0][0]
    assert isinstance(term, L)
    gplt.categorical(target="y", gam=gam, term=term, data=test_case.data)
    plt.close("all")


all_test_cases = (
    cases_1d_continuous
    | cases_2d_continuous
    | {"categorical_linear": (tc.categorical_linear_gam(GAM), {"target": "y"})}
)

all_gam_test_cases = tc.get_test_cases()


@pytest.mark.parametrize(
    "test_case",
    all_gam_test_cases.values(),
    ids=all_gam_test_cases.keys(),
)
def test_plot(test_case: tc.GAMTestCase):
    gam = test_case.gam_model.fit(test_case.data, **test_case.fit_kwargs)
    try:
        gplt.plot(gam=gam, ncols=1)  # scatter=True fails for mvn + gaulss
    except (ValueError, NotImplementedError) as e:
        if "plot any" in str(e):
            pass
        else:
            raise
    plt.close("all")


@pytest.mark.parametrize(
    "test_case",
    all_gam_test_cases.values(),
    ids=all_gam_test_cases.keys(),
)
def test_qq(test_case: tc.GAMTestCase):
    gam = test_case.gam_model.fit(test_case.data, **test_case.fit_kwargs)
    try:
        gplt.qq(gam=gam)
    except NotImplementedError as e:
        accept_strs = [
            "Multivariate response",  # e.g. mvn and gaulss
            "Sample function not available",  # Quasi families
        ]
        if any(s in str(e) for s in accept_strs):
            pass
        else:
            raise

    except TypeError as e:
        if "Family must support CDF method" in str(e):
            pass
        else:
            raise
    plt.close("all")


@pytest.mark.parametrize(
    "test_case",
    all_gam_test_cases.values(),
    ids=all_gam_test_cases.keys(),
)
def test_residuals_vs_linear_predictor(test_case: tc.GAMTestCase):
    gam = test_case.gam_model.fit(test_case.data, **test_case.fit_kwargs)
    target = list(gam.predictors.keys())[0]
    try:
        gplt.residuals_vs_linear_predictor(gam, target=target)
    except NotImplementedError as e:
        if "Multivariate response" in str(e):  # e.g. mvn and gaulss
            print(gam.family.__class__.__name__)
            pass
        else:
            raise

    plt.close("all")
